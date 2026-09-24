# Contributing

This repository follows [CDO "Continuous-release" branching](https://cyberdomainontology.org/ontology/development/#branching-cdo-continuous).  In short:

* Please file Pull Requests against `main`.
* If you wish to track this repository at a certain version, please use Git submodules to note what version you tracked.

Feedback is welcome, especially with accompanying examples, whether in worked-through RDF or as English narrative.


## Creating new shapes repositories

Shape repositories are started with an in-common Git history, rather than relying on GitHub-specific functions like templating and repository-forking.  The reason for this is to assist with propagating changes seen necessary across all of the shape repositories.

To create a new shapes repository for the ontology with short name `Foo`, we suggest:

1. Clone the upstream example repository: `git clone https://github.com/Cyber-Domain-Ontology/CDO-Shapes-Example.git CDO-Shapes-Foo`.
1. Substitute all references to the "example" ontology with the desired ontology.  Generally, this is handled by:
   1. Updating the [README](README.md) to change the name of the repository.  (Minimally, the title line should be revised.)
   1. Addressing the "TODOs" in [`dependencies/Makefile`](dependencies/Makefile).  Note the `check-supply-chain` recipes will typically apply to repositories that have a similarly named recipe and are linked as submodules.
   1. Updating the TSV files under [`etc/`](etc/).  This is to support local-file editing with some ontology tooling (developed for [UCO Issue 449](https://github.com/ucoProject/UCO/issues/449)).  [These lines](https://github.com/ucoProject/UCO/blob/1.2.0/src/create-catalog-v001.xml.py#L68-L77) describe the file formats.
   1. Adding any supplementary ontology information under [`ontology/cdo-example.ttl`], renaming as appropriate.
   1. Updating the dependency lists in the `normalized_ttls` variable near the top of [`dependencies/Makefile`], and the `generated_dependencies_ttls` variables near the tops of [`ontology/Makefile`] and [`shapes/Makefile`].
   1. Renaming the [shapes file under `/shapes`](shapes/sh-example.ttl), and updating its contents.
   1. Updating the [exemplars file under `/tests`](tests/exemplars.ttl) to use all classes and properties reviewed in the repository-local shapes graph (i.e., the file `/shapes/sh-example.ttl` became).
   1. After all of the above edits are completed, running `make check` from the top source directory should confirm Turtle files are normalized and unit tests pass.
1. Push the updated profile to a new repository.

Note that if this repository is being built upon other shapes repositories, it _is_ an intended effect that the dependency files' source-lists are manually curated, and may become lengthy.  This is due to some syntactic requirements inducing a need to ensure that graph files are only loaded once.  (E.g., some SHACL graphs cannot be loaded twice because of duplicative blank nodes causing conflicts.)
