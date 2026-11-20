# gUFO SHACL Validation — Reference Documentation

## 1. Purpose and Scope

This document describes the SHACL validation shapes for ontologies based on the
**gentle Unified Foundational Ontology (gUFO)**. It serves as the authoritative
reference for understanding which gUFO rules are enforced, how each rule is
decomposed into independently verifiable constraints, how those constraints are
formally specified, and how they are implemented and tested.

The validation shapes are defined in `shapes/sh-gufo.ttl` and are applied using
[pyshacl](https://github.com/RDFLib/pySHACL). The test suite is located in the
`tests/` directory.

---

## 2. Repository Structure

```
CDO-Shapes-gufo/
├── shapes/
│   └── sh-gufo.ttl                  # SHACL shape definitions
├── tests/
│   ├── exemplars.ttl                # Valid individuals exercising each shape
│   ├── exemplars_XFAIL.ttl          # Deliberately invalid individuals
│   ├── exemplars_XFAIL_validation.ttl  # Expected SHACL violation reports
│   ├── test_exemplar_coverage.py    # pytest test suite
│   └── sh-qc.ttl                    # Quality-check shapes for test data
└── dependencies/
    └── formatted-gufo.ttl           # gUFO ontology (OWL 2 DL)
```

---

## 3. Validation Pipeline

Validation proceeds in four stages:

1. **Entailment** — `src/entail.py` adds RDFS entailments to `exemplars.ttl`
   (subclass, subproperty, domain, range) so that pyshacl sees inherited types.
   This step applies only to `exemplars.ttl`, not to `exemplars_XFAIL.ttl`.
   Failure test data must therefore declare all types explicitly.

2. **Success validation** — pyshacl validates the expanded exemplars against
   `sh-gufo.ttl` and expects `sh:conforms true`. Any violation indicates a
   regression in the shapes.

3. **Failure validation** — pyshacl validates `exemplars_XFAIL.ttl` and expects
   `sh:conforms false`. The resulting violation report is saved as
   `exemplars_XFAIL_validation.ttl`.

4. **pytest** — `test_exemplar_coverage.py` verifies two things:
   - `test_exemplar_coverage()` confirms that every shape target class and
     property path has at least one exemplar individual in `exemplars.ttl`.
   - Per-rule functions read `exemplars_XFAIL_validation.ttl` and assert that
     exactly the expected violations are present, identified by focus node,
     source shape, and constraint component.

---

## 4. Literature and gUFO Rule Sources

The rules documented here are derived from the following sources, listed in
order of authority:

| Reference | Scope |
|---|---|
| `formatted-gufo.ttl` — the gUFO OWL 2 DL ontology | Authoritative axiomatisation |
| Guizzardi et al. (2022) — *UFO: Unified Foundational Ontology*, Applied Ontology 17(1) | Complete formal specification of all micro-theories |
| Guizzardi (2005) — *Ontological Foundations for Structural Conceptual Models*, PhD thesis, University of Twente | Original axiomatisation of UFO-A (endurants, aspects, relations) |
| Guizzardi et al. (2018) — *Endurant Types in Ontology-Driven Conceptual Modeling: Towards OntoUML 2.0*, ER 2018 | Endurant type taxonomy and constraints |
| Fonseca, Porello, Guizzardi, Almeida & Guarino (2019) — *Relations in Ontology-Driven Conceptual Modeling*, ER 2019 | Material, comparative, relator, and extrinsic mode constraints |
| Carvalho, Almeida, Fonseca & Guizzardi (2017) — *Multi-level ontology-based conceptual modeling*, DKE 109 | `partitions` and `categorizes` powertype patterns |
| Sales & Guizzardi (2015) — *Empirically Uncovered Anti-Patterns*, DKE 99 | RelRig, FreeRole, MultDep anti-patterns |
| Sales & Guizzardi (2019) — *Taxonomic Structures*, CEUR Vol-2519 | MixIden, MixRig, GSRig anti-patterns |

---

## 5. Rule Documentation

Each rule is documented using the following four-part structure:

- **(i) Rule description** — natural language statement of the rule, its
  ontological rationale, and its source in the gUFO literature.
- **(ii) Test aspects** — decomposition of the rule into independently
  verifiable aspects, each with a unique identifier and description.
- **(iii) DL expressions** — formal Description Logic specification for each
  aspect, making the mathematical meaning of every test precise.
- **(iv) Implementation** — the SHACL shape(s), test exemplars (both valid and
  deliberately invalid), and pytest function(s) that realise the validation.

---

### Rule A1 — Every Aspect Inheres in Exactly One ConcreteIndividual

#### (i) Rule Description

In gUFO a `gufo:Aspect` is an endurant that is existentially dependent on
another concrete individual — its *bearer* — through the relation of
*inherence*, expressed by `gufo:inheresIn`. The property is declared functional,
asymmetric, and irreflexive with domain `gufo:Aspect` and range
`gufo:ConcreteIndividual`. Both `gufo:IntrinsicAspect` and `gufo:ExtrinsicMode`
carry an `owl:qualifiedCardinality "1"` restriction on `inheresIn`, expressing
that every aspect inheres in **exactly one** concrete individual — neither zero
nor more than one.

**Sources:** Guizzardi (2005) ch. 4; `formatted-gufo.ttl`
`owl:qualifiedCardinality "1"` on `IntrinsicAspect` and `ExtrinsicMode`.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| A1.1 | Upper bound: an `Aspect` may not inhere in more than one `ConcreteIndividual` |
| A1.2 | Lower bound: every `Aspect` must inhere in at least one `ConcreteIndividual` |
| A1.3 | Range: the object of `inheresIn` must be a `ConcreteIndividual` |
| A1.4 | Domain: only an `Aspect` may be the subject of `inheresIn` |

#### (iii) DL Expressions

**A1.1 — Upper bound:**
$$\text{Aspect} \sqsubseteq \leq 1\,\text{inheresIn}.\text{ConcreteIndividual}$$

**A1.2 — Lower bound:**
$$\text{Aspect} \sqsubseteq \geq 1\,\text{inheresIn}.\text{ConcreteIndividual}$$

**Combined (full gUFO axiom):**
$$\text{Aspect} \sqsubseteq =1\,\text{inheresIn}.\text{ConcreteIndividual}$$

**A1.3 — Range:**
$$\top \sqsubseteq \forall\,\text{inheresIn}.\text{ConcreteIndividual}$$

**A1.4 — Domain:**
$$\exists\,\text{inheresIn}.\top \sqsubseteq \text{Aspect}$$

#### (iv) Implementation

**SHACL shapes:**

`sh-gufo:Aspect-shape` enforces the lower bound (A1.2); the upper bound (A1.1)
is enforced by `sh-gufo:ExtrinsicMode-shape` and `sh-gufo:IntrinsicAspect-shape`
through `sh:qualifiedMaxCount 1`:

```turtle
sh-gufo:Aspect-shape
    a sh:NodeShape ;
    rdfs:comment "rdfs:seeAlso links other shapes that review this class."@en ;
    rdfs:seeAlso sh-gufo:Aspect-disjointWith-Object-shape ;
    sh:property [
        a sh:PropertyShape ;
        sh:message "Every gufo:Aspect must inhere in exactly one ConcreteIndividual ( https://nemo-ufes.github.io/gufo/#inheresIn )."@en ;
        sh:minCount 1 ;
        sh:path gufo:inheresIn ;
    ] ;
    sh:targetClass gufo:Aspect ;
    sh:xone (
        [ a sh:NodeShape ; sh:class gufo:ExtrinsicAspect ; ]
        [ a sh:NodeShape ; sh:class gufo:IntrinsicAspect ; ]
    ) ;
    .

sh-gufo:inheresIn-objects-shape
    a sh:NodeShape ;
    sh:class gufo:ConcreteIndividual ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:targetObjectsOf gufo:inheresIn ;
    .

sh-gufo:inheresIn-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:Aspect ;
    sh:property [
        a sh:PropertyShape ;
        sh:maxCount "1"^^xsd:integer ;
        sh:path gufo:inheresIn ;
    ] ;
    sh:targetSubjectsOf gufo:inheresIn ;
    .
```

**Success test (`tests/exemplars.ttl`):**
```turtle
kb:Aspect-c6c0dc61-2ced-498d-821c-443761c87de0
    a gufo:ExtrinsicMode ;
    gufo:inheresIn kb:ConcreteIndividual-1c404c3c-ecf3-4946-8130-e40548bef69f ;
    rdfs:seeAlso
        sh-gufo:ExtrinsicMode-shape ,
        sh-gufo:inheresIn-subjects-shape ;
    .

kb:ConcreteIndividual-1c404c3c-ecf3-4946-8130-e40548bef69f
    a gufo:Object ;
    rdfs:seeAlso sh-gufo:inheresIn-objects-shape ;
    .
```

**Failure test (`tests/exemplars_XFAIL.ttl`) — A1.2:**
```turtle
kb:ExtrinsicMode-8f4c2a1d-3b7e-4f9a-bc12-5d6e7f8a9b0c
    a gufo:ExtrinsicMode ;
    rdfs:comment "This node is expected to trigger a validation error for being a gufo:Aspect without any gufo:inheresIn triple."@en ;
    rdfs:seeAlso sh-gufo:Aspect-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_aspect_inheres_in() -> None:
    """
    Verifies A1.2: every gufo:Aspect must inhere in at least one
    ConcreteIndividual (sh:minCount 1 on gufo:inheresIn in Aspect-shape).
    An ExtrinsicMode without any inheresIn triple must trigger a
    MinCountConstraintComponent violation on Aspect-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nAspect
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:Aspect-shape ;
    sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
    sh:focusNode ?nAspect ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["ExtrinsicMode-8f4c2a1d-3b7e-4f9a-bc12-5d6e7f8a9b0c"],
    }
```

---

### Rule A2 — Every ExtrinsicMode Must Externally Depend on At Least One Endurant

#### (i) Rule Description

A `gufo:ExtrinsicMode` is an extrinsic aspect that inheres in one concrete
individual (its bearer) but also *externally depends* on at least one other
endurant that is mereologically disjoint from the bearer. This external
dependence is expressed via `gufo:externallyDependsOn`. The gUFO OWL
implementation restricts `gufo:ExtrinsicMode` with
`owl:someValuesFrom gufo:ConcreteIndividual` on `externallyDependsOn`. The
property is also declared `owl:IrreflexiveProperty`.

**Sources:** Guizzardi (2005); `formatted-gufo.ttl`; gUFO documentation §2.7.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| A2.1 | Existential obligation: every `ExtrinsicMode` must have at least one `externallyDependsOn` triple |
| A2.2 | Domain: only an `ExtrinsicMode` may be the subject of `externallyDependsOn` |
| A2.3 | Range: the object of `externallyDependsOn` must be an `Endurant` |

#### (iii) DL Expressions

**A2.1 — Existential obligation:**
$$\text{ExtrinsicMode} \sqsubseteq \geq 1\,\text{externallyDependsOn}.\text{Endurant}$$

**A2.2 — Domain:**
$$\exists\,\text{externallyDependsOn}.\top \sqsubseteq \text{ExtrinsicMode}$$

**A2.3 — Range:**
$$\top \sqsubseteq \forall\,\text{externallyDependsOn}.\text{Endurant}$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:ExtrinsicMode-shape
    a sh:NodeShape ;
    sh:property
        [
            a sh:PropertyShape ;
            sh:message "Every gufo:ExtrinsicMode must externally depend on at least one Endurant ( https://nemo-ufes.github.io/gufo/#externallyDependsOn )."@en ;
            sh:minCount 1 ;
            sh:path gufo:externallyDependsOn ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path gufo:inheresIn ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:ConcreteIndividual ;
            ] ;
        ] ;
    sh:targetClass gufo:ExtrinsicMode ;
    .

sh-gufo:externallyDependsOn-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:ExtrinsicMode ;
    sh:targetSubjectsOf gufo:externallyDependsOn ;
    .

sh-gufo:externallyDependsOn-objects-shape
    a sh:NodeShape ;
    sh:class gufo:Endurant ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:targetObjectsOf gufo:externallyDependsOn ;
    .
```

**Success test (`tests/exemplars.ttl`):**
```turtle
kb:ExtrinsicMode-01964f52-6337-4703-80d2-5903d7635901
    a gufo:ExtrinsicMode ;
    gufo:externallyDependsOn kb:Endurant-2617295a-5922-4d06-90ce-83845c2914af ;
    rdfs:seeAlso sh-gufo:externallyDependsOn-subjects-shape ;
    .

kb:Endurant-2617295a-5922-4d06-90ce-83845c2914af
    a gufo:Object ;
    rdfs:seeAlso sh-gufo:externallyDependsOn-objects-shape ;
    .
```

**Failure test (`tests/exemplars_XFAIL.ttl`) — A2.1:**
```turtle
kb:ExtrinsicMode-3c7d1e2f-5a6b-4c8d-9e0f-1a2b3c4d5e6f
    a gufo:ExtrinsicMode ;
    gufo:inheresIn kb:ConcreteIndividual-1c404c3c-ecf3-4946-8130-e40548bef69f ;
    rdfs:comment "This node is expected to trigger a validation error for being a gufo:ExtrinsicMode without any gufo:externallyDependsOn triple."@en ;
    rdfs:seeAlso sh-gufo:ExtrinsicMode-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_extrinsicmode_externally_depends_on() -> None:
    """
    Verifies A2.1: every gufo:ExtrinsicMode must externally depend on at
    least one Endurant (sh:minCount 1 on gufo:externallyDependsOn).
    An ExtrinsicMode without any externallyDependsOn triple must trigger a
    MinCountConstraintComponent violation on ExtrinsicMode-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nExtrinsicMode
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:ExtrinsicMode-shape ;
    sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
    sh:focusNode ?nExtrinsicMode ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["ExtrinsicMode-3c7d1e2f-5a6b-4c8d-9e0f-1a2b3c4d5e6f"],
    }
```

---

### Rule A3 — TemporaryConstitutionSituation Must Have Exactly One concernsConstitutedEndurant

#### (i) Rule Description

A `gufo:TemporaryConstitutionSituation` represents a situation in which one
endurant temporarily constitutes another. It must be associated with exactly one
constituted endurant via `gufo:concernsConstitutedEndurant`, and must be
referenced by exactly one constituting endurant via the inverse of
`gufo:standsInQualifiedConstitution`. The gUFO OWL implementation declares
`owl:qualifiedCardinality "1"` on both paths.

**Sources:** `formatted-gufo.ttl`; gUFO documentation §2.1.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| A3.1 | Upper bound: at most one `concernsConstitutedEndurant` |
| A3.2 | Lower bound: at least one `concernsConstitutedEndurant` |
| A3.3 | Range: object of `concernsConstitutedEndurant` must be an `Endurant` |
| A3.4 | Domain: subject of `concernsConstitutedEndurant` must be a `TemporaryConstitutionSituation` |
| A3.5 | Upper bound on inverse: at most one `Endurant` uses this situation via `standsInQualifiedConstitution` |

#### (iii) DL Expressions

**A3.1 — Upper bound:**
$$\text{TemporaryConstitutionSituation} \sqsubseteq \leq 1\,\text{concernsConstitutedEndurant}.\text{Object}$$

**A3.2 — Lower bound:**
$$\text{TemporaryConstitutionSituation} \sqsubseteq \geq 1\,\text{concernsConstitutedEndurant}.\top$$

**Combined:**
$$\text{TemporaryConstitutionSituation} \sqsubseteq =1\,\text{concernsConstitutedEndurant}.\text{Object}$$

**A3.3 — Range:**
$$\top \sqsubseteq \forall\,\text{concernsConstitutedEndurant}.\text{Endurant}$$

**A3.4 — Domain:**
$$\exists\,\text{concernsConstitutedEndurant}.\top \sqsubseteq \text{TemporaryConstitutionSituation}$$

**A3.5 — Upper bound on inverse:**
$$\text{TemporaryConstitutionSituation} \sqsubseteq \leq 1\,\text{standsInQualifiedConstitution}^-.\text{Object}$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:TemporaryConstitutionSituation-shape
    a sh:NodeShape ;
    sh:property
        [
            a sh:PropertyShape ;
            sh:message "Every gufo:TemporaryConstitutionSituation must concern exactly one constituted Endurant ( https://nemo-ufes.github.io/gufo/#concernsConstitutedEndurant )."@en ;
            sh:minCount 1 ;
            sh:path gufo:concernsConstitutedEndurant ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path gufo:concernsConstitutedEndurant ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Object ;
            ] ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path [ sh:inversePath gufo:standsInQualifiedConstitution ] ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Object ;
            ] ;
        ] ;
    sh:targetClass gufo:TemporaryConstitutionSituation ;
    .

sh-gufo:concernsConstitutedEndurant-objects-shape
    a sh:NodeShape ;
    sh:class gufo:Endurant ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:targetObjectsOf gufo:concernsConstitutedEndurant ;
    .

sh-gufo:concernsConstitutedEndurant-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:TemporaryConstitutionSituation ;
    sh:targetSubjectsOf gufo:concernsConstitutedEndurant ;
    .
```

**Success tests (`tests/exemplars.ttl`):**
```turtle
kb:TemporaryConstitutionSituation-490fa048-fc2a-4434-8376-80579af09d88
    a gufo:TemporaryConstitutionSituation ;
    gufo:concernsConstitutedEndurant kb:Endurant-11b7d0cf-3a5e-40da-a79c-a6b9c243ee28 ;
    rdfs:seeAlso
        sh-gufo:TemporaryConstitutionSituation-shape ,
        sh-gufo:concernsConstitutedEndurant-subjects-shape ;
    .

kb:TemporaryConstitutionSituation-932e7a34-1d58-4e8b-8265-9f8f62bb0c34
    a gufo:TemporaryConstitutionSituation ;
    rdfs:seeAlso sh-gufo:standsInQualifiedConstitution-objects-shape ;
    .
```

**Failure test (`tests/exemplars_XFAIL.ttl`) — A3.2:**
```turtle
kb:TemporaryConstitutionSituation-4d8e2f3a-6b7c-4d9e-0f1a-2b3c4d5e6f7a
    a gufo:TemporaryConstitutionSituation ;
    rdfs:comment "This node is expected to trigger a validation error for being a gufo:TemporaryConstitutionSituation without any gufo:concernsConstitutedEndurant triple."@en ;
    rdfs:seeAlso sh-gufo:TemporaryConstitutionSituation-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_temporary_constitution_situation() -> None:
    """
    Verifies A3.2: every gufo:TemporaryConstitutionSituation must concern at
    least one constituted Endurant (sh:minCount 1 on
    gufo:concernsConstitutedEndurant). A TemporaryConstitutionSituation without
    a concernsConstitutedEndurant triple must trigger a
    MinCountConstraintComponent violation on TemporaryConstitutionSituation-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nSituation
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:TemporaryConstitutionSituation-shape ;
    sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
    sh:focusNode ?nSituation ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["TemporaryConstitutionSituation-4d8e2f3a-6b7c-4d9e-0f1a-2b3c4d5e6f7a"],
    }
```

---

### Rule A4 — TemporaryInstantiationSituation Must Have Exactly One concernsNonRigidType

#### (i) Rule Description

A `gufo:TemporaryInstantiationSituation` captures a situation in which an
endurant temporarily instantiates a `gufo:NonRigidType`. It must be associated
with exactly one `NonRigidType` via `gufo:concernsNonRigidType`, and must be
referenced by exactly one endurant via the inverse of
`gufo:standsInQualifiedInstantiation`. The gUFO OWL implementation declares
`owl:qualifiedCardinality "1"` on both paths.

**Sources:** `formatted-gufo.ttl`; gUFO documentation §2.9.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| A4.1 | Upper bound: at most one `concernsNonRigidType` |
| A4.2 | Lower bound: at least one `concernsNonRigidType` |
| A4.3 | Range: object must be a `NonRigidType` |
| A4.4 | Domain: subject must be a `TemporaryInstantiationSituation` |
| A4.5 | Upper bound on inverse: at most one `Endurant` uses this situation |

#### (iii) DL Expressions

**A4.1 — Upper bound:**
$$\text{TemporaryInstantiationSituation} \sqsubseteq \leq 1\,\text{concernsNonRigidType}.\text{NonRigidType}$$

**A4.2 — Lower bound:**
$$\text{TemporaryInstantiationSituation} \sqsubseteq \geq 1\,\text{concernsNonRigidType}.\top$$

**Combined:**
$$\text{TemporaryInstantiationSituation} \sqsubseteq =1\,\text{concernsNonRigidType}.\text{NonRigidType}$$

**A4.3 — Range:**
$$\top \sqsubseteq \forall\,\text{concernsNonRigidType}.\text{NonRigidType}$$

**A4.4 — Domain:**
$$\exists\,\text{concernsNonRigidType}.\top \sqsubseteq \text{TemporaryInstantiationSituation}$$

**A4.5 — Upper bound on inverse:**
$$\text{TemporaryInstantiationSituation} \sqsubseteq \leq 1\,\text{standsInQualifiedInstantiation}^-.\text{Endurant}$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:TemporaryInstantiationSituation-shape
    a sh:NodeShape ;
    sh:property
        [
            a sh:PropertyShape ;
            sh:message "Every gufo:TemporaryInstantiationSituation must concern at least one NonRigidType ( https://nemo-ufes.github.io/gufo/#concernsNonRigidType )."@en ;
            sh:minCount 1 ;
            sh:path gufo:concernsNonRigidType ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path gufo:concernsNonRigidType ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:NonRigidType ;
            ] ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path [ sh:inversePath gufo:standsInQualifiedInstantiation ] ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Endurant ;
            ] ;
        ] ;
    sh:targetClass gufo:TemporaryInstantiationSituation ;
    .

sh-gufo:concernsNonRigidType-objects-shape
    a sh:NodeShape ;
    sh:class gufo:NonRigidType ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:targetObjectsOf gufo:concernsNonRigidType ;
    .

sh-gufo:concernsNonRigidType-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:TemporaryInstantiationSituation ;
    sh:property [
        a sh:PropertyShape ;
        sh:maxCount "1"^^xsd:integer ;
        sh:path gufo:concernsNonRigidType ;
    ] ;
    sh:targetSubjectsOf gufo:concernsNonRigidType ;
    .
```

**Success tests (`tests/exemplars.ttl`):**
```turtle
kb:TemporaryInstantiationSituation-41702321-9550-458b-9438-f48d28d7e0c8
    a gufo:TemporaryInstantiationSituation ;
    gufo:concernsNonRigidType kb:NonRigidType-0a7a7dc6-842e-4542-a360-56c4f2f13308 ;
    rdfs:seeAlso
        sh-gufo:TemporaryInstantiationSituation-shape ,
        sh-gufo:concernsNonRigidType-subjects-shape ;
    .

kb:TemporaryInstantiationSituation-d50f30d2-d042-4003-9b81-5878e348bbc6
    a gufo:TemporaryInstantiationSituation ;
    rdfs:seeAlso sh-gufo:standsInQualifiedInstantiation-objects-shape ;
    .
```

**Failure test (`tests/exemplars_XFAIL.ttl`) — A4.2:**
```turtle
kb:TemporaryInstantiationSituation-5e9f3a4b-7c8d-4e0f-1a2b-3c4d5e6f7a8b
    a gufo:TemporaryInstantiationSituation ;
    rdfs:comment "This node is expected to trigger a validation error for being a gufo:TemporaryInstantiationSituation without any gufo:concernsNonRigidType triple."@en ;
    rdfs:seeAlso sh-gufo:TemporaryInstantiationSituation-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_temporary_instantiation_situation() -> None:
    """
    Verifies A4.2: every gufo:TemporaryInstantiationSituation must concern at
    least one NonRigidType (sh:minCount 1 on gufo:concernsNonRigidType). A
    TemporaryInstantiationSituation without a concernsNonRigidType triple must
    trigger a MinCountConstraintComponent violation on
    TemporaryInstantiationSituation-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nSituation
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:TemporaryInstantiationSituation-shape ;
    sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
    sh:focusNode ?nSituation ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["TemporaryInstantiationSituation-5e9f3a4b-7c8d-4e0f-1a2b-3c4d5e6f7a8b"],
    }
```

---

### Rule A5 — TemporaryParthoodSituation Must Have Exactly One concernsTemporaryWhole

#### (i) Rule Description

A `gufo:TemporaryParthoodSituation` captures a situation in which an endurant
is temporarily part of another. It must be associated with exactly one whole via
`gufo:concernsTemporaryWhole`, and must be referenced by exactly one endurant
via the inverse of `gufo:standsInQualifiedParthood`. The gUFO OWL implementation
declares `owl:qualifiedCardinality "1"` on both paths.

**Sources:** `formatted-gufo.ttl`; gUFO documentation §2.2.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| A5.1 | Upper bound: at most one `concernsTemporaryWhole` |
| A5.2 | Lower bound: at least one `concernsTemporaryWhole` |
| A5.3 | Range: object must be an `Endurant` |
| A5.4 | Domain: subject must be a `TemporaryParthoodSituation` |
| A5.5 | Upper bound on inverse: at most one `Endurant` uses this situation |

#### (iii) DL Expressions

**A5.1 — Upper bound:**
$$\text{TemporaryParthoodSituation} \sqsubseteq \leq 1\,\text{concernsTemporaryWhole}.\text{Endurant}$$

**A5.2 — Lower bound:**
$$\text{TemporaryParthoodSituation} \sqsubseteq \geq 1\,\text{concernsTemporaryWhole}.\top$$

**Combined:**
$$\text{TemporaryParthoodSituation} \sqsubseteq =1\,\text{concernsTemporaryWhole}.\text{Endurant}$$

**A5.3 — Range:**
$$\top \sqsubseteq \forall\,\text{concernsTemporaryWhole}.\text{Endurant}$$

**A5.4 — Domain:**
$$\exists\,\text{concernsTemporaryWhole}.\top \sqsubseteq \text{TemporaryParthoodSituation}$$

**A5.5 — Upper bound on inverse:**
$$\text{TemporaryParthoodSituation} \sqsubseteq \leq 1\,\text{standsInQualifiedParthood}^-.\text{Endurant}$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:TemporaryParthoodSituation-shape
    a sh:NodeShape ;
    sh:property
        [
            a sh:PropertyShape ;
            sh:message "Every gufo:TemporaryParthoodSituation must concern at least one temporary whole ( https://nemo-ufes.github.io/gufo/#concernsTemporaryWhole )."@en ;
            sh:minCount 1 ;
            sh:path gufo:concernsTemporaryWhole ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path gufo:concernsTemporaryWhole ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Endurant ;
            ] ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path [ sh:inversePath gufo:standsInQualifiedParthood ] ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Endurant ;
            ] ;
        ] ;
    sh:targetClass gufo:TemporaryParthoodSituation ;
    .

sh-gufo:concernsTemporaryWhole-objects-shape
    a sh:NodeShape ;
    sh:class gufo:Endurant ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:targetObjectsOf gufo:concernsTemporaryWhole ;
    .

sh-gufo:concernsTemporaryWhole-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:TemporaryParthoodSituation ;
    sh:property [
        a sh:PropertyShape ;
        sh:maxCount "1"^^xsd:integer ;
        sh:path gufo:concernsTemporaryWhole ;
    ] ;
    sh:targetSubjectsOf gufo:concernsTemporaryWhole ;
    .
```

**Success tests (`tests/exemplars.ttl`):**
```turtle
kb:TemporaryParthoodSituation-4292a36e-659c-4644-a197-a0e84dfb2394
    a gufo:TemporaryParthoodSituation ;
    gufo:concernsTemporaryWhole kb:Endurant-4053ed7d-05c9-44ce-869f-2745d84a40ce ;
    rdfs:seeAlso
        sh-gufo:TemporaryParthoodSituation-shape ,
        sh-gufo:concernsTemporaryWhole-subjects-shape ;
    .

kb:TemporaryParthoodSituation-bdfd62c0-4188-4cc2-a823-2664b8478fe1
    a gufo:TemporaryParthoodSituation ;
    rdfs:seeAlso sh-gufo:standsInQualifiedParthood-objects-shape ;
    .
```

**Failure test (`tests/exemplars_XFAIL.ttl`) — A5.2:**
```turtle
kb:TemporaryParthoodSituation-6f0a4b5c-8d9e-4f1a-2b3c-4d5e6f7a8b9c
    a gufo:TemporaryParthoodSituation ;
    rdfs:comment "This node is expected to trigger a validation error for being a gufo:TemporaryParthoodSituation without any gufo:concernsTemporaryWhole triple."@en ;
    rdfs:seeAlso sh-gufo:TemporaryParthoodSituation-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_temporary_parthood_situation() -> None:
    """
    Verifies A5.2: every gufo:TemporaryParthoodSituation must concern at
    least one temporary whole (sh:minCount 1 on gufo:concernsTemporaryWhole).
    A TemporaryParthoodSituation without a concernsTemporaryWhole triple must
    trigger a MinCountConstraintComponent violation on
    TemporaryParthoodSituation-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nSituation
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:TemporaryParthoodSituation-shape ;
    sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
    sh:focusNode ?nSituation ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["TemporaryParthoodSituation-6f0a4b5c-8d9e-4f1a-2b3c-4d5e6f7a8b9c"],
    }
```

---

### Rule A6 — TemporaryRelationshipSituation Must Have One RelationshipType and At Least One Related Endurant

#### (i) Rule Description

A `gufo:TemporaryRelationshipSituation` reifies a temporary relationship between
endurants. It must be associated with exactly one `gufo:RelationshipType` via
`gufo:concernsRelationshipType` (`owl:qualifiedCardinality "1"`) and with at
least one related endurant via `gufo:concernsRelatedEndurant`
(`owl:someValuesFrom gufo:Endurant`). It must also be referenced by exactly one
endurant via the inverse of `gufo:standsInQualifiedRelationship`.

**Sources:** `formatted-gufo.ttl`; gUFO documentation §2.9.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| A6.1 | Upper bound on `concernsRelationshipType`: at most one |
| A6.2 | Lower bound on `concernsRelationshipType`: at least one |
| A6.3 | Lower bound on `concernsRelatedEndurant`: at least one |
| A6.4 | Upper bound on `concernsRelatedEndurant`: at most one |
| A6.5 | Range of `concernsRelationshipType`: object must be a `RelationshipType` |
| A6.6 | Range of `concernsRelatedEndurant`: object must be an `Endurant` |
| A6.7 | Domain of `concernsRelationshipType`: subject must be a `TemporaryRelationshipSituation` |
| A6.8 | Domain of `concernsRelatedEndurant`: subject must be a `TemporaryRelationshipSituation` |
| A6.9 | Upper bound on inverse: at most one `Endurant` uses this situation |

#### (iii) DL Expressions

**A6.1:**
$$\text{TemporaryRelationshipSituation} \sqsubseteq \leq 1\,\text{concernsRelationshipType}.\text{RelationshipType}$$

**A6.2:**
$$\text{TemporaryRelationshipSituation} \sqsubseteq \geq 1\,\text{concernsRelationshipType}.\top$$

**A6.3:**
$$\text{TemporaryRelationshipSituation} \sqsubseteq \geq 1\,\text{concernsRelatedEndurant}.\text{Endurant}$$

**A6.4:**
$$\text{TemporaryRelationshipSituation} \sqsubseteq \leq 1\,\text{concernsRelatedEndurant}.\text{Endurant}$$

**A6.5:**
$$\top \sqsubseteq \forall\,\text{concernsRelationshipType}.\text{RelationshipType}$$

**A6.6:**
$$\top \sqsubseteq \forall\,\text{concernsRelatedEndurant}.\text{Endurant}$$

**A6.7:**
$$\exists\,\text{concernsRelationshipType}.\top \sqsubseteq \text{TemporaryRelationshipSituation}$$

**A6.8:**
$$\exists\,\text{concernsRelatedEndurant}.\top \sqsubseteq \text{TemporaryRelationshipSituation}$$

**A6.9:**
$$\text{TemporaryRelationshipSituation} \sqsubseteq \leq 1\,\text{standsInQualifiedRelationship}^-.\text{Endurant}$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:TemporaryRelationshipSituation-shape
    a sh:NodeShape ;
    sh:property
        [
            a sh:PropertyShape ;
            sh:message "Every gufo:TemporaryRelationshipSituation must concern at least one RelationshipType ( https://nemo-ufes.github.io/gufo/#concernsRelationshipType )."@en ;
            sh:minCount 1 ;
            sh:path gufo:concernsRelationshipType ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path gufo:concernsRelationshipType ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:RelationshipType ;
            ] ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:message "Every gufo:TemporaryRelationshipSituation must concern at least one related Endurant ( https://nemo-ufes.github.io/gufo/#concernsRelatedEndurant )."@en ;
            sh:minCount 1 ;
            sh:path gufo:concernsRelatedEndurant ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path gufo:concernsRelatedEndurant ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Endurant ;
            ] ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path [ sh:inversePath gufo:standsInQualifiedRelationship ] ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Endurant ;
            ] ;
        ] ;
    sh:targetClass gufo:TemporaryRelationshipSituation ;
    .

sh-gufo:concernsRelationshipType-objects-shape
    a sh:NodeShape ;
    sh:class gufo:RelationshipType ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:targetObjectsOf gufo:concernsRelationshipType ;
    .

sh-gufo:concernsRelationshipType-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:TemporaryRelationshipSituation ;
    sh:property [
        a sh:PropertyShape ;
        sh:maxCount "1"^^xsd:integer ;
        sh:path gufo:concernsRelationshipType ;
    ] ;
    sh:targetSubjectsOf gufo:concernsRelationshipType ;
    .

sh-gufo:concernsRelatedEndurant-objects-shape
    a sh:NodeShape ;
    sh:class gufo:Endurant ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:targetObjectsOf gufo:concernsRelatedEndurant ;
    .

sh-gufo:concernsRelatedEndurant-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:TemporaryRelationshipSituation ;
    sh:property [
        a sh:PropertyShape ;
        sh:maxCount "1"^^xsd:integer ;
        sh:path gufo:concernsRelatedEndurant ;
    ] ;
    sh:targetSubjectsOf gufo:concernsRelatedEndurant ;
    .
```

**Success tests (`tests/exemplars.ttl`):**
```turtle
kb:TemporaryRelationshipSituation-f874b7a3-5add-49f4-895c-9fbe42b40095
    a gufo:TemporaryRelationshipSituation ;
    gufo:concernsRelationshipType kb:RelationshipType-0813ed87-2f47-4a1b-a063-834b467c3d31 ;
    rdfs:seeAlso sh-gufo:concernsRelationshipType-subjects-shape ;
    .

kb:TemporaryRelationshipSituation-2a64c96d-9629-4c29-9d63-e6f69cdbdabd
    a gufo:TemporaryRelationshipSituation ;
    gufo:concernsRelatedEndurant kb:Endurant-7ac20c26-1f62-40c1-a6e0-0e96fb088e9b ;
    rdfs:seeAlso sh-gufo:concernsRelatedEndurant-subjects-shape ;
    .

kb:TemporaryRelationshipSituation-29301400-6b45-4176-b570-f52c28cd2789
    a gufo:TemporaryRelationshipSituation ;
    rdfs:seeAlso sh-gufo:standsInQualifiedRelationship-objects-shape ;
    .
```

**Failure tests (`tests/exemplars_XFAIL.ttl`) — A6.2 and A6.3:**
```turtle
kb:TemporaryRelationshipSituation-7a1b5c6d-9e0f-4a1b-3c4d-5e6f7a8b9c0d
    a gufo:TemporaryRelationshipSituation ;
    gufo:concernsRelatedEndurant kb:Endurant-7ac20c26-1f62-40c1-a6e0-0e96fb088e9b ;
    rdfs:comment "This node is expected to trigger a validation error for being a gufo:TemporaryRelationshipSituation without any gufo:concernsRelationshipType triple."@en ;
    rdfs:seeAlso sh-gufo:TemporaryRelationshipSituation-shape ;
    .

kb:TemporaryRelationshipSituation-8b2c6d7e-0f1a-4b2c-4d5e-6f7a8b9c0d1e
    a gufo:TemporaryRelationshipSituation ;
    gufo:concernsRelationshipType kb:RelationshipType-0813ed87-2f47-4a1b-a063-834b467c3d31 ;
    rdfs:comment "This node is expected to trigger a validation error for being a gufo:TemporaryRelationshipSituation without any gufo:concernsRelatedEndurant triple."@en ;
    rdfs:seeAlso sh-gufo:TemporaryRelationshipSituation-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_temporary_relationship_situation() -> None:
    """
    Verifies A6.2 and A6.3: every gufo:TemporaryRelationshipSituation must
    concern at least one RelationshipType and at least one related Endurant.
    Two separate focus nodes are expected, one for each missing property.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")
    ns_gufo = Namespace("http://purl.org/nemo/gufo#")

    pairs: Set[Tuple[URIRef, URIRef]] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nSituation ?nPath
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:TemporaryRelationshipSituation-shape ;
    sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
    sh:focusNode ?nSituation ;
    sh:resultPath ?nPath ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        assert isinstance(result[1], URIRef)
        pairs.add((result[0], result[1]))

    assert pairs == {
        (
            ns_kb["TemporaryRelationshipSituation-7a1b5c6d-9e0f-4a1b-3c4d-5e6f7a8b9c0d"],
            ns_gufo["concernsRelationshipType"],
        ),
        (
            ns_kb["TemporaryRelationshipSituation-8b2c6d7e-0f1a-4b2c-4d5e-6f7a8b9c0d1e"],
            ns_gufo["concernsRelatedEndurant"],
        ),
    }
```

---

### Rule B1 — QualityValueAttributionSituation Uses Exactly One Quality Value Pattern

#### (i) Rule Description

A `gufo:QualityValueAttributionSituation` must be associated with a quality
value using exactly one of two mutually exclusive patterns: either a reified
quality value via `gufo:concernsReifiedQualityValue`, or a literal value via
`gufo:concernsQualityValue`. The two patterns are alternatives — using both
simultaneously is semantically inconsistent, and using neither makes the
situation meaningless. The gUFO OWL implementation expresses this as
`owl:unionOf` of two cardinality restrictions.

**Sources:** `formatted-gufo.ttl`; gUFO documentation §2.5.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| B1.1 | Exactly one pattern present: a QVAS with neither property is invalid |
| B1.2 | Mutual exclusion: a QVAS with both properties simultaneously is invalid |
| B1.3 | Upper bound on `concernsReifiedQualityValue`: at most one |
| B1.4 | Upper bound on `concernsQualityValue`: at most one |
| B1.5 | Range of `concernsReifiedQualityValue`: object must be a `QualityValue` |
| B1.6 | Domain of `concernsReifiedQualityValue`: subject must be a QVAS |
| B1.7 | Domain of `concernsQualityValue`: subject must be a QVAS |
| B1.8 | Range of `concernsQualityValue`: object must be a `Literal` |

#### (iii) DL Expressions

**B1.1+B1.2 — Exclusive disjunction (xone semantics):**
$$\text{QVAS} \sqsubseteq \bigoplus\{(\exists\,\text{concernsReifiedQualityValue}.\text{QualityValue}),\ (\exists\,\text{concernsQualityValue}.\top)\}$$

where $\bigoplus$ denotes exclusive disjunction.

**B1.3 — Upper bound on `concernsReifiedQualityValue`:**
$$\text{QVAS} \sqsubseteq \leq 1\,\text{concernsReifiedQualityValue}.\text{QualityValue}$$

**B1.4 — Upper bound on `concernsQualityValue`:**
$$\text{QVAS} \sqsubseteq \leq 1\,\text{concernsQualityValue}.\top$$

**B1.5 — Range of `concernsReifiedQualityValue`:**
$$\top \sqsubseteq \forall\,\text{concernsReifiedQualityValue}.\text{QualityValue}$$

**B1.6 — Domain of `concernsReifiedQualityValue`:**
$$\exists\,\text{concernsReifiedQualityValue}.\top \sqsubseteq \text{QVAS}$$

**B1.7 — Domain of `concernsQualityValue`:**
$$\exists\,\text{concernsQualityValue}.\top \sqsubseteq \text{QVAS}$$

**B1.8 — Range of `concernsQualityValue`:**
$$\top \sqsubseteq \forall\,\text{concernsQualityValue}.\text{Literal}$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:QualityValueAttributionSituation-shape
    a sh:NodeShape ;
    sh:xone (
        [
            a sh:NodeShape ;
            sh:property [
                a sh:PropertyShape ;
                sh:path gufo:concernsReifiedQualityValue ;
                sh:qualifiedMaxCount "1"^^xsd:integer ;
                sh:qualifiedMinCount "1"^^xsd:integer ;
                sh:qualifiedValueShape [
                    a sh:NodeShape ;
                    sh:class gufo:QualityValue ;
                ] ;
            ] ;
        ]
        [
            a sh:NodeShape ;
            sh:property [
                a sh:PropertyShape ;
                sh:maxCount "1"^^xsd:integer ;
                sh:minCount 1 ;
                sh:path gufo:concernsQualityValue ;
            ] ;
        ]
    ) ;
    sh:property
        [
            a sh:PropertyShape ;
            sh:path gufo:concernsQualityType ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:EndurantType ;
            ] ;
        ] ,
        [
            a sh:PropertyShape ;
            sh:path [ sh:inversePath gufo:standsInQualifiedAttribution ] ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Endurant ;
            ] ;
        ] ;
    sh:targetClass gufo:QualityValueAttributionSituation ;
    .
```

**Success tests (`tests/exemplars.ttl`):**
```turtle
kb:QualityValueAttributionSituation-20fec4d2-6e44-49ed-94aa-799845277a8c
    a gufo:QualityValueAttributionSituation ;
    gufo:concernsQualityValue "" ;
    rdfs:seeAlso
        sh-gufo:QualityValueAttributionSituation-shape ,
        sh-gufo:concernsQualityValue-subjects-shape ;
    .

kb:QualityValueAttributionSituation-87d3fdff-f584-43f9-9339-974d46cc3187
    a gufo:QualityValueAttributionSituation ;
    gufo:concernsReifiedQualityValue kb:QualityValue-bbbc153a-8979-4ca8-a1cc-89a53194c5c8 ;
    rdfs:seeAlso sh-gufo:concernsReifiedQualityValue-subjects-shape ;
    .
```

**Failure tests (`tests/exemplars_XFAIL.ttl`) — B1.1 and B1.2:**
```turtle
kb:QualityValueAttributionSituation-9c3d7e8f-1a2b-4c3d-5e6f-7a8b9c0d1e2f
    a gufo:QualityValueAttributionSituation ;
    gufo:concernsReifiedQualityValue kb:QualityValue-bbbc153a-8979-4ca8-a1cc-89a53194c5c8 ;
    gufo:concernsQualityValue "" ;
    rdfs:comment "This node is expected to trigger a validation error for having both gufo:concernsReifiedQualityValue and gufo:concernsQualityValue simultaneously."@en ;
    rdfs:seeAlso sh-gufo:QualityValueAttributionSituation-shape ;
    .

kb:QualityValueAttributionSituation-0d4e8f9a-2b3c-4d4e-6f7a-8b9c0d1e2f3a
    a gufo:QualityValueAttributionSituation ;
    rdfs:comment "This node is expected to trigger a validation error for having neither gufo:concernsReifiedQualityValue nor gufo:concernsQualityValue."@en ;
    rdfs:seeAlso sh-gufo:QualityValueAttributionSituation-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_quality_value_attribution_xone() -> None:
    """
    Verifies B1.1 and B1.2: a gufo:QualityValueAttributionSituation must use
    exactly one quality value pattern (sh:xone). Having neither pattern
    (B1.1) or having both simultaneously (B1.2) must each produce an
    XoneConstraintComponent violation on QualityValueAttributionSituation-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nSituation
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:QualityValueAttributionSituation-shape ;
    sh:sourceConstraintComponent sh:XoneConstraintComponent ;
    sh:focusNode ?nSituation ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["QualityValueAttributionSituation-9c3d7e8f-1a2b-4c3d-5e6f-7a8b9c0d1e2f"],
        ns_kb["QualityValueAttributionSituation-0d4e8f9a-2b3c-4d4e-6f7a-8b9c0d1e2f3a"],
    }
```

---

### Rule B2 — concernsQualityType Range Must Be a Subclass of gufo:Quality

#### (i) Rule Description

The property `gufo:concernsQualityType` identifies the quality type whose value
is attributed in a `gufo:QualityValueAttributionSituation`. gUFO specifies that
the range must be a subclass of `gufo:Quality` — not merely any
`gufo:EndurantType`. Without this tighter constraint, a `gufo:Kind` that
subclasses `gufo:Object` would incorrectly pass validation as a quality type.

**Sources:** gUFO documentation for `concernsQualityType`; `formatted-gufo.ttl`.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| B2.1 | Range is an `EndurantType` |
| B2.2 | Range is specifically a subclass of `gufo:Quality` |
| B2.3 | Domain: subject must be a `QualityValueAttributionSituation` |
| B2.4 | Upper bound: at most one `concernsQualityType` per QVAS |

#### (iii) DL Expressions

**B2.1 — Range is an EndurantType:**
$$\top \sqsubseteq \forall\,\text{concernsQualityType}.\text{EndurantType}$$

**B2.2 — Range is a subclass of Quality:**
$$\top \sqsubseteq \forall\,\text{concernsQualityType}.(\text{EndurantType} \sqcap \exists\,\text{rdfs:subClassOf}^+.\text{Quality})$$

**B2.3 — Domain:**
$$\exists\,\text{concernsQualityType}.\top \sqsubseteq \text{QualityValueAttributionSituation}$$

**B2.4 — Upper bound:**
$$\text{QualityValueAttributionSituation} \sqsubseteq \leq 1\,\text{concernsQualityType}.\text{EndurantType}$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:concernsQualityType-objects-shape
    a sh:NodeShape ;
    sh:message "The object of gufo:concernsQualityType must be an EndurantType that subclasses gufo:Quality ( https://nemo-ufes.github.io/gufo/#concernsQualityType )."@en ;
    sh:class gufo:EndurantType ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:property [
        a sh:PropertyShape ;
        sh:hasValue gufo:Quality ;
        sh:message "The object of gufo:concernsQualityType must be a subclass of gufo:Quality."@en ;
        sh:path [ sh:oneOrMorePath rdfs:subClassOf ] ;
    ] ;
    sh:targetObjectsOf gufo:concernsQualityType ;
    .

sh-gufo:concernsQualityType-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:QualityValueAttributionSituation ;
    sh:property [
        a sh:PropertyShape ;
        sh:maxCount "1"^^xsd:integer ;
        sh:path gufo:concernsQualityType ;
    ] ;
    sh:targetSubjectsOf gufo:concernsQualityType ;
    .
```

**Success test (`tests/exemplars.ttl`):**
```turtle
kb:QualityType-3a0ff32d-9743-46e4-bdcd-e86777f98551
    a gufo:Kind , owl:Class ;
    rdfs:subClassOf gufo:Quality ;
    rdfs:seeAlso sh-gufo:concernsQualityType-objects-shape ;
    .
```

**Failure test (`tests/exemplars_XFAIL.ttl`) — B2.2:**
```turtle
kb:Kind-1e2f9a0b-3c4d-4e1f-7a8b-9c0d1e2f3a4b
    a gufo:Kind , owl:Class ;
    rdfs:subClassOf gufo:Object ;
    rdfs:comment "This node is expected to trigger a validation error for being used as the object of gufo:concernsQualityType while not being a subclass of gufo:Quality."@en ;
    rdfs:seeAlso sh-gufo:concernsQualityType-objects-shape ;
    .

kb:QualityValueAttributionSituation-1e2f0a1b-4d5e-4f2a-8b9c-0d1e2f3a4b5c
    a gufo:QualityValueAttributionSituation ;
    gufo:concernsQualityValue "" ;
    gufo:concernsQualityType kb:Kind-1e2f9a0b-3c4d-4e1f-7a8b-9c0d1e2f3a4b ;
    rdfs:comment "This node uses a non-Quality EndurantType as gufo:concernsQualityType, which is expected to trigger a validation error."@en ;
    rdfs:seeAlso sh-gufo:concernsQualityType-objects-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_concerns_quality_type_range() -> None:
    """
    Verifies B2.2: the object of gufo:concernsQualityType must be an
    EndurantType that subclasses gufo:Quality. An EndurantType that
    subclasses gufo:Object must trigger a HasValueConstraintComponent
    violation on concernsQualityType-objects-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nType
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:concernsQualityType-objects-shape ;
    sh:sourceConstraintComponent sh:HasValueConstraintComponent ;
    sh:focusNode ?nType ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["Kind-1e2f9a0b-3c4d-4e1f-7a8b-9c0d1e2f3a4b"],
    }
```

---

### Rule B3 — MaterialRelationshipType Must Derive From a Subclass of gufo:Relator

#### (i) Rule Description

A `gufo:MaterialRelationshipType` represents a relationship type whose instances
are derived from a relator. According to Fonseca et al. (2019), a material
relationship type must be derived from a subclass of `gufo:Relator` — not merely
any subclass of `gufo:ExtrinsicAspect`. Using an `ExtrinsicMode` subclass as the
derivation basis for a `MaterialRelationshipType` is the *RelRig* anti-pattern
(Sales & Guizzardi, 2015), which incorrectly treats a mode-mediated relation as
a relator-mediated one.

**Sources:** Fonseca et al. (2019); Sales & Guizzardi (2015) RelRig anti-pattern;
`formatted-gufo.ttl`.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| B3.1 | Domain: subjects of `isDerivedFrom` must be a `MaterialRelationshipType` or `ComparativeRelationshipType` |
| B3.2 | Objects of `isDerivedFrom` must be an `EndurantType` subclassing `gufo:Aspect` |
| B3.3 | `ComparativeRelationshipType` derives from a subclass of `gufo:IntrinsicAspect` |
| B3.4 | `MaterialRelationshipType` derives from a subclass of `gufo:Relator` specifically |

#### (iii) DL Expressions

**B3.1 — Domain:**
$$\exists\,\text{isDerivedFrom}.\top \sqsubseteq \text{MaterialRelationshipType} \sqcup \text{ComparativeRelationshipType}$$

**B3.2 — Object subclasses Aspect:**
$$\top \sqsubseteq \forall\,\text{isDerivedFrom}.(\text{EndurantType} \sqcap \exists\,\text{rdfs:subClassOf}^+.\text{Aspect})$$

**B3.3 — ComparativeRelationshipType derives from IntrinsicAspect subclass:**
$$\text{ComparativeRelationshipType} \sqsubseteq \forall\,\text{isDerivedFrom}.(\text{EndurantType} \sqcap \exists\,\text{rdfs:subClassOf}^+.\text{IntrinsicAspect})$$

**B3.4 — MaterialRelationshipType derives from Relator subclass:**
$$\text{MaterialRelationshipType} \sqsubseteq \forall\,\text{isDerivedFrom}.(\text{EndurantType} \sqcap \exists\,\text{rdfs:subClassOf}^+.\text{Relator})$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:isDerivedFrom-MaterialRelationshipType-subjects-shape
    a sh:NodeShape ;
    rdfs:seeAlso <https://nemo-ufes.github.io/gufo/#isDerivedFrom> ;
    sh:message "gufo:MaterialRelationshipTypes should be derived from a subclass of gufo:Relator ( https://nemo-ufes.github.io/gufo/#isDerivedFrom )."@en ;
    sh:or (
        [
            a sh:NodeShape ;
            sh:not [
                a sh:NodeShape ;
                sh:class gufo:MaterialRelationshipType ;
            ] ;
        ]
        [
            a sh:NodeShape ;
            sh:property [
                a sh:PropertyShape ;
                sh:path gufo:isDerivedFrom ;
                sh:property [
                    a sh:PropertyShape ;
                    sh:hasValue gufo:Relator ;
                    sh:path [ sh:oneOrMorePath rdfs:subClassOf ] ;
                ] ;
            ] ;
        ]
    ) ;
    sh:targetSubjectsOf gufo:isDerivedFrom ;
    .
```

**Success tests (`tests/exemplars.ttl`):**
```turtle
kb:MaterialRelationshipType-2133b940-8a06-4856-bf46-684592243af4
    a owl:ObjectProperty , gufo:MaterialRelationshipType ;
    gufo:isDerivedFrom kb:EndurantType-959b6cff-b5a4-4168-be1f-d66d0c8033d6 ;
    rdfs:seeAlso
        sh-gufo:isDerivedFrom-MaterialRelationshipType-subjects-shape ,
        sh-gufo:isDerivedFrom-subjects-shape ;
    .

kb:EndurantType-959b6cff-b5a4-4168-be1f-d66d0c8033d6
    a gufo:Kind , owl:Class ;
    rdfs:subClassOf gufo:Relator ;
    rdfs:seeAlso
        sh-gufo:isDerivedFrom-MaterialRelationshipType-subjects-shape ,
        sh-gufo:isDerivedFrom-objects-shape ;
    .
```

**Failure tests (`tests/exemplars_XFAIL.ttl`) — B3.4:**
```turtle
kb:EndurantType-2f3a0b1c-5e6f-4a2b-8c9d-0e1f2a3b4c5d
    a gufo:Kind , owl:Class ;
    rdfs:subClassOf gufo:ExtrinsicMode ;
    rdfs:comment "This node subclasses gufo:ExtrinsicMode (not gufo:Relator) and triggers an invalid isDerivedFrom for a MaterialRelationshipType."@en ;
    rdfs:seeAlso sh-gufo:isDerivedFrom-MaterialRelationshipType-subjects-shape ;
    .

kb:MaterialRelationshipType-3a4b1c2d-6f7a-4b3c-9d0e-1f2a3b4c5d6e
    a owl:ObjectProperty , gufo:MaterialRelationshipType ;
    gufo:isDerivedFrom kb:EndurantType-2f3a0b1c-5e6f-4a2b-8c9d-0e1f2a3b4c5d ;
    rdfs:comment "This node is expected to trigger a validation error for deriving from a subclass of gufo:ExtrinsicMode rather than gufo:Relator."@en ;
    rdfs:seeAlso sh-gufo:isDerivedFrom-MaterialRelationshipType-subjects-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_material_relationship_type_relator() -> None:
    """
    Verifies B3.4: a gufo:MaterialRelationshipType must derive from a subclass
    of gufo:Relator. Derivation from a subclass of gufo:ExtrinsicMode must
    trigger an OrConstraintComponent violation on
    isDerivedFrom-MaterialRelationshipType-subjects-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nRelType
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:isDerivedFrom-MaterialRelationshipType-subjects-shape ;
    sh:sourceConstraintComponent sh:OrConstraintComponent ;
    sh:focusNode ?nRelType ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["MaterialRelationshipType-3a4b1c2d-6f7a-4b3c-9d0e-1f2a3b4c5d6e"],
    }
```

---

### Rule C1 — EndurantType Satisfies Two Independent Exclusivity Constraints

#### (i) Rule Description

Every `gufo:EndurantType` must satisfy two independent exclusive disjunctions
simultaneously: it must be exactly one of `NonRigidType` or `RigidType` (the
rigidity partition), and exactly one of `NonSortal` or `Sortal` (the sortality
partition). In SHACL these are expressed as two separate `sh:xone` constraints
on the same shape node. Because SHACL conjoins multiple property values on a
node shape, both constraints must be satisfied independently — this is not a
single disjunction but a conjunction of two exclusive disjunctions.

**Sources:** Guizzardi et al. (2018); `formatted-gufo.ttl`
`owl:disjointUnionOf` on `EndurantType`.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| C1.1 | Every `EndurantType` is exactly one of `NonRigidType` or `RigidType` |
| C1.2 | Every `EndurantType` is exactly one of `NonSortal` or `Sortal` |

#### (iii) DL Expressions

**C1.1 — Rigidity partition:**
$$\text{EndurantType} \sqsubseteq \bigoplus\{\text{NonRigidType},\ \text{RigidType}\}$$

**C1.2 — Sortality partition:**
$$\text{EndurantType} \sqsubseteq \bigoplus\{\text{NonSortal},\ \text{Sortal}\}$$

**Combined — both must hold independently:**
$$\text{EndurantType} \sqsubseteq \bigoplus\{\text{NonRigidType},\ \text{RigidType}\}\ \sqcap\ \bigoplus\{\text{NonSortal},\ \text{Sortal}\}$$

#### (iv) Implementation

**SHACL shape:**

```turtle
sh-gufo:EndurantType-shape
    a sh:NodeShape ;
    rdfs:comment "This shape applies two independent sh:xone constraints. The first requires every EndurantType to be exactly one of (NonRigidType, RigidType). The second requires every EndurantType to be exactly one of (NonSortal, Sortal). Both constraints must hold simultaneously and independently — this is a conjunction of two exclusive disjunctions, not a single disjunction."@en ;
    sh:targetClass gufo:EndurantType ;
    sh:xone
        (
            [ a sh:NodeShape ; sh:class gufo:NonRigidType ; ]
            [ a sh:NodeShape ; sh:class gufo:RigidType ; ]
        ) ,
        (
            [ a sh:NodeShape ; sh:class gufo:NonSortal ; ]
            [ a sh:NodeShape ; sh:class gufo:Sortal ; ]
        )
        ;
    .
```

**Success test (`tests/exemplars.ttl`):**

Any `EndurantType` exemplar satisfies this shape; for example, `gufo:Category`
is a `RigidType` and a `NonSortal`, satisfying both `sh:xone` constraints:
```turtle
kb:EndurantType-1e1f2313-7cbb-47ae-bdd0-bc4a4a5a654e
    a gufo:Category , owl:Class ;
    gufo:hasAssociatedQualityValueType kb:AbstractIndividualType-73fdd434-b356-4b08-8ad6-e112a8727e61 ;
    rdfs:seeAlso sh-gufo:hasAssociatedQualityValueType-subjects-shape ;
    .
```

**Failure test (`tests/exemplars_XFAIL.ttl`):**
```turtle
kb:EndurantType-f6898a59-a3ec-4ed9-9b1d-0cd9a19d2663
    a gufo:EndurantType , owl:Class ;
    rdfs:comment "This is expected to trigger a validation error for not satisfying the disjoint-union, exactly-one clauses in EndurantType review."@en ;
    rdfs:seeAlso sh-gufo:EndurantType-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_enduranttype() -> None:
    """
    Verifies C1.1 and C1.2: every gufo:EndurantType must be exactly one of
    (NonRigidType, RigidType) and exactly one of (NonSortal, Sortal).
    A bare EndurantType without any subtype must trigger an
    XoneConstraintComponent violation on EndurantType-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nEndurantType
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:EndurantType-shape ;
    sh:sourceConstraintComponent sh:XoneConstraintComponent ;
    sh:focusNode ?nEndurantType ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["EndurantType-f6898a59-a3ec-4ed9-9b1d-0cd9a19d2663"],
    }
```

---

### Rule D1 — QualityValueAttributionSituation Must Be Used by Exactly One Endurant

#### (i) Rule Description

A `gufo:QualityValueAttributionSituation` must be linked to exactly one
`gufo:Endurant` via the inverse of `gufo:standsInQualifiedAttribution`. The
gUFO OWL implementation declares `owl:qualifiedCardinality "1"` on this inverse
path, expressing that the situation must be referenced by exactly one endurant
— neither zero nor more than one.

**Sources:** `formatted-gufo.ttl` `owl:qualifiedCardinality "1"` on inverse of
`standsInQualifiedAttribution`.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| D1.1 | Upper bound: at most one `Endurant` uses this situation via `standsInQualifiedAttribution` |
| D1.2 | Lower bound: at least one `Endurant` must use this situation |
| D1.3 | Domain of `standsInQualifiedAttribution`: subject must be an `Endurant` |
| D1.4 | Range of `standsInQualifiedAttribution`: object must be a `QualityValueAttributionSituation` |

#### (iii) DL Expressions

**D1.1 — Upper bound:**
$$\text{QVAS} \sqsubseteq \leq 1\,\text{standsInQualifiedAttribution}^-.\text{Endurant}$$

**D1.2 — Lower bound:**
$$\text{QVAS} \sqsubseteq \geq 1\,\text{standsInQualifiedAttribution}^-.\top$$

**D1.3 — Domain:**
$$\exists\,\text{standsInQualifiedAttribution}.\top \sqsubseteq \text{Endurant}$$

**D1.4 — Range:**
$$\top \sqsubseteq \forall\,\text{standsInQualifiedAttribution}.\text{QVAS}$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:QualityValueAttributionSituation-shape
    a sh:NodeShape ;
    ...
    sh:property
        ...
        [
            a sh:PropertyShape ;
            sh:message "Every gufo:QualityValueAttributionSituation must be used by at least one Endurant via gufo:standsInQualifiedAttribution."@en ;
            sh:path [ sh:inversePath gufo:standsInQualifiedAttribution ] ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedMinCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Endurant ;
            ] ;
        ] ;
    sh:targetClass gufo:QualityValueAttributionSituation ;
    .

sh-gufo:standsInQualifiedAttribution-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:Endurant ;
    sh:targetSubjectsOf gufo:standsInQualifiedAttribution ;
    .

sh-gufo:standsInQualifiedAttribution-objects-shape
    a sh:NodeShape ;
    sh:class gufo:QualityValueAttributionSituation ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:targetObjectsOf gufo:standsInQualifiedAttribution ;
    .
```

**Success tests (`tests/exemplars.ttl`):**
```turtle
kb:Endurant-30842dd2-146e-4720-81eb-ff8f655058a5
    a gufo:Object ;
    gufo:standsInQualifiedAttribution kb:QualityValueAttributionSituation-71781915-ac36-4264-83f4-3a89df7de700 ;
    rdfs:seeAlso sh-gufo:standsInQualifiedAttribution-subjects-shape ;
    .

kb:QualityValueAttributionSituation-71781915-ac36-4264-83f4-3a89df7de700
    a gufo:QualityValueAttributionSituation ;
    rdfs:seeAlso sh-gufo:standsInQualifiedAttribution-objects-shape ;
    .
```

**Failure test (`tests/exemplars_XFAIL.ttl`) — D1.2:**
```turtle
kb:QualityValueAttributionSituation-2f3a1b2c-5d6e-4f3a-9b0c-1d2e3f4a5b6c
    a gufo:QualityValueAttributionSituation ;
    gufo:concernsQualityValue "" ;
    rdfs:comment "This node is expected to trigger a validation error for being a gufo:QualityValueAttributionSituation not referenced by any Endurant via gufo:standsInQualifiedAttribution."@en ;
    rdfs:seeAlso sh-gufo:QualityValueAttributionSituation-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_quality_value_attribution_stands_in() -> None:
    """
    Verifies D1.2: every gufo:QualityValueAttributionSituation must be
    referenced by at least one Endurant via gufo:standsInQualifiedAttribution
    (sh:qualifiedMinCount 1 on inverse path). A QVAS with no such reference
    must trigger a QualifiedMinCountConstraintComponent violation on
    QualityValueAttributionSituation-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nSituation
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:QualityValueAttributionSituation-shape ;
    sh:sourceConstraintComponent sh:QualifiedMinCountConstraintComponent ;
    sh:focusNode ?nSituation ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["QualityValueAttributionSituation-2f3a1b2c-5d6e-4f3a-9b0c-1d2e3f4a5b6c"],
    }
```

---

### Rule D2 — TemporaryRelationshipSituation Must Be Used by Exactly One Endurant

#### (i) Rule Description

A `gufo:TemporaryRelationshipSituation` must be linked to exactly one
`gufo:Endurant` via the inverse of `gufo:standsInQualifiedRelationship`. The
gUFO OWL implementation declares `owl:qualifiedCardinality "1"` on this inverse
path.

**Sources:** `formatted-gufo.ttl` `owl:qualifiedCardinality "1"` on inverse of
`standsInQualifiedRelationship`.

#### (ii) Test Aspects

| ID | Aspect |
|---|---|
| D2.1 | Upper bound: at most one `Endurant` uses this situation via `standsInQualifiedRelationship` |
| D2.2 | Lower bound: at least one `Endurant` must use this situation |
| D2.3 | Domain of `standsInQualifiedRelationship`: subject must be an `Endurant` |
| D2.4 | Range of `standsInQualifiedRelationship`: object must be a `TemporaryRelationshipSituation` |

#### (iii) DL Expressions

**D2.1 — Upper bound:**
$$\text{TemporaryRelationshipSituation} \sqsubseteq \leq 1\,\text{standsInQualifiedRelationship}^-.\text{Endurant}$$

**D2.2 — Lower bound:**
$$\text{TemporaryRelationshipSituation} \sqsubseteq \geq 1\,\text{standsInQualifiedRelationship}^-.\top$$

**D2.3 — Domain:**
$$\exists\,\text{standsInQualifiedRelationship}.\top \sqsubseteq \text{Endurant}$$

**D2.4 — Range:**
$$\top \sqsubseteq \forall\,\text{standsInQualifiedRelationship}.\text{TemporaryRelationshipSituation}$$

#### (iv) Implementation

**SHACL shapes:**

```turtle
sh-gufo:TemporaryRelationshipSituation-shape
    a sh:NodeShape ;
    sh:property
        [
            a sh:PropertyShape ;
            sh:message "Every gufo:TemporaryRelationshipSituation must be referenced by at least one Endurant via gufo:standsInQualifiedRelationship."@en ;
            sh:path [ sh:inversePath gufo:standsInQualifiedRelationship ] ;
            sh:qualifiedMaxCount "1"^^xsd:integer ;
            sh:qualifiedMinCount "1"^^xsd:integer ;
            sh:qualifiedValueShape [
                a sh:NodeShape ;
                sh:class gufo:Endurant ;
            ] ;
        ] ;
    sh:targetClass gufo:TemporaryRelationshipSituation ;
    .

sh-gufo:standsInQualifiedRelationship-subjects-shape
    a sh:NodeShape ;
    sh:class gufo:Endurant ;
    sh:targetSubjectsOf gufo:standsInQualifiedRelationship ;
    .

sh-gufo:standsInQualifiedRelationship-objects-shape
    a sh:NodeShape ;
    sh:class gufo:TemporaryRelationshipSituation ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:targetObjectsOf gufo:standsInQualifiedRelationship ;
    .
```

**Success tests (`tests/exemplars.ttl`):**
```turtle
kb:Endurant-c38ea234-5d65-40d2-9ce6-9ca9d070a3e6
    a gufo:Object ;
    gufo:standsInQualifiedRelationship kb:TemporaryRelationshipSituation-29301400-6b45-4176-b570-f52c28cd2789 ;
    rdfs:seeAlso sh-gufo:standsInQualifiedRelationship-subjects-shape ;
    .

kb:TemporaryRelationshipSituation-29301400-6b45-4176-b570-f52c28cd2789
    a gufo:TemporaryRelationshipSituation ;
    rdfs:seeAlso sh-gufo:standsInQualifiedRelationship-objects-shape ;
    .
```

**Failure test (`tests/exemplars_XFAIL.ttl`) — D2.1 and D2.2:**
```turtle
kb:TemporaryRelationshipSituation-4b5c2d3e-7f8a-4c4b-0d1e-2f3a4b5c6d7e
    a gufo:TemporaryRelationshipSituation ;
    gufo:concernsRelationshipType kb:RelationshipType-0813ed87-2f47-4a1b-a063-834b467c3d31 ;
    gufo:concernsRelatedEndurant kb:Endurant-7ac20c26-1f62-40c1-a6e0-0e96fb088e9b ;
    rdfs:comment "This node is expected to trigger a validation error for being a gufo:TemporaryRelationshipSituation not referenced by any Endurant via gufo:standsInQualifiedRelationship."@en ;
    rdfs:seeAlso sh-gufo:TemporaryRelationshipSituation-shape ;
    .
```

**pytest (`tests/test_exemplar_coverage.py`):**
```python
def test_exemplar_xfail_validation_temporary_relationship_situation_stands_in() -> None:
    """
    Verifies D2.1 and D2.2: every gufo:TemporaryRelationshipSituation must be
    referenced by exactly one Endurant via gufo:standsInQualifiedRelationship
    (qualifiedMinCount 1 and qualifiedMaxCount 1 on inverse path). A
    TemporaryRelationshipSituation with no such reference must trigger a
    QualifiedMinCountConstraintComponent violation on
    TemporaryRelationshipSituation-shape.
    """
    validation_graph = Graph()
    validation_graph.parse("exemplars_XFAIL_validation.ttl")

    ns_kb = Namespace("http://example.org/kb/")

    n_focus_nodes: Set[URIRef] = set()
    for result in validation_graph.query("""\
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX sh-gufo: <http://example.org/shapes/sh-gufo/>
SELECT ?nSituation
WHERE {
  ?nValidationResult
    a sh:ValidationResult ;
    sh:sourceShape sh-gufo:TemporaryRelationshipSituation-shape ;
    sh:sourceConstraintComponent sh:QualifiedMinCountConstraintComponent ;
    sh:focusNode ?nSituation ;
    .
}
"""):
        assert isinstance(result, ResultRow)
        assert isinstance(result[0], URIRef)
        n_focus_nodes.add(result[0])

    assert n_focus_nodes == {
        ns_kb["TemporaryRelationshipSituation-4b5c2d3e-7f8a-4c4b-0d1e-2f3a4b5c6d7e"],
    }
```

---

## 6. Summary of Rules and Test Aspects

| Rule | Description | Test aspects |
|---|---|---|
| A1 | Every Aspect inheres in exactly one ConcreteIndividual | 4 |
| A2 | Every ExtrinsicMode has at least one externallyDependsOn | 3 |
| A3 | TemporaryConstitutionSituation has exactly one concernsConstitutedEndurant | 5 |
| A4 | TemporaryInstantiationSituation has exactly one concernsNonRigidType | 5 |
| A5 | TemporaryParthoodSituation has exactly one concernsTemporaryWhole | 5 |
| A6 | TemporaryRelationshipSituation has one RelationshipType and at least one Endurant | 9 |
| B1 | QualityValueAttributionSituation uses exactly one quality value pattern | 8 |
| B2 | concernsQualityType range is a subclass of gufo:Quality | 4 |
| B3 | MaterialRelationshipType derives from a subclass of gufo:Relator | 4 |
| C1 | EndurantType satisfies two independent rigidity and sortality partitions | 2 |
| D1 | QualityValueAttributionSituation is used by exactly one Endurant | 4 |
| D2 | TemporaryRelationshipSituation is used by exactly one Endurant | 4 |
| **Total** | | **57** |
