-- Knowledge graph pilot: the store of the design position.
-- Loads into an empty database as the owner. Safe to load twice.

create extension if not exists vector;
create extension if not exists pg_trgm;
create extension if not exists unaccent;

drop schema if exists kg cascade;
create schema kg;
set search_path = kg, public;

-- convert_to is stable, not immutable; with a fixed encoding this wrapper is immutable.
create function utf8_bytes(t text) returns bytea language sql immutable parallel safe
  return convert_to(t, 'UTF8');

-- Node kinds and the edge rules between them.
create table node_kind (kind text primary key);
insert into node_kind values
  ('source'), ('span'), ('problem'), ('conjecture'), ('criticism'), ('test'), ('decision');

create table edge_type (type text primary key);
create table edge_rule (
  type text not null references edge_type,
  source_kind text not null references node_kind,
  target_kind text not null references node_kind,
  primary key (type, source_kind, target_kind)
);
insert into edge_type values
  ('part_of'), ('replies_to'), ('quotes'), ('criticises'), ('rests_on'), ('similar_to'), ('written_in');
insert into edge_rule values
  ('part_of', 'span', 'source'),
  ('replies_to', 'span', 'span'),
  ('quotes', 'conjecture', 'span'),
  ('quotes', 'decision', 'span'),
  ('criticises', 'criticism', 'conjecture'),
  ('rests_on', 'decision', 'conjecture'),
  ('similar_to', 'span', 'span'),
  ('similar_to', 'conjecture', 'conjecture'),
  ('written_in', 'source', 'span');

-- Nodes. A claimed relation that can be criticised is a node of its own.
create table node (
  id bigint generated always as identity primary key,
  kind text not null references node_kind,
  lang text not null default 'english' check (lang in ('english', 'german')),
  body text not null,
  external_id text unique,
  anchor jsonb not null default '{}',
  content_hash bytea generated always as (sha256(kg.utf8_bytes(body))) stored,
  recorded_at timestamptz not null default now(),
  tsv tsvector generated always as (
    case lang
      when 'german' then to_tsvector('german'::regconfig, body)
      else to_tsvector('english'::regconfig, body)
    end
  ) stored
);
create index node_tsv on node using gin (tsv);
create index node_trgm on node using gin (body gin_trgm_ops);
create index node_hash on node (content_hash);

-- Edges. Append-only: a change ends the old row and writes a new one.
create table edge (
  id bigint generated always as identity primary key,
  source_id bigint not null references node,
  target_id bigint not null references node,
  type text not null references edge_type,
  status text not null check (status in ('candidate', 'confirmed')),
  asserted_by text not null,
  evidence_span_id bigint references node,
  valid_from timestamptz not null default now(),
  valid_to timestamptz,
  recorded_at timestamptz not null default now(),
  meta jsonb not null default '{}'
);
create index edge_out on edge (source_id, type) where valid_to is null;
create index edge_in on edge (target_id, type) where valid_to is null;

-- Vectors, one row per node, model, and model version.
create table embedding (
  node_id bigint not null references node,
  model text not null,
  model_version text not null,
  vector vector(384) not null,
  primary key (node_id, model, model_version)
);
create index embedding_hnsw on embedding using hnsw (vector vector_cosine_ops);

-- Outbox: the record of events; NOTIFY only wakes the reader.
create table outbox (
  id bigint generated always as identity primary key,
  node_id bigint not null references node,
  kind text not null,
  created_at timestamptz not null default now()
);
create table outbox_cursor (consumer text primary key, last_id bigint not null default 0);

-- Rule: an edge's ends must have the kinds its type allows.
create function check_edge_kinds() returns trigger language plpgsql as $$
begin
  if not exists (
    select 1 from edge_rule r
    join node s on s.id = new.source_id
    join node t on t.id = new.target_id
    where r.type = new.type and r.source_kind = s.kind and r.target_kind = t.kind
  ) then
    raise exception 'edge % from node % to node % breaks the kind rules', new.type, new.source_id, new.target_id;
  end if;
  return new;
end $$;
create trigger edge_kinds before insert on edge for each row execute function check_edge_kinds();

-- Where a quote sits in a text: exact, whitespace (only whitespace differs), or missing.
create function quote_found(quote text, body text) returns text language sql immutable parallel safe
return case
  when coalesce(quote, '') = '' then 'missing'
  when strpos(body, quote) > 0 then 'exact'
  when strpos(regexp_replace(btrim(body), '\s+', ' ', 'g'),
              regexp_replace(btrim(quote), '\s+', ' ', 'g')) > 0 then 'whitespace'
  else 'missing'
end;

-- Rule: a quotes edge needs its source's quote in the target span's text.
create function check_quote() returns trigger language plpgsql as $$
declare
  quote text;
  body text;
begin
  select s.anchor ->> 'quote', t.body into quote, body
  from node s, node t where s.id = new.source_id and t.id = new.target_id;
  if quote_found(quote, body) = 'missing' then
    raise exception 'quote of node % is not in span %', new.source_id, new.target_id
      using errcode = 'check_violation';
  end if;
  return new;
end $$;
create trigger edge_quote before insert on edge for each row when (new.type = 'quotes')
  execute function check_quote();

-- Rule: a node's kind may change only if every live edge still fits.
create function check_node_kind_change() returns trigger language plpgsql as $$
begin
  if new.kind is distinct from old.kind and exists (
    select 1 from edge e
    join node s on s.id = case when e.source_id = new.id then new.id else e.source_id end
    join node t on t.id = case when e.target_id = new.id then new.id else e.target_id end
    where e.valid_to is null and (e.source_id = new.id or e.target_id = new.id)
      and not exists (
        select 1 from edge_rule r
        where r.type = e.type
          and r.source_kind = case when e.source_id = new.id then new.kind else s.kind end
          and r.target_kind = case when e.target_id = new.id then new.kind else t.kind end
      )
  ) then
    raise exception 'changing node % to kind % breaks a live edge', new.id, new.kind;
  end if;
  if old.kind = 'decision' then
    raise exception 'decision % is append-only', old.id;
  end if;
  return new;
end $$;
create trigger node_kind_change before update on node for each row execute function check_node_kind_change();

-- Rule: decisions and edges are append-only. Only valid_to may be set once.
create function refuse_change() returns trigger language plpgsql as $$
begin
  if tg_op = 'TRUNCATE' then
    raise exception '% is append-only', tg_table_name;
  end if;
  if tg_table_name = 'node' then
    if (to_jsonb(old) ->> 'kind') = 'decision' then
      raise exception 'decision % is append-only', old.id;
    end if;
    return old;
  end if;
  if tg_table_name = 'edge' then
    if tg_op = 'DELETE' then
      raise exception 'edge % is append-only', old.id;
    end if;
    if old.valid_to is not null
       or (to_jsonb(new) - 'valid_to') is distinct from (to_jsonb(old) - 'valid_to') then
      raise exception 'edge % is append-only; only valid_to may be set once', old.id;
    end if;
  end if;
  return coalesce(new, old);
end $$;
create trigger edge_no_change before update or delete on edge for each row execute function refuse_change();
create trigger edge_no_truncate before truncate on edge for each statement execute function refuse_change();
create trigger node_no_delete before delete on node for each row execute function refuse_change();
create trigger node_no_truncate before truncate on node for each statement execute function refuse_change();

-- Events: a new conjecture or decision writes an outbox row and wakes listeners.
create function raise_event() returns trigger language plpgsql as $$
declare
  event_id bigint;
begin
  if new.kind in ('conjecture', 'decision') then
    insert into outbox (node_id, kind) values (new.id, new.kind) returning id into event_id;
    perform pg_notify('kg_events', event_id::text);
  end if;
  return new;
end $$;
create trigger node_event after insert on node for each row execute function raise_event();

-- Fused search: full-text and vector rankings merged by reciprocal rank fusion.
create function hybrid_search(
  query text, query_vector vector(384), config regconfig, k int default 10,
  keyword_weight float8 default 1, vector_weight float8 default 1, model_name text default 'stand-in'
) returns table (node_id bigint, score float8, keyword_rank bigint, vector_rank bigint)
language sql stable
set hnsw.iterative_scan = relaxed_order
as $$
  with keyword as (
    select n.id, row_number() over (order by ts_rank_cd(n.tsv, q) desc) as r
    from node n, websearch_to_tsquery(config, query) q
    where n.tsv @@ q
    order by ts_rank_cd(n.tsv, q) desc
    limit 50
  ),
  nearest as (
    select e.node_id as id, e.vector <=> query_vector as distance
    from embedding e
    where e.model = model_name
    order by e.vector <=> query_vector
    limit 50
  ),
  vec as (
    select id, row_number() over (order by distance) as r from nearest
  )
  select coalesce(keyword.id, vec.id),
         coalesce(keyword_weight / (60 + keyword.r), 0) + coalesce(vector_weight / (60 + vec.r), 0),
         keyword.r, vec.r
  from keyword full join vec on vec.id = keyword.id
  order by 2 desc
  limit k
$$;

-- Search, then follow live edges in both directions.
create function search_then_traverse(
  query text, query_vector vector(384), config regconfig, k int default 5, depth int default 1,
  model_name text default 'stand-in'
) returns table (seed_id bigint, node_id bigint, hops int, score float8)
language sql stable as $$
  with recursive seeds as (
    select h.node_id, h.score from hybrid_search(query, query_vector, config, k, 1, 1, model_name) h
  ),
  walk (seed_id, node_id, hops, score) as (
    select s.node_id, s.node_id, 0, s.score from seeds s
    union all
    select w.seed_id,
           case when e.source_id = w.node_id then e.target_id else e.source_id end,
           w.hops + 1, w.score
    from walk w
    join edge e on (e.source_id = w.node_id or e.target_id = w.node_id) and e.valid_to is null
    where w.hops < depth
  ) cycle node_id set is_cycle using path
  select distinct on (seed_id, node_id) seed_id, node_id, hops, score
  from walk where not is_cycle
  order by seed_id, node_id, hops
$$;

-- The application role: read and insert, never rewrite.
do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'kg_app') then
    create role kg_app login password 'app';
  end if;
end $$;
grant usage on schema kg to kg_app;
grant select, insert on all tables in schema kg to kg_app;
grant update (kind) on node to kg_app;
grant update (valid_to) on edge to kg_app;
grant update on outbox_cursor to kg_app;
grant usage on all sequences in schema kg to kg_app;
grant execute on all functions in schema kg to kg_app;
alter role kg_app set search_path = kg, public;
