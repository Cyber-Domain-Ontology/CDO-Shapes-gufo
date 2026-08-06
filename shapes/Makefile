#!/usr/bin/make -f

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

SHELL := /bin/bash

top_srcdir := $(shell cd .. ; pwd)

uco_srcdir := $(top_srcdir)/dependencies/UCO

# This list is all of the graph files that contain shapes graphs linked
# by owl:imports, plus the UCO OWL DL shapes.  The UCO OWL DL shapes are
# not linked by owl:imports, to allow for substituting experimental
# shapes or removing the dependency.  Non-shapes graphs are delegated to
# ../ontology/generated-dependencies.ttl.
generated_dependencies_ttls := \
  $(top_srcdir)/dependencies/formatted-gufoshapes.ttl \
  $(uco_srcdir)/ontology/owl/owl.ttl

ttl_basenames := $(wildcard sh-*.ttl)

all: \
  catalog-v001.xml

# .empty.ttl is retained to guarantee rdfpipe takes at least one file as
# an input when building generated-local.ttl.
.empty.ttl:
	test -r $@

catalog-v001.xml: \
  $(top_srcdir)/.venv.done.log \
  $(top_srcdir)/etc/domain_directories.tsv \
  $(top_srcdir)/etc/dependency_files.tsv \
  $(top_srcdir)/src/create-catalog-v001.xml.py \
  $(uco_srcdir)/ontology/uco/master/catalog-v001.xml \
  generated-shapes.ttl
	rm -f _$@
	source $(top_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/src/create-catalog-v001.xml.py \
	    --catalog-xml $(uco_srcdir)/ontology/uco/master/catalog-v001.xml \
	    _$@ \
	    $(top_srcdir)/etc/domain_directories.tsv \
	    $(top_srcdir)/etc/dependency_files.tsv \
	    "$(top_srcdir)" \
	    generated-shapes.ttl
	mv _$@ $@

check: \
  catalog-v001.xml

clean:
	@rm -f \
	  _* \
	  catalog-v001.xml \
	  generated-*

generated-dependencies.ttl: \
  $(generated_dependencies_ttls) \
  $(top_srcdir)/.venv.done.log \
  $(top_srcdir)/ontology/generated-dependencies.ttl \
  .empty.ttl
	source $(top_srcdir)/venv/bin/activate \
	  && rdfpipe \
	    --output-format turtle \
	    $(generated_dependencies_ttls) \
	    .empty.ttl \
	    > _$@
	# Check for conflicts when merging shape files.
	source $(top_srcdir)/venv/bin/activate \
	  && pyshacl \
	    --metashacl \
	    --ont-graph $(top_srcdir)/ontology/generated-dependencies.ttl \
	    --shacl _$@ \
	    .empty.ttl
	mv _$@ $@

generated-local.ttl: \
  $(top_srcdir)/.venv.done.log \
  $(ttl_basenames)
	source $(top_srcdir)/venv/bin/activate \
	  && rdfpipe \
	    --output-format turtle \
	    $(ttl_basenames) \
	    > _$@
	mv _$@ $@

generated-shapes.ttl: \
  $(top_srcdir)/ontology/generated-ontology.ttl \
  generated-dependencies.ttl \
  generated-local.ttl
	source $(top_srcdir)/venv/bin/activate \
	  && rdfpipe \
	    --output-format turtle \
	    generated-dependencies.ttl \
	    generated-local.ttl \
	    > _$@
	# Check for conflicts when merging shape files.
	source $(top_srcdir)/venv/bin/activate \
	  && pyshacl \
	    --metashacl \
	    --ont-graph $(top_srcdir)/ontology/generated-ontology.ttl \
	    --shacl _$@ \
	    .empty.ttl
	mv _$@ $@
