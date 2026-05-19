from __future__ import annotations

import json

from catalyst_q_benchmarks.official_corpora import canonical_dimacs_cnf, parse_dimacs_cnf, parse_orlib_mknap


def test_parse_dimacs_cnf_handles_multiline_clauses_and_comments():
    text = """
c uf20 style fixture
p cnf 3 2
1 -2
3 0
-1 2 0
%
"""

    variables, clauses = parse_dimacs_cnf(text)

    assert variables == 3
    assert clauses == [[1, -2, 3], [-1, 2]]


def test_parse_dimacs_cnf_infers_variable_count_without_header():
    variables, clauses = parse_dimacs_cnf("1 -4 0\n2 3 0\n")

    assert variables == 4
    assert clauses == [[1, -4], [2, 3]]


def test_dimacs_fixture_is_json_serializable_for_raw_records():
    variables, clauses = parse_dimacs_cnf("p cnf 2 1\n1 -2 0\n")

    payload = {"variables": variables, "clauses": clauses}

    assert json.loads(json.dumps(payload)) == {"variables": 2, "clauses": [[1, -2]]}


def test_canonical_dimacs_cnf_strips_satlib_trailers():
    original = "p cnf 2 1\n1 -2 0\n%\n0\n"
    variables, clauses = parse_dimacs_cnf(original)

    canonical = canonical_dimacs_cnf(variables, clauses)

    assert canonical == "p cnf 2 1\n1 -2 0\n"


def test_parse_orlib_mknap_reads_multidimensional_knapsack_fixture():
    text = """
1
3 2 13
4 5 9
2 3 4
4 2 5
5 7
"""

    instances = parse_orlib_mknap(text, source_url="https://example.test/mknap1.txt")

    assert len(instances) == 1
    instance = instances[0]
    assert instance["instance_id"] == "mknap1_01"
    assert instance["items"] == 3
    assert instance["constraints_count"] == 2
    assert instance["optimum"] == 13
    assert instance["values"] == [4, 5, 9]
    assert instance["constraints"] == [[2, 3, 4], [4, 2, 5]]
    assert instance["capacities"] == [5, 7]
