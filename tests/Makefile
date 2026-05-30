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

all: \
  generated-exemplars-expanded.ttl

.pyshacl.done.log: \
  $(top_srcdir)/ontology/generated-ontology.ttl \
  $(top_srcdir)/shapes/generated-shapes.ttl \
  generated-exemplars-expanded.ttl
	source $(top_srcdir)/venv/bin/activate \
	  && pyshacl \
	    --ont-graph $(top_srcdir)/ontology/generated-ontology.ttl \
	    --shacl $(top_srcdir)/shapes/generated-shapes.ttl \
	    generated-exemplars-expanded.ttl
	touch $@

.pytest.done.log: \
  $(top_srcdir)/ontology/generated-ontology.ttl \
  $(top_srcdir)/shapes/generated-local.ttl \
  concepts_excused.txt \
  exemplars.ttl \
  test_exemplar_coverage.py
	source $(top_srcdir)/venv/bin/activate \
	  && python3 -m doctest \
	    test_exemplar_coverage.py
	source $(top_srcdir)/venv/bin/activate \
	  && pytest \
	    --log-level=DEBUG
	touch $@

check: \
  generated-monolithic.ttl \
  .pytest.done.log \
  .pyshacl.done.log

clean:
	@rm -f \
	  .*.done.log \
	  generated-*

generated-exemplars-entailment.ttl: \
  $(top_srcdir)/.venv.done.log \
  $(top_srcdir)/ontology/generated-ontology.ttl \
  $(top_srcdir)/src/entail.py \
  exemplars.ttl
	source $(top_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/src/entail.py \
	    _$@ \
	    exemplars.ttl \
	    $(top_srcdir)/ontology/generated-ontology.ttl
	mv _$@ $@

generated-exemplars-expanded.ttl: \
  generated-exemplars-entailment.ttl
	source $(top_srcdir)/venv/bin/activate \
	  && rdfpipe \
	    --output-format turtle \
	    exemplars.ttl \
	    $< \
	    > _$@
	mv _$@ $@

# Cross-review OWL and SHACL specifications together.
generated-monolithic.ttl: \
  $(top_srcdir)/.venv.done.log \
  $(top_srcdir)/ontology/generated-ontology.ttl \
  $(top_srcdir)/shapes/generated-shapes.ttl \
  $(uco_srcdir)/ontology/owl/owl.ttl
	source $(top_srcdir)/venv/bin/activate \
	  && rdfpipe \
	    --output-format turtle \
	    $(top_srcdir)/ontology/generated-ontology.ttl \
	    $(top_srcdir)/shapes/generated-shapes.ttl \
	    > _$@
	source $(top_srcdir)/venv/bin/activate \
	  && pyshacl \
	    --shacl $(uco_srcdir)/ontology/owl/owl.ttl \
	    _$@
	mv _$@ $@
