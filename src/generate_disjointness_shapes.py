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
This script is provided for assistance with initially generating SHACL shapes to review OWL-disjointedness.  It generates shapes specialized to each pair of disjoint classes, by consuming owl:disjointWith and owl:AllDisjointClasses statements.

This script generates results into a standalone graph file, which is then expected to be folded into a shapes file, or used to start a shapes file.

This script is not expected to run more than once.  Most content will generate deterministically, but blank nodes will also be generated and will cause additional, redundant shapes if folded in by another script.
"""

__version__ = "0.1.0"

import argparse
import logging
import warnings
from typing import Dict, Set, Tuple

from rdflib import RDF, RDFS, SH, BNode, Graph, Literal, Namespace, URIRef
from rdflib.query import ResultRow

NS_RDF = RDF
NS_RDFS = RDFS

# This addresses a curious bug with type review and attempting to
# reference the 'sh:class' and 'sh:not' concepts.  (Because they are
# Python keywords, the dictionary style needs to be used.  But then
# something goes awry in type review.)
NS_SH = Namespace(str(SH))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--namespace-iri",
        default="http://example.org/shapes/example/",
        help="The namespace IRI to use for the generated shapes.",
    )
    parser.add_argument(
        "--namespace-prefix",
        default="sh-ex",
        help="The namespace prefix to use for the generated shapes.",
    )
    parser.add_argument(
        "--exclude-label-language",
        action="append",
        help="Implies --use-rdfs-label.  Can be passed multiple times.  Excludes a language tag.  To require a language tag, give 'None'.",
    )
    parser.add_argument(
        "--include-label-language",
        action="append",
        help="Implies --use-rdfs-label.  Can be passed multiple times.  Adds an extra language tag.  By default, 'en' is included.",
    )
    parser.add_argument(
        "--trim-prefixes",
        action="store_true",
        help="The generated suffix for the shape will, by default, include the concept prefix for classes, e.g. 'uco-action:Action' would yield 'uco-action-Action' in the shape's suffix.  With this flag, the prefix would be dropped, e.g. 'uco-action:Action' would yield 'Action' instead.",
    )
    parser.add_argument(
        "--use-rdfs-label",
        action="store_true",
        help="Include rdfs:label value in generated SHACL message.  Note: At this time, labels with no language tag or tagged as English ('en') are included.  To control the set of label language labels, use --include-label-language and --exclude-label-language.",
    )
    parser.add_argument("out_graph")
    parser.add_argument("in_graph", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    ns_shapes = Namespace(args.namespace_iri)

    # This might be toggled on in the next few code blocks.
    use_rdfs_label: bool = args.use_rdfs_label

    require_language_tags: bool = False
    language_tags: Set[str] = {"en"}
    excluded_language_tags: Set[str] = set()
    if args.exclude_label_language:
        use_rdfs_label = True
        for label_language in args.exclude_label_language:
            if label_language == "None":
                require_language_tags = True
            else:
                excluded_language_tags.add(label_language)
    if args.include_label_language:
        use_rdfs_label = True
        for label_language in args.include_label_language:
            language_tags.add(label_language)
    language_tags -= excluded_language_tags

    in_graph = Graph()
    out_graph = Graph()

    for _in_graph_filename in args.in_graph:
        in_graph.parse(_in_graph_filename)

    # Bind namespaces in output graph.
    out_graph.bind(args.namespace_prefix, ns_shapes)
    for prefix, n_namespace in in_graph.namespace_manager.namespaces():
        out_graph.bind(prefix, n_namespace)

    query = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?nClass ?nDisjointClass
WHERE {
  {
    ?nDisjointClass owl:disjointWith ?nClass .
  }
  UNION
  {
    ?nDisjointedness
      a owl:AllDisjointClasses ;
      owl:members/rdf:rest*/rdf:first ?nClass ;
      owl:members/rdf:rest+/rdf:first ?nDisjointClass ;
      .
    FILTER ( ?nClass != ?nDisjointClass )
  }
}
"""

    n_classes_with_any_disjointedness: Set[URIRef] = set()
    pairs: Set[Tuple[URIRef, URIRef]] = set()
    for result in in_graph.query(query):
        assert isinstance(result, ResultRow)
        if not isinstance(result[0], URIRef):
            continue
        if not isinstance(result[1], URIRef):
            continue
        n_classes_with_any_disjointedness.add(result[0])
        n_classes_with_any_disjointedness.add(result[1])
        n_classes_sorted = sorted([result[0], result[1]])
        pairs.add((n_classes_sorted[0], n_classes_sorted[1]))
    logging.debug(
        "len(n_classes_with_any_disjointedness) = %d.",
        len(n_classes_with_any_disjointedness),
    )
    logging.debug("len(pairs) = %d.", len(pairs))

    logging.debug("language_tags = %r.", language_tags)
    logging.debug("require_language_tags = %r.", require_language_tags)
    logging.debug("use_rdfs_label = %r.", use_rdfs_label)

    n_class_to_labels: Dict[URIRef, Set[str]] = dict()
    if use_rdfs_label:
        for n_class in n_classes_with_any_disjointedness:
            # logging.debug("n_class = %r.", n_class)
            for l_object in in_graph.objects(n_class, NS_RDFS.label):
                # logging.debug("l_object = %r.", l_object)
                assert isinstance(l_object, Literal)
                if l_object.language is None:
                    if require_language_tags:
                        logging.debug("Skipping %r for no language tag.", l_object)
                        continue
                elif l_object.language not in language_tags:
                    logging.debug(
                        "Skipping %r for non-requested language tag.", l_object
                    )
                    continue
                if n_class not in n_class_to_labels:
                    n_class_to_labels[n_class] = set()
                n_class_to_labels[n_class].add(str(l_object))
    n_class_to_label: Dict[URIRef, str] = dict()
    for n_class in n_class_to_labels:
        n_class_to_label[n_class] = "(%s)" % (
            ", ".join(sorted(n_class_to_labels[n_class]))
        )
    logging.debug("len(n_class_to_labels) = %d.", len(n_class_to_labels))
    logging.debug("len(n_class_to_label) = %d.", len(n_class_to_label))

    for pair in pairs:
        n_class_1: URIRef = pair[0]
        n_class_2: URIRef = pair[1]

        class_qname_1 = in_graph.namespace_manager.qname(n_class_1)
        class_qname_2 = in_graph.namespace_manager.qname(n_class_2)

        any_non_compacted = False
        for class_qname in [class_qname_1, class_qname_2]:
            if ":" not in class_qname:
                warnings.warn(
                    "Skipping shape generation, because IRI did not compact: %s."
                    % class_qname
                )
                any_non_compacted = True
                break
        if any_non_compacted:
            continue

        if args.trim_prefixes:
            class_reference_1 = ":".join(class_qname_1.split(":")[1:])
            class_reference_2 = ":".join(class_qname_2.split(":")[1:])
        else:
            class_reference_1 = class_qname_1.replace(":", "-")
            class_reference_2 = class_qname_2.replace(":", "-")

        class_message_part_1 = class_qname_1
        if n_class_1 in n_class_to_label:
            class_message_part_1 += " " + n_class_to_label[n_class_1]

        class_message_part_2 = class_qname_2
        if n_class_2 in n_class_to_label:
            class_message_part_2 += " " + n_class_to_label[n_class_2]

        disjointedness_shape_suffix = "%s-disjointWith-%s-shape" % (
            class_reference_1,
            class_reference_2,
        )
        n_disjointedness_shape = ns_shapes[disjointedness_shape_suffix]
        out_graph.add((n_disjointedness_shape, NS_RDF.type, NS_SH.NodeShape))
        out_graph.add(
            (
                n_disjointedness_shape,
                NS_SH.message,
                Literal(
                    "%s and %s are disjoint classes."
                    % (class_message_part_1, class_message_part_2),
                    lang="en",
                ),
            )
        )
        n_not_shape = BNode()
        out_graph.add((n_not_shape, NS_RDF.type, NS_SH.NodeShape))
        out_graph.add((n_not_shape, NS_SH["class"], n_class_2))
        out_graph.add((n_disjointedness_shape, NS_SH["not"], n_not_shape))
        out_graph.add((n_disjointedness_shape, NS_SH.targetClass, n_class_1))

    out_graph.serialize(args.out_graph)


if __name__ == "__main__":
    main()
