"""Spike code for the data-model DSL PoC: validation-depth error cases.

Writes one model file per error case for DBML and LinkML. Each case changes
exactly one place in the valid acid slice; the script fails if a change does
not apply. A case that cannot arise in a language is listed as not applicable
in cases.tsv instead of being invented.

Usage: python3 make-cases.py   (run from poc/data_model_from_dsl/validation)
"""

import pathlib

HERE = pathlib.Path(__file__).parent
DBML = (HERE / "../dbml/acid-slice.dbml").read_text()
LINKML = (HERE / "../linkml/acid-slice.yaml").read_text()

CASES = [
    ("E01", "reference to a column that does not exist"),
    ("E02", "unique key on a column that does not exist"),
    ("E03", "composite reference with mismatched column counts"),
    ("E04", "foreign key whose column type differs from the target"),
    ("E05", "duplicate table"),
    ("E06", "duplicate column in one table"),
    ("E07", "column type that is not defined"),
    ("E08", "duplicate enum value"),
    ("E09", "primary key on a column that does not exist"),
    ("E10", "check or rule that names a column that does not exist"),
    ("E11", "two primary keys in one table"),
    ("E12", "group member that does not exist"),
]


def mutate(src: str, old: str, new: str) -> str:
    assert src.count(old) == 1, f"pattern not unique or missing: {old!r}"
    return src.replace(old, new)


dbml = {
    "E01": lambda s: mutate(s, "Ref plan_domain_fk: plan.domain_id > domain.domain_id",
                            "Ref plan_domain_fk: plan.domain_id > domain.domain_key"),
    "E02": lambda s: mutate(s, "(domain_id, odate) [unique", "(domain_id, odate_x) [unique"),
    "E03": lambda s: mutate(s, "task_version.(domain_id, task_id) > task.(domain_id, task_id)",
                            "task_version.(domain_id, task_id) > task.(task_id)"),
    "E04": lambda s: mutate(s, "Table task {\n  task_id bigint [not null]\n  domain_id bigint [not null]",
                            "Table task {\n  task_id bigint [not null]\n  domain_id varchar [not null]"),
    "E05": lambda s: s + "\nTable plan {\n  plan_id bigint [not null]\n}\n",
    "E06": lambda s: mutate(s, "  odate date [not null]\n", "  odate date [not null]\n  odate date [not null]\n"),
    "E07": lambda s: mutate(s, "  state plan_state [not null]", "  state plan_status [not null]"),
    "E08": lambda s: mutate(s, "Enum plan_state {\n  PENDING\n  OPEN\n  CLOSED\n}",
                            "Enum plan_state {\n  PENDING\n  OPEN\n  CLOSED\n  OPEN\n}"),
    "E09": lambda s: mutate(s, "plan_id [pk, name: 'plan_pkey']", "plan_key [pk, name: 'plan_pkey']"),
    "E10": lambda s: mutate(s, "`kind = 'SMART' OR state = 'ACTIVE'`", "`kind = 'SMART' OR status = 'ACTIVE'`"),
    "E11": lambda s: mutate(s, "plan_id [pk, name: 'plan_pkey']",
                            "plan_id [pk, name: 'plan_pkey']\n    odate [pk, name: 'plan_pkey2']"),
    "E12": lambda s: mutate(s, "TableGroup domain_owned {\n  task\n", "TableGroup domain_owned {\n  task\n  task_x\n"),
}

PLAN_ATTRS = "      plan_id: {identifier: true, range: integer}\n      domain_id: {required: true, range: Domain}\n      odate: {required: true, range: date}\n"
linkml = {
    "E01": None,  # references point to a class, not to a column
    "E02": lambda s: mutate(s, "uq_plan_domain_odate: {unique_key_slots: [domain_id, odate]}",
                            "uq_plan_domain_odate: {unique_key_slots: [domain_id, odate_x]}"),
    "E03": None,  # no composite references
    "E04": None,  # references point to a class, so the key type comes from it
    "E05": lambda s: mutate(s, "\nenums:\n", "\n  Plan:\n    attributes:\n      plan_id: {identifier: true, range: integer}\n\nenums:\n"),
    "E06": lambda s: mutate(s, PLAN_ATTRS, PLAN_ATTRS + "      odate: {required: true, range: date}\n"),
    "E07": lambda s: mutate(s, "      state: {required: true, range: PlanState}", "      state: {required: true, range: PlanStatus}"),
    "E08": lambda s: mutate(s, "PlanState: {permissible_values: {PENDING: {}, OPEN: {}, CLOSED: {}}}",
                            "PlanState: {permissible_values: {PENDING: {}, OPEN: {}, CLOSED: {}, OPEN: {}}}"),
    "E09": None,  # the identifier is a property of an existing slot
    "E10": lambda s: mutate(s, "            kind: {none_of: [{equals_string: SMART}]}",
                            "            kindx: {none_of: [{equals_string: SMART}]}"),
    "E11": lambda s: mutate(s, "      odate: {required: true, range: date}\n      state: {required: true, range: PlanState}",
                            "      odate: {identifier: true, range: date}\n      state: {required: true, range: PlanState}"),
    "E12": None,  # no group construct
}

out = HERE / "cases"
out.mkdir(exist_ok=True)
rows = ["case\tdescription\tdbml_file\tlinkml_file"]
for cid, desc in CASES:
    d = out / f"{cid}.dbml"
    d.write_text(dbml[cid](DBML))
    if linkml[cid] is None:
        lfile = "n/a"
    else:
        lf = out / f"{cid}.yaml"
        lf.write_text("# yamllint disable-file\n" + linkml[cid](LINKML))
        lfile = lf.name
    rows.append(f"{cid}\t{desc}\t{d.name}\t{lfile}")
(HERE / "cases.tsv").write_text("\n".join(rows) + "\n")
print("\n".join(rows))
