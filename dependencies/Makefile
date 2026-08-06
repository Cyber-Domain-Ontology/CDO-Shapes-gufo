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

RDF_TOOLKIT_JAR := $(uco_srcdir)/lib/rdf-toolkit.jar

# TODO: This variable lists files for Make to generate and delete on
# 'make clean' calls.  This variable should be adapted to list each file
# to normalize.
# Note that to support the catalog-v001.xml preconditions, this list
# must only be files in this directory.
normalized_ttls := \
  formatted-gufo.ttl \
  formatted-gufoshapes.ttl

all: \
  catalog-v001.xml

$(RDF_TOOLKIT_JAR):
	@echo "DEBUG:dependencies/Makefile:top_srcdir=$(top_srcdir)" >&2
	@echo "ERROR:dependencies/Makefile:rdf-toolkit.jar not found.  Did you run `make` from the top source directory?" >&2
	@test -r $@

catalog-v001.xml: \
  $(normalized_ttls) \
  $(top_srcdir)/.venv.done.log \
  $(top_srcdir)/etc/domain_directories.tsv \
  $(top_srcdir)/etc/dependency_files.tsv \
  $(top_srcdir)/src/create-catalog-v001.xml.py
	rm -f _$@
	source $(top_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/src/create-catalog-v001.xml.py \
	    _$@ \
	    $(top_srcdir)/etc/domain_directories.tsv \
	    $(top_srcdir)/etc/dependency_files.tsv \
	    "$(top_srcdir)" \
	    $(normalized_ttls)
	mv _$@ $@

check: \
  all

clean:
	@rm -f \
	  $(normalized_ttls) \
	  catalog-v001.xml

formatted-gufo.ttl: \
  gufo/gufo.ttl \
  $(RDF_TOOLKIT_JAR) \
  $(top_srcdir)/.venv.done.log
	source $(top_srcdir)/venv/bin/activate \
	  && pyshacl \
	    --shacl UCO/ontology/owl/owl.ttl \
	    $<
	java -jar $(RDF_TOOLKIT_JAR) \
	  --inline-blank-nodes \
	  --source $< \
	  --source-format turtle \
	  --target _$@ \
	  --target-format turtle
	mv _$@ $@

formatted-gufoshapes.ttl: \
  gufoshapes/gufoshapes.ttl \
  $(RDF_TOOLKIT_JAR) \
  $(top_srcdir)/.venv.done.log
	source $(top_srcdir)/venv/bin/activate \
	  && pyshacl \
	    --shacl UCO/ontology/owl/owl.ttl \
	    $<
	java -jar $(RDF_TOOLKIT_JAR) \
	  --inline-blank-nodes \
	  --source $< \
	  --source-format turtle \
	  --target _$@ \
	  --target-format turtle
	mv _$@ $@
