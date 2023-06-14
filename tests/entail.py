#!/usr/bin/env python3

# Portions of this file contributed by NIST are governed by the following
# statement:
#
# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

"""
This script implements a restricted set of RDFS entailment patterns, sourced from here:

https://www.w3.org/TR/rdf11-mt/#patterns-of-rdfs-entailment-informative

The implementation is a subset of the 13 patterns, as well as restricting the entailments to only IRI-identified nodes.
"""

__version__ = "0.1.0"

import argparse
from typing import Dict

from rdflib import Graph, URIRef


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_graph")
    parser.add_argument("in_graph", nargs="+")
    args = parser.parse_args()

    out_graph = Graph()
    in_graph = Graph()

    for _in_graph_file in args.in_graph:
        in_graph.parse(_in_graph_file)

    in_and_out_graph = Graph()
    in_and_out_graph += in_graph

    pattern_to_construct_query: Dict[str, str] = {
        "rdfs2": """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?yyy rdf:type ?xxx .
}
WHERE {
  ?aaa rdfs:domain ?xxx .
  ?yyy ?aaa ?zzz .
  FILTER isIRI(?aaa)
  FILTER isIRI(?xxx)
  FILTER isIRI(?yyy)
  FILTER isIRI(?zzz)
}
""",
        "rdfs3": """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?zzz rdf:type ?xxx .
}
WHERE {
  ?aaa rdfs:range ?xxx .
  ?yyy ?aaa ?zzz .
  FILTER isIRI(?aaa)
  FILTER isIRI(?xxx)
  FILTER isIRI(?yyy)
  FILTER isIRI(?zzz)
}
""",
        "rdfs5": """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?xxx rdfs:subPropertyOf ?zzz .
}
WHERE {
  ?xxx rdfs:subPropertyOf ?yyy .
  ?yyy rdfs:subPropertyOf ?zzz .
  FILTER isIRI(?xxx)
  FILTER isIRI(?yyy)
  FILTER isIRI(?zzz)
}
""",
        "rdfs7": """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?xxx ?bbb ?yyy .
}
WHERE {
  ?aaa rdfs:subPropertyOf ?bbb .
  ?xxx ?aaa ?yyy .
  FILTER isIRI(?aaa)
  FILTER isIRI(?bbb)
  FILTER isIRI(?xxx)
  FILTER isIRI(?yyy)
}
""",
        "rdfs9": """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?zzz rdf:type ?yyy .
}
WHERE {
  ?xxx rdfs:subClassOf ?yyy .
  ?zzz rdf:type ?xxx .
  FILTER isIRI(?xxx)
  FILTER isIRI(?yyy)
  FILTER isIRI(?zzz)
}
""",
        "rdfs11": """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?xxx rdfs:subClassOf ?zzz .
}
WHERE {
  ?xxx rdfs:subClassOf ?yyy .
  ?yyy rdfs:subClassOf ?zzz .
  FILTER isIRI(?xxx)
  FILTER isIRI(?yyy)
  FILTER isIRI(?zzz)
}
""",
    }

    tmp_graph: Graph
    while True:
        tmp_graph = Graph()
        for pattern in pattern_to_construct_query:
            construct_query = pattern_to_construct_query[pattern]
            for construct_result in in_and_out_graph.query(construct_query):
                assert isinstance(construct_result, tuple)
                assert isinstance(construct_result[0], URIRef)
                assert isinstance(construct_result[1], URIRef)
                assert isinstance(construct_result[2], URIRef)
                tmp_graph.add(
                    (construct_result[0], construct_result[1], construct_result[2])
                )
        if len(tmp_graph - in_and_out_graph) == 0:
            break
        for triple in tmp_graph.triples((None, None, None)):
            in_and_out_graph.add(triple)
            out_graph.add(triple)

    out_graph.serialize(args.out_graph)


if __name__ == "__main__":
    main()
