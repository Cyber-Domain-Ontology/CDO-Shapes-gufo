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
   1. Update the [README](README.md) to change the name of the repository.  (Minimally, the title line should be revised.)
   1. Addressing the "TODOs" in [`dependencies/Makefile`](dependencies/Makefile)
   1. Updating the TSV files under [`etc/`](etc/).  This is to support local-file editing with some ontology tooling (developed for [UCO Issue 449](https://github.com/ucoProject/UCO/issues/449)).  [These lines](https://github.com/ucoProject/UCO/blob/1.2.0/src/create-catalog-v001.xml.py#L68-L77) describe the file formats.
   1. Renaming the [shapes file under `/shapes`](shapes/sh-example.ttl), and updating its contents.
   1. Updating the [exemplars file under `/tests`](tests/exemplars.ttl) to use all classes and properties reviewed in the shapes graph.
   1. After all of the above edits are completed, running `make check` from the top source directory should confirm Turtle files are normalized and unit tests pass.
1. Push the updated profile to a new repository.
