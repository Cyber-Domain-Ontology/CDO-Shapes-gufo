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

PYTHON3 ?= python3

all: \
  .venv-pre-commit/var/.pre-commit-built.log \
  all-shapes

.PHONY: \
  all-dependencies \
  all-shapes \
  check-dependencies \
  check-mypy \
  check-shapes \
  check-supply-chain \
  check-supply-chain-cdo-shapes \
  check-supply-chain-pre-commit \
  check-supply-chain-submodules

# This Make target should be left in place, even if it does nothing.  It
# has been found beneficial with profiles that have a submodule-based
# dependency on other profiles.
.git_submodule_init_imports.done.log: \
  .gitmodules
	# TODO - Initialize non-CDO submodule here.
	touch $@

.git_submodule_init.done.log: \
  .git_submodule_init_imports.done.log
	git submodule update \
	  --init
	$(MAKE) \
	  --directory dependencies/UCO \
	  .git_submodule_init.done.log \
	  .lib.done.log
	touch $@

.venv.done.log: \
  requirements.txt
	rm -rf venv
	$(PYTHON3) -m venv \
	  venv
	source venv/bin/activate \
	  && pip install \
	    --upgrade \
	    pip \
	    setuptools \
	    wheel
	source venv/bin/activate \
	  && pip install \
	    --requirement requirements.txt
	touch $@

# This virtual environment is meant to be built once and then persist, even through 'make clean'.
# If a recipe is written to remove this flag file, it should first run `pre-commit uninstall`.
.venv-pre-commit/var/.pre-commit-built.log:
	rm -rf .venv-pre-commit
	test -r .pre-commit-config.yaml \
	  || (echo "ERROR:Makefile:pre-commit is expected to install for this repository, but .pre-commit-config.yaml does not seem to exist." >&2 ; exit 1)
	$(PYTHON3) -m venv \
	  .venv-pre-commit
	source .venv-pre-commit/bin/activate \
	  && pip install \
	    --upgrade \
	    pip \
	    setuptools \
	    wheel
	source .venv-pre-commit/bin/activate \
	  && pip install \
	    pre-commit
	source .venv-pre-commit/bin/activate \
	  && pre-commit install
	mkdir -p \
	  .venv-pre-commit/var
	touch $@

all-dependencies: \
  .git_submodule_init.done.log \
  .venv.done.log
	$(MAKE) \
	  --directory dependencies

all-shapes: \
  all-dependencies
	$(MAKE) \
	  --directory shapes

check: \
  .venv-pre-commit/var/.pre-commit-built.log \
  check-mypy \
  check-dependencies \
  check-shapes
	$(MAKE) \
	  --directory tests \
	  check

check-dependencies: \
  all-dependencies
	$(MAKE) \
	  --directory dependencies \
	  check

check-mypy: \
  .venv.done.log
	source venv/bin/activate \
	  && mypy \
	    --exclude dependencies \
	    --exclude venv \
	    --strict \
	    .

check-shapes: \
  all-shapes
	$(MAKE) \
	  --directory shapes \
	  check

# This target's dependencies potentially modify the working directory's
# Git state, so it is intentionally not a dependency of check.
check-supply-chain: \
  check-supply-chain-cdo-shapes \
  check-mypy \
  check-supply-chain-pre-commit \
  check-supply-chain-submodules

check-supply-chain-cdo-shapes:
	git remote get-url \
	  _CHECK_SUPPLY_CHAIN_upstream \
	  || git remote add \
	    _CHECK_SUPPLY_CHAIN_upstream \
	    https://github.com/Cyber-Domain-Ontology/CDO-Shapes-Example.git
	git fetch \
	  _CHECK_SUPPLY_CHAIN_upstream
	@echo "DEBUG:Makefile:$$(git merge-base _CHECK_SUPPLY_CHAIN_upstream/base HEAD) (merge-base)" >&2
	@echo "DEBUG:Makefile:$$(git rev-parse _CHECK_SUPPLY_CHAIN_upstream/base) (base)" >&2
	@echo "DEBUG:Makefile:$$(git rev-parse HEAD) (HEAD)" >&2
	test \
	  "x$$(git merge-base _CHECK_SUPPLY_CHAIN_upstream/base HEAD)" \
	  == \
	  "x$$(git rev-parse _CHECK_SUPPLY_CHAIN_upstream/base)" \
	  || (echo "ERROR:Makefile:The current branch is behind the upstream 'base' branch.  Please merge the upstream 'base' commit into the current branch." >&2 ; exit 1)

# Update pre-commit configuration and use the updated config file to
# review code.  Only have Make exit if 'pre-commit run' modifies files.
check-supply-chain-pre-commit: \
  .venv-pre-commit/var/.pre-commit-built.log
	source .venv-pre-commit/bin/activate \
	  && pre-commit autoupdate
	git diff \
	  --exit-code \
	  .pre-commit-config.yaml \
	  || ( \
	      source .venv-pre-commit/bin/activate \
	        && pre-commit run \
	          --all-files \
	          --config .pre-commit-config.yaml \
	    ) \
	    || git diff \
	      --exit-code \
	      --stat \
	      || ( \
	          echo \
	            "WARNING:Makefile:pre-commit configuration can be updated.  It appears the update would change file formatting." \
	            >&2 \
	            ; exit 1 \
                )
	@git diff \
	  --exit-code \
	  .pre-commit-config.yaml \
	  || echo \
	    "INFO:Makefile:pre-commit configuration can be updated.  It appears the update would not change file formatting." \
	    >&2

check-supply-chain-submodules: \
  .git_submodule_init.done.log
	git submodule update \
	  --remote
	git diff \
	  --exit-code \
	  --ignore-submodules=dirty \
	  dependencies

clean:
	@$(MAKE) \
	  --directory tests \
	  clean
	@$(MAKE) \
	  --directory shapes \
	  clean
	@$(MAKE) \
	  --directory dependencies \
	  clean
	@rm -f \
	  .*.done.log
