#!/usr/bin/make -f

# Portions of this file contributed by NIST are governed by the following
# statement:
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

ttl_basenames := $(wildcard sh-*.ttl)

check_ttl_targets := $(foreach ttl_basename,$(ttl_basenames),check-$(ttl_basename))

all: \
  catalog-v001.xml

.PHONY: \
  check-%.ttl

.PRECIOUS: \
  .check-%.ttl

$(RDF_TOOLKIT_JAR):
	@echo "DEBUG:shapes/Makefile:top_srcdir=$(top_srcdir)" >&2
	@echo "ERROR:shapes/Makefile:rdf-toolkit.jar not found.  Did you run `make` from the top source directory?" >&2
	@test -r $@

.check-%.ttl: \
  %.ttl \
  $(RDF_TOOLKIT_JAR)
	java -jar $(RDF_TOOLKIT_JAR) \
	  --inline-blank-nodes \
	  --source $< \
	  --source-format turtle \
	  --target _$@ \
	  --target-format turtle
	mv _$@ $@

catalog-v001.xml: \
  $(top_srcdir)/.venv.done.log \
  $(top_srcdir)/etc/domain_directories.tsv \
  $(top_srcdir)/etc/dependency_files.tsv \
  $(top_srcdir)/src/create-catalog-v001.xml.py \
  $(uco_srcdir)/ontology/uco/master/catalog-v001.xml
	rm -f _$@
	source $(top_srcdir)/venv/bin/activate \
	  && python3 $(top_srcdir)/src/create-catalog-v001.xml.py \
	    --catalog-xml $(uco_srcdir)/ontology/uco/master/catalog-v001.xml \
	    _$@ \
	    $(top_srcdir)/etc/domain_directories.tsv \
	    $(top_srcdir)/etc/dependency_files.tsv \
	    "$(top_srcdir)" \
	    $(ttl_basenames)
	mv _$@ $@

check: \
  $(check_ttl_targets) \
  catalog-v001.xml

check-%.ttl: \
  %.ttl \
  .check-%.ttl
	diff $^	\
	  || (echo "ERROR:shapes/Makefile:The local $< does not match the normalized version. If the above reported changes look fine, run 'cp .check-$< $<' while in the sub-folder shapes/ to get a file ready to commit to Git." >&2 ; exit 1)

clean:
	@rm -f \
	  _* \
	  catalog-v001.xml
