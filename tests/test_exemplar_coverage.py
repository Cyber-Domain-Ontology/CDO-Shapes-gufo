#!/usr/bin/env python3

# Portions of this file contributed by NIST are governed by the
# following statement:
#
# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to Title 17 Section 105 of the
# United States Code, this software is not subject to copyright
# protection within the United States. NIST assumes no responsibility
# whatsoever for its use by other parties, and makes no guarantees,
# expressed or implied, about its quality, reliability, or any other
# characteristic.
#
# We would appreciate acknowledgement if the software is used.

import logging
from pathlib import Path
from typing import Generator, Optional, Set

from rdflib import SH, BNode, Graph, URIRef
from rdflib.term import IdentifiedNode

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

    concepts_excused: Set[URIRef] = set()
    concepts_excused_filepath = srcdir / "concepts_excused.txt"
    logging.debug("Loading excused-concepts set %r.", concepts_excused_filepath)
    with concepts_excused_filepath.open("r") as concepts_excused_fh:
        for line in concepts_excused_fh:
            cleaned_line = line.strip()
            if cleaned_line == "":
                continue
            if cleaned_line.startswith("#"):
                continue
            concepts_excused.add(URIRef(cleaned_line))
    logging.debug("len(concepts_excused) = %d.", len(concepts_excused))

    properties_mapped: Set[URIRef] = set()
    properties_with_exemplars: Set[URIRef] = set()

    result: Optional[bool]

    for n_sh_predicate_with_predicate_object in {
        NS_SH.disjoint,
        NS_SH.equals,
        NS_SH.lessThan,
        NS_SH.lessThanOrEquals,
        NS_SH.targetObjectsOf,
        NS_SH.targetSubjectsOf,
    }:
        for n_object in shapes_graph.objects(
            None, n_sh_predicate_with_predicate_object
        ):
            if isinstance(n_object, URIRef):
                properties_mapped.add(n_object)
    for n_object in shapes_graph.objects(None, NS_SH.path):
        assert isinstance(n_object, IdentifiedNode)
        for n_property in properties_in_shacl_property_path(shapes_graph, n_object):
            properties_mapped.add(n_property)

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

    if properties_mapped > (properties_with_exemplars | concepts_excused):
        logging.info("These mapped properties have no exemplar instances:")
        undemonstrated_properties = (
            properties_mapped - properties_with_exemplars - concepts_excused
        )
        for undemonstrated_property in sorted(undemonstrated_properties):
            logging.info("* %s", str(undemonstrated_property))

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

    if classes_mapped > (classes_with_exemplars | concepts_excused):
        logging.info("These mapped classes have no exemplar instances:")
        undemonstrated_classes = (
            classes_mapped - classes_with_exemplars - concepts_excused
        )
        for undemonstrated_class in sorted(undemonstrated_classes):
            logging.info("* %s", str(undemonstrated_class))

    assert properties_mapped <= (
        properties_with_exemplars | concepts_excused
    ) and classes_mapped <= (classes_with_exemplars | concepts_excused)


def properties_in_shacl_property_path(
    graph: Graph, n_property_path: IdentifiedNode
) -> Generator[URIRef, None, None]:
    """
    https://www.w3.org/TR/shacl/#property-paths
    >>> import rdflib
    >>> graph_text = '''
    ... # Example graph built from: https://www.w3.org/TR/shacl/#property-paths
    ... PREFIX ex: <http://example.com/ns#>
    ... PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    ... PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    ... PREFIX sh: <http://www.w3.org/ns/shacl#>
    ... []
    ...     a sh:PropertyShape ;
    ...     sh:path ex:parent ;
    ...     .
    ... []
    ...     a sh:PropertyShape ;
    ...     sh:path [ sh:inversePath ex:parent ];
    ...     .
    ... []
    ...     a sh:PropertyShape ;
    ...     sh:path ( ex:parent ex:firstName );
    ...     .
    ... []
    ...     a sh:PropertyShape ;
    ...     sh:path ( rdf:type [ sh:zeroOrMorePath rdfs:subClassOf ] );
    ...     .
    ... []
    ...     a sh:PropertyShape ;
    ...     sh:path [ sh:alternativePath ( ex:father ex:mother ) ];
    ...     .
    ... '''
    >>> graph = rdflib.Graph()
    >>> _ = graph.parse(data=graph_text, format="turtle")
    >>> ns_ex = rdflib.Namespace("http://example.com/ns#")
    >>> n_properties_in_graph: set[rdflib.URIRef] = set()
    >>> for n_property_path in graph.objects(None, rdflib.SH.path):
    ...     for n_property in properties_in_shacl_property_path(graph, n_property_path):
    ...         n_properties_in_graph.add(n_property)
    >>> assert n_properties_in_graph == {
    ...     ns_ex["father"],
    ...     ns_ex["firstName"],
    ...     ns_ex["mother"],
    ...     ns_ex["parent"],
    ...     rdflib.RDF["type"],
    ...     rdflib.RDFS["subClassOf"],
    ... }
    """
    if isinstance(n_property_path, URIRef):
        yield n_property_path
    else:
        assert isinstance(n_property_path, BNode)
        for n_object in graph.objects(n_property_path, NS_SH.inversePath):
            assert isinstance(n_object, IdentifiedNode)
            yield from properties_in_shacl_property_path(graph, n_object)
        else:
            for n_object in graph.objects(n_property_path, NS_SH.zeroOrMorePath):
                assert isinstance(n_object, IdentifiedNode)
                yield from properties_in_shacl_property_path(graph, n_object)
            else:
                for n_object in graph.objects(n_property_path, NS_SH.oneOrMorePath):
                    assert isinstance(n_object, IdentifiedNode)
                    yield from properties_in_shacl_property_path(graph, n_object)
                else:
                    for n_object in graph.objects(n_property_path, NS_SH.zeroOrOnePath):
                        assert isinstance(n_object, IdentifiedNode)
                        yield from properties_in_shacl_property_path(graph, n_object)
                    else:
                        for n_object in graph.objects(
                            n_property_path, NS_SH.alternativePath
                        ):
                            assert isinstance(n_object, IdentifiedNode)
                            for n_alternative_path_member in graph.items(n_object):
                                assert isinstance(
                                    n_alternative_path_member, IdentifiedNode
                                )
                                yield from properties_in_shacl_property_path(
                                    graph, n_alternative_path_member
                                )
                        else:
                            for n_sequence_member in graph.items(n_property_path):
                                assert isinstance(n_sequence_member, IdentifiedNode)
                                yield from properties_in_shacl_property_path(
                                    graph, n_sequence_member
                                )
