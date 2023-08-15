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


import logging
from pathlib import Path
from typing import Optional, Set

from rdflib import SH, Graph, URIRef
from rdflib.query import ResultRow

NS_SH = SH

srcdir = Path(__file__).parent
top_srcdir = srcdir.parent


def test_exemplar_coverage() -> None:
    """
    This test confirms that for each review-subject class C and property
    P in this repository's shapes graph C (/P) is used in the exemplars
    graph.
    """
    exemplar_graph = Graph()
    shapes_graph = Graph()
    tbox_graph = Graph()
    combined_graph = Graph()

    for filepath in (top_srcdir / "shapes").iterdir():
        if filepath.name.startswith("."):
            # Skip quality control test artifacts.
            continue
        if filepath.name.endswith(".ttl"):
            logging.debug("Loading shapes graph %r.", filepath)
            shapes_graph.parse(filepath)
    logging.debug("len(shapes_graph) = %d.", len(shapes_graph))

    monolithic_filepath = srcdir / "monolithic.ttl"
    tbox_graph.parse(monolithic_filepath)

    exemplar_filepath = srcdir / "exemplars.ttl"
    logging.debug("Loading exemplars graph %r.", exemplar_filepath)
    exemplar_graph.parse(exemplar_filepath)
    logging.debug("len(exemplar_graph) = %d.", len(exemplar_graph))

    combined_graph = exemplar_graph + tbox_graph

    properties_mapped: Set[URIRef] = set()
    properties_with_exemplars: Set[URIRef] = set()

    result: Optional[bool]

    for n_sh_predicate_with_predicate_object in {
        NS_SH.inversePath,
        NS_SH.path,
        NS_SH.targetObjectsOf,
        NS_SH.targetSubjectsOf,
        NS_SH.zeroOrMorePath,
    }:
        for n_object in shapes_graph.objects(
            None, n_sh_predicate_with_predicate_object
        ):
            if isinstance(n_object, URIRef):
                properties_mapped.add(n_object)
    for alternative_path_result in shapes_graph.query(
        """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sh: <http://www.w3.org/ns/shacl#>
SELECT ?nPredicate
WHERE {
  ?nShThing sh:alternativePath ?nAlternativePathList .
  ?nAlternativePathList rdf:rest*/rdf:first ?nPredicate .
  FILTER isURI(?nPredicate)
}
"""
    ):
        assert isinstance(alternative_path_result, ResultRow)
        assert isinstance(alternative_path_result[0], URIRef)
        properties_mapped.add(alternative_path_result[0])

    property_query = """\
ASK {
  ?nIndividual1 ?nUsedProperty ?nIndividual2 .
  ?nUsedProperty rdfs:subPropertyOf* ?nProperty .
}
"""
    for property_mapped in sorted(properties_mapped):
        result = None
        for property_result in combined_graph.query(
            property_query, initBindings={"nProperty": property_mapped}
        ):
            assert isinstance(property_result, bool)
            result = property_result
        if result is True:
            properties_with_exemplars.add(property_mapped)

    try:
        assert properties_mapped <= properties_with_exemplars
    except AssertionError:
        logging.info("These mapped properties have no exemplar instances:")
        undemonstrated_properties = properties_mapped - properties_with_exemplars
        for undemonstrated_property in sorted(undemonstrated_properties):
            logging.info("* %s", str(undemonstrated_property))
        raise

    classes_mapped: Set[URIRef] = set()
    classes_with_exemplars: Set[URIRef] = set()

    for n_object in shapes_graph.objects(None, NS_SH.targetClass):
        assert isinstance(n_object, URIRef)
        classes_mapped.add(n_object)

    class_query = """\
ASK {
  ?nIndividual a/rdfs:subClassOf* ?nClass .
}
"""
    for class_mapped in sorted(classes_mapped):
        result = None
        for class_result in combined_graph.query(
            class_query, initBindings={"nClass": class_mapped}
        ):
            assert isinstance(class_result, bool)
            result = class_result
        if result is True:
            classes_with_exemplars.add(class_mapped)
        else:
            logging.debug("class_mapped = %r.", class_mapped)
            logging.debug("result = %r.", result)

    try:
        assert classes_mapped <= classes_with_exemplars
    except AssertionError:
        logging.info("These mapped classes have no exemplar instances:")
        undemonstrated_classes = classes_mapped - classes_with_exemplars
        for undemonstrated_class in sorted(undemonstrated_classes):
            logging.info("* %s", str(undemonstrated_class))
        raise
