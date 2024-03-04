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

shape_ttls := $(wildcard $(top_srcdir)/shapes/sh-*.ttl)

all: \
  exemplars-expanded.ttl

.pyshacl.done.log: \
  exemplars-expanded.ttl \
  monolithic.ttl
	source $(top_srcdir)/venv/bin/activate \
	  && pyshacl \
	    --metashacl \
	    --ont-graph monolithic.ttl \
	    --shacl monolithic.ttl \
	    exemplars-expanded.ttl
	touch $@

.pytest.done.log: \
  concepts_excused.txt \
  exemplars.ttl \
  monolithic.ttl \
  test_exemplar_coverage.py
	source $(top_srcdir)/venv/bin/activate \
	  && pytest \
	    --log-level=DEBUG
	touch $@

check: \
  .pytest.done.log \
  .pyshacl.done.log

clean:
	@rm -f \
	  .*.done.log \
	  exemplars-entailment.ttl \
	  exemplars-expanded.ttl \
	  monolithic.ttl

exemplars-entailment.ttl: \
  $(top_srcdir)/.venv.done.log \
  $(top_srcdir)/src/entail.py \
  exemplars.ttl \
  monolithic.ttl
	source $(top_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/src/entail.py \
	    _$@ \
	    exemplars.ttl \
	    monolithic.ttl
	mv _$@ $@

exemplars-expanded.ttl: \
  exemplars-entailment.ttl
	source $(top_srcdir)/venv/bin/activate \
	  && rdfpipe \
	    --output-format turtle \
	    exemplars.ttl \
	    $< \
	    > _$@
	mv _$@ $@

monolithic.ttl: \
  $(top_srcdir)/.venv.done.log \
  $(top_srcdir)/dependencies/imports-transitive.ttl \
  $(shape_ttls)
	source $(top_srcdir)/venv/bin/activate \
	  && rdfpipe \
	    --output-format turtle \
	    $(top_srcdir)/dependencies/imports-transitive.ttl \
	    $(shape_ttls) \
	    $(uco_srcdir)/ontology/owl/owl.ttl \
	    > _$@
	source $(top_srcdir)/venv/bin/activate \
	  && pyshacl \
	    --shacl $(uco_srcdir)/ontology/owl/owl.ttl \
	    _$@
	mv _$@ $@
