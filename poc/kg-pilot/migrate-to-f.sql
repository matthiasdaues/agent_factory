-- Brings a store loaded before stories E and F up to the current schema.sql without dropping data.
-- Run as the owner: psql ... -v ON_ERROR_STOP=1 -f migrate-to-f.sql. Safe to run twice.
-- Edges written before the gate are not checked again.
set search_path = kg, public;

insert into node_kind values ('topic'), ('name') on conflict do nothing;
insert into edge_type values ('names'), ('about') on conflict do nothing;
insert into edge_rule values
  ('names', 'name', 'topic'),
  ('quotes', 'name', 'span'),
  ('about', 'decision', 'topic')
on conflict do nothing;

-- Where a quote sits in a text: exact, whitespace (only whitespace differs), or missing.
create or replace function quote_found(quote text, body text) returns text language sql immutable parallel safe
return case
  when coalesce(quote, '') = '' then 'missing'
  when strpos(body, quote) > 0 then 'exact'
  when strpos(regexp_replace(btrim(body), '\s+', ' ', 'g'),
              regexp_replace(btrim(quote), '\s+', ' ', 'g')) > 0 then 'whitespace'
  else 'missing'
end;

-- Rule: a quotes edge needs its source's quote in the target span's text.
create or replace function check_quote() returns trigger language plpgsql as $$
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
create or replace trigger edge_quote before insert on edge for each row when (new.type = 'quotes')
  execute function check_quote();

-- Topic route: the topics whose names occur in the question, and their decisions.
-- A name matches when word_similarity with some part of the question reaches the threshold.
create or replace function topic_route(question text, threshold float8 default 0.8)
returns table (topic_id bigint, name text, similarity float8, decision_id bigint, span_id bigint, status text)
language sql stable as $$
  with names as (
    select n.id, n.body, word_similarity(n.body, question) as s
    from node n where n.kind = 'name' and word_similarity(n.body, question) >= threshold
  ),
  topics as (
    select distinct on (e.target_id) e.target_id as topic_id, names.body, names.s
    from names join edge e on e.source_id = names.id and e.type = 'names' and e.valid_to is null
    order by e.target_id, names.s desc
  )
  select t.topic_id, t.body, t.s, a.source_id, q.target_id, a.status
  from topics t
  join edge a on a.target_id = t.topic_id and a.type = 'about' and a.valid_to is null
  left join edge q on q.source_id = a.source_id and q.type = 'quotes' and q.valid_to is null
  order by t.s desc, a.source_id
$$;

grant execute on all functions in schema kg to kg_app;
