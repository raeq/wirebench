# Circuit Component Modelling Framework

## 1. Overview

This document specifies a mathematical framework for modelling electronic and
multi-physics circuits as constraint graphs. The framework supports structural
validation, passive component inference, dynamic simulation, and hierarchical
composition. It is grounded in the same primitives as Modified Nodal Analysis
and extends to multi-domain systems through a bond-graph foundation.

---

## 2. Scope

The framework covers electrical circuits fully and extends to mechanical, thermal,
hydraulic, and optical domains through coupling factor nodes. The bond-graph correspondence
(Section 13) is not an add-on but a structural commitment: junction nodes, storage
elements with state, and coupling factor nodes are bond-graph primitives in domain-neutral
form. This commitment is made explicitly because the isolation barrier model
(Section 9) admits magnetic, optical, and thermal coupling factor nodes as first-class elements,
and a framework that handles these coupling types without a multi-domain foundation
would be incomplete.

---

## 3. Primitives

Three primitives constitute the complete kernel. Coupling edges — connections spanning ground-domain boundaries — are a subclass of factor node, distinguished by their endpoint domains rather than by a separate primitive.

**Kirchhoff junction node** — a point in the circuit with an associated potential
variable. KCL holds at every junction unconditionally: the algebraic sum of all
currents at the node is zero (ΣI = 0). Voltage is the potential difference between
two nodes in the same ground domain. Direction (input/output/bidirectional) is not
a fundamental property of junction nodes; it is an advisory hint that enables fast
structural pre-checking but carries no formal weight.

**Factor node** — a constraint relating the potentials and flows at two or more
junction nodes. Every constraint in the circuit — KCL at each junction, constitutive
relations for every component, and coupling across domain boundaries — is a factor
node. Factor nodes are algebraic (no state) or differential (with internal state).

The circuit-diagram convention of drawing a component as an *edge* between two
junction nodes is a notational shorthand: a two-terminal factor node connecting
exactly two junction potentials and one branch current. For multi-terminal components
(transistor, op-amp) where one port's behaviour depends on another's, the factor node
cannot be drawn as a simple edge and must be stated explicitly. The two forms are
equivalent representations of the same constraint content; factor node is primary.

**Ground domain tag** — every junction node belongs to exactly one ground domain.
Voltage is only well-defined between nodes in the same domain. Cross-domain potential
comparison is structurally invalid.

A **coupling factor node** is a factor node whose endpoints span ground domains. It
expresses a constitutive relation across an isolation barrier — transformer turns ratio,
optocoupler current transfer ratio, thermal conductance — using the same formalism as
any other factor node. No direct electrical current crosses the boundary; this follows
from KCL being domain-local rather than from a separate primitive. DC blocking is a
property of the coupling factor's constitutive function, not of the edge type.

---

## 4. Consolidated Axioms

**A1 — Node**: every terminal is a Kirchhoff junction node. KCL holds at every
node unconditionally and universally.

**A2 — Ground domain**: every node belongs to exactly one ground domain.
Cross-domain voltage comparison is invalid by construction.

**A3 — Edge**: every edge carries a constitutive relation. The relation is algebraic,
or differential (with state). Coupling factor nodes span ground domains. KCL and
KVL follow from topology; all other constraints are per-edge.

**A4 — Connectivity**: every node must participate in at least one constitutive
relation. An isolated node is a structural error.

**A5 — Power**: components whose interface declares external-power-required ports
must have those edges connected. Power ports are junction nodes constrained by their
supply potential. Whether a component requires external power is a declared interface
property, not an inferred classification into active vs passive.

**A6 — Cardinality**: edges are mandatory or optional. An absent mandatory edge is
a structural error, detectable at wiring time.

**A7 — Isolation**: a coupling factor node has endpoints in different ground
domains. No direct electrical current crosses the boundary — this follows from
KCL being domain-local, not from a separate edge primitive.

**A8 — System boundary**: a well-formed system has power input edges (hard rule).
Absence of signal-domain input or output edges is a domain-aware warning, not an
error. A thermal-only subsystem with no electrical I/O is valid.

**A9 — Impedance compatibility**: for any junction node, a valid operating point
must exist — a (V, I) pair satisfying every factor node connected at that junction
simultaneously. When the Thévenin impedance of one connected sub-network is much
larger than another's, voltage fidelity at the junction degrades; the weaker network
cannot maintain its operating point. This is an operating-point constraint, derivable
from solving the factor graph, not a structural property verifiable at wiring time.
The direction-based shorthand — source, load, output, drive capability, fan-out —
is the hint-layer approximation used for fast pre-checking under the advisory
direction hints of A1, and carries no formal weight in the constraint model.

**A10 — Hierarchy**: a component may contain sub-components. External ports are a
designated subset of internal junction nodes. Ground domain assignments of internal
nodes must be consistent with the parent graph.

---

## 5. The Constraint Graph

The circuit is a directed graph G = (V, E) where V is the set of junction nodes
and E is the set of edges. The incidence matrix A encodes the topology.

Two classes of constraint operate within the single constraint graph, both
expressed as factor nodes:

**KCL factor nodes** — one per junction node, derived from the incidence matrix A.
Equivalent to A·i(t) = 0 globally; KVL (v = Aᵀ·e) follows by duality. These hold
universally regardless of component types.

**Constitutive factor nodes** — one or more per component, expressing the component's
physical law:

```
f_e(v_e, i_e, ẋ_e, x_e, t) = 0    for each component e
```

There is one constraint graph. The circuit-diagram representation — junction nodes
connected by edges carrying constitutive relations — is a notational shorthand for
the factor graph valid when all components are two-terminal. Section 6 uses this
shorthand; Section 8 states the general factor-node form required for multi-terminal
components. They are equivalent representations of the same constraint content.

### Graph Structure and Evaluation

G may contain cycles. Strongly Connected Components (SCCs) are identified by
Tarjan's algorithm (O(V + E)). The condensation graph — each SCC collapsed to a
single node — is always a DAG, evaluated in topological order.

Single-node SCCs evaluate in one pass. Multi-node SCCs (true feedback cycles) are
resolved by fixed-point iteration.

**Convergence axiom**: every cycle must converge. Three outcomes:

| Outcome | Interpretation | Validity |
|---|---|---|
| Fixed point | Stable memory or control | Valid |
| Periodic orbit | Oscillator | Valid if intentional |
| Non-convergence | Forbidden state or instability | Invalid |

Forbidden states surface as non-convergence naturally — no special-casing required.

---

## 6. Edge Constitutive Relations

This section presents constitutive relations in the two-terminal edge shorthand
established in Section 3, valid when a factor node connects exactly two junction
nodes. Multi-terminal factor nodes are specified in Section 8.

The edge-relation table is the complete extension point for new component types.

| Edge type | Constitutive relation | Internal state |
|---|---|---|
| Resistor | V = R·I | none |
| Capacitor | I = C·dV/dt | Q(t) = ∫I dt |
| Inductor | V = L·dI/dt | Φ(t) = ∫V dt |
| Voltage source | V = Vs(t) | none |
| Current source | I = Is(t) | none |
| Ideal wire | V = 0, I free | none |
| Open circuit | I = 0, V free | none |
| Diode | I = Is(e^(V/Vt) − 1) | none |
| Spring (mechanical) | F = k·x | x(t) = ∫v dt |
| Mass (mechanical) | F = m·dv/dt | p(t) = ∫F dt |
| Damper (mechanical) | F = b·v | none |
| Thermal resistor | Q̇ = ΔT/R_th | none |
| Thermal capacitor | Q̇ = C_th·dT/dt | E(t) = ∫Q̇ dt |
| Coupling factor node | domain-specific (turns ratio, CTR, thermal conductance) | — |

Resistors are the degenerate case with empty state. Dynamic elements (C, L, spring,
mass) have internal state. New component types are new rows. The multi-physics
entries (mechanical, thermal) are native instances of the framework, not extensions.

---

## 7. Dynamic Elements: DAE and State

### DAE Formulation

The full system is a Differential-Algebraic Equation. The constitutive relation on
each edge determines its type; the graph topology is unchanged regardless of whether
edges are algebraic or differential:

```
A·i(t) = 0                                            (KCL — topology)
v(t) = Aᵀ·e(t)                                        (KVL — topology)
f_k(v_k, i_k, ẋ_k, x_k, t) = 0   for each constitutive factor node k   (constitutive)
```

State x_e is empty for R, equals Q for C, and equals Φ (equivalently I_L) for L.

### Minimum State: Tree-Cotree Decomposition

State-space dimension is a graph property, verifiable before numerical integration
(Desoer & Kuh; Chua, Desoer, Kuh — *Linear and Nonlinear Circuits*):

1. Pick a spanning tree T of G
2. Place capacitors in T — their voltages are independent state variables
3. Place inductors in the cotree T* — their currents are independent state variables
4. dim(state) = #C + #L

Two pathological topologies reduce the count:

| Pathology | Mechanism | Effect |
|---|---|---|
| Loop of capacitors only (± voltage sources) | KVL constrains capacitor voltages | State − 1 per loop |
| Cutset of inductors only (± current sources) | KCL constrains inductor currents | State − 1 per cutset |

Both are detected by graph algorithms before simulation. State rank is a static
structural property.

### Companion Models for Numerical Simulation

With backward Euler at timestep Δt, dynamic edges become Norton equivalents:

```
Capacitor C  →  conductance C/Δt  ∥  current source (C/Δt)·V_prev
Inductor L   →  conductance Δt/L  ∥  current source I_prev
```

The per-timestep problem is a resistive network solvable by standard MNA. All
dynamics live in the iterative update of companion sources between steps.
Trapezoidal rule gives better accuracy at moderate additional cost.

---

## 8. Multi-Terminal Factor Nodes

All component constraints are factor nodes (Section 3). For two-terminal components
the factor node reduces to the edge shorthand of Section 6. For multi-terminal
components — controlled sources, differential pairs — the factor node connects three
or more variable nodes and cannot be drawn as a simple edge. This section specifies
that case.

The factor graph structure:

- **Variable nodes**: potential and flow variables at each junction
- **Factor nodes**: functions relating those variables — including KCL, constitutive
  relations, and coupling

| Component | Factor nodes |
|---|---|
| Resistor | Va − Vb = I·R |
| BJT | Ic = β·Ib ; Ie = Ib + Ic |
| Op-amp (ideal) | Vout = A(V+ − V−) |
| KCL at junction | ΣI = 0 |

The op-amp differential pair — where V+ and V− jointly determine Vout — is a
single factor node connecting three variable nodes. No special port classification
is required.

### Algebraic and Differential Factor Nodes

Algebraic factor nodes are standard. For dynamic elements, the constitutive
relation is differential. Two approaches are available; the choice is open:

**Time-discretisation**: replace dV/dt with (V[t] − V[t−1])/Δt. The factor
becomes algebraic per timestep, consistent with the companion model approach.
Continuous-time analyticity is lost.

**First-class differential factor node**: extend the factor node type to include
differential operators. Continuous-time formulation is preserved at the cost of a
more complex solver.

The DAE formulation (Section 7) resolves dynamic elements for the
topology-and-constitutive view. For the factor-graph view, the above choice
is an open problem.

---

## 9. Isolation Barriers and Ground Domains

An isolation barrier terminates electrical current flow on both sides. In graph terms:

- A **sink terminal** on the primary side — current enters, does not leave electrically
- A **source terminal** on the secondary side — current originates without upstream electrical path

The two terminals are connected by a **coupling factor node** with typed properties:

| Mechanism | Coupling type | Frequency constraint | Passes DC? |
|---|---|---|---|
| Transformer | Magnetic | Upper limit (core saturation) | No |
| Optocoupler | Optical | LED and detector bandwidth | No |
| Capacitive isolation | Electric field | Lower cutoff (blocks DC) | No |
| Piezoelectric | Mechanical | Resonant frequency | No |

DC blocking is a property of the coupling factor's constitutive function: it is a
hard constraint, not a consequence of a particular mechanism.

**Isolation voltage rating**: the maximum potential difference between ground domains
before dielectric breakdown. A property of the coupling factor node.

**Ground domain rules**:
- All nodes in a domain share a voltage reference
- Coupling factor nodes are the only valid connections between domains
- Cross-domain voltage comparison in the constraint solver is invalid by construction

---

## 10. Hierarchical Composition

Hierarchy allows a sub-circuit to present as a single component in a parent graph.

**Port exposure**: a sub-circuit designates a subset of its internal junction nodes
as external ports. All remaining nodes are hidden. The external interface is a typed
list of (node, domain, cardinality) triples. The interface is the only valid
interaction point between the sub-circuit and its parent.

**Parametric instantiation**: a component type may be parameterised by port count
(AND-n gate, where n is a parameter) or by component values (resistor with
parameter R). The type system must support parameterised port lists and typed
parameters. Instantiation binds parameters to values and resolves the port list
before structural validation.

**SCC collapsing**: a cyclic sub-circuit may be abstracted as a single node in
specific tractable cases:

- *Linear SCCs*: state-space reduction yields an (A, B, C, D) model or transfer
  function; always computable for well-posed linear systems.
- *Finite-state discrete SCCs*: abstraction to a state-machine interface is feasible
  when the state space is finite and transitions are deterministic. The SR latch is
  this case — it abstracts to three states (Set, Reset, Hold) with defined transition
  rules, not to a continuous constitutive relation.

For general non-linear SCCs (non-linear feedback, analog oscillators) and hybrid
SCCs (switching circuits, mixed discrete/continuous), symbolic elimination of internal
variables to yield a closed-form external constitutive relation is not generally
feasible. Abstraction must rely on simulation-based characterisation, manual derivation
for specific topologies, or formal verification methods that confirm behavioural
equivalence without producing a closed form. This is an open problem; see Section 15.

**Cross-hierarchy ground-domain rules**:
- A sub-circuit may not introduce a new ground domain without an explicit isolation
  barrier (coupling factor node) declared at its external interface
- Ground domain tags must be consistent across all levels of the hierarchy
- An isolation barrier crossing a hierarchy boundary must appear in the sub-circuit's
  port list

**Validation at composition time**:
- All mandatory ports of the sub-circuit must be connected in the parent
- Ground domain assignments must be consistent with the parent graph
- Fan-out and impedance constraints (A9) must hold at the interface boundary

---

## 11. System Boundary

**Power** (hard rule, A5): every system has power input edges. A component with
declared power-required ports but unconnected power edges is a structural error unconditionally.

**Signal I/O** (soft rules, domain-aware):
- No signal-domain input edges: warning — system may not respond to external conditions
  (controllability concern within that domain)
- No signal-domain output edges: warning — system may produce no observable effect
  in that domain (observability concern)

Checks are per-domain. A heat sink has thermal-domain edges and no electrical
signal I/O; it is not a modelling error. A self-oscillating circuit has no external
signal input; it is valid if intentional. Both soft rules may be suppressed by
explicit declaration of intent.

---

## 12. Inference Layer

### Problem Formulation

Passive component inference is an unsatisfiability problem: given a partially
connected constraint graph where some connections are missing or domain-incompatible,
find the minimum set of factor nodes whose insertion restores local satisfiability.

This replaces direction-based range-table inference, which assumed directed signal
flow incompatible with the Kirchhoff junction model.

The minimum-cardinality formulation is NP-hard in general. Practical inference
does not search this space directly. Three mechanisms together reduce it to a
tractable procedure for well-typed circuits:

1. **Domain-typed pattern matching** — the domain pair (source domain, target domain)
   maps to a candidate component class via a lookup table. The domain type system
   prunes what is in general a search problem to a table lookup for well-typed
   circuits. Domain inference does not require enumeration.

2. **Algebraic value derivation** — once a component class is identified, parameter
   values are computed by solving the constitutive relation with port ranges as
   boundary conditions. This is a small algebraic system, not a search.

3. **Heuristic selection among candidates** — when multiple component classes could
   satisfy the constraint (shunt resistor vs transimpedance amplifier for
   current-to-voltage), selection is guided by preference ordering: passive over
   active, minimum component count, then power/cost/area budgets.

The hard combinatorial core — optimal selection over a large candidate space under
global constraints — is not addressed here and is listed as an open problem in
Section 15.

### Domain Inference

When two nodes of incompatible domains must be connected, the constraint system
between them is unsatisfiable. The required factor-node class is determined by the domain pair. In this table,
"from" and "to" refer to information flow at the inference layer — the domain of
the signal as available and the domain required by the receiving component —
not to electrical direction, which the framework has demoted to advisory status.

| From domain | To domain | Inferred component class |
|---|---|---|
| Current (high impedance source) | Voltage | Shunt resistor (passive, V = I·R) |
| Current (low impedance / precision) | Voltage | Transimpedance amplifier (active) |
| Analog | Digital | Comparator |
| High voltage analog | Low voltage analog | Resistor divider or linear regulator |
| Electrical | Mechanical | Actuator or transducer (coupling factor node) |
| Electrical | Thermal | Resistive heater (coupling factor node) |

The shunt resistor and transimpedance amplifier are both valid current-to-voltage
conversions. A shunt resistor develops a voltage as a byproduct of current flowing
through it; the conversion is in the measurement. A transimpedance amplifier actively
converts current to voltage with gain and input isolation. Which is inferred depends
on source impedance, required bandwidth, gain, and power constraints.

### Value Derivation

Given a component class and boundary conditions from port ranges, parameter values
follow from the constitutive relation:

- Shunt resistor: R = V_required / I_source
- Current-limiting resistor: R = (V_supply − V_forward) / I_desired
- Voltage divider ratio: R1/R2 = (V_in / V_out) − 1

For non-linear components (diodes, transistors), value derivation requires a known
operating point. Newton-Raphson convergence to the operating point must precede
inference. The companion model framework provides the computational structure.

### Power Envelope

Given voltage and current ranges on a port:
- P_max = V_max × I_max — worst-case instantaneous power
- P_avg — from signal waveform; governs thermal dissipation

**Component rating check**: P_max must not exceed the component's power rating.
**System power budget**: sum of all demands must not exceed supply rating.
Both checks operate on range properties and require no simulation.

### Topology-Dependent Safety Rules

Some hazards require graph-pattern matching rather than range analysis:

**Inductor flyback**: an inductive edge (L) in series with a switching element.
V = L·dI/dt with a suddenly interrupted current produces a voltage spike
potentially orders of magnitude above the supply rail. Flag: flyback protection
required. Protective component: flyback diode across the inductive load.

**C-only loops**: detected by tree-cotree analysis before simulation.
Flag: state rank reduced; initialisation constraints required.

**L-only cutsets**: detected by tree-cotree analysis before simulation.
Flag: state rank reduced; initialisation constraints required.

These rules form a separate inference pass over graph topology and component-type
tags, operating above the constraint solver.

---

## 13. Multi-Physics Foundation: Bond Graphs

The framework is structurally a bond graph. The correspondence is exact:

Per-domain effort/flow assignments: electrical — voltage is effort, current is flow;
mechanical — force is effort, velocity is flow; thermal — temperature is effort,
heat flux is flow. These fix the standard convention throughout the table.

| Framework element | Bond graph element |
|---|---|
| Kirchhoff junction (shared potential) | 0-junction |
| KVL loop node (shared flow) | 1-junction |
| Capacitor / spring | C-element (effort storage) |
| Inductor / mass | I-element (flow storage) |
| Resistor / damper | R-element (dissipation) |
| Coupling factor node | Bond across energy domains |
| Voltage source | Se-element |
| Current source | Sf-element |

Port-Hamiltonian theory provides the coordinate-free generalisation: the Dirac
structure encodes the power-conserving interconnection, and the Hamiltonian encodes
stored energy. This is the appropriate foundation for formal stability proofs and
for circuits where energy bookkeeping across domains must be exact.

The bond-graph commitment means mechanical, hydraulic, and thermal subsystems are
native instances of the framework — not domain-specific extensions. Dynamic state
(Section 7), inter-port dependency (Section 8), and multi-domain coupling (Section 9)
are unified under the single primitive set rather than resolved independently.

---

## 14. Relationship to Existing Tools

| Tool or method | Correspondence |
|---|---|
| SPICE / MNA | Kirchhoff junctions + constitutive relations + companion models; electrical-only |
| VHDL / Verilog | Hierarchical composition with typed ports; structural DRC; digital domain |
| Tarjan SCC algorithm | Evaluation order determination; abstraction boundary detection |
| EDA design rule checking | Structural axioms A1–A10; power, fan-out, and domain rules |
| Bond graphs (Paynter, Karnopp) | Complete multi-domain correspondence; Section 13 |
| Port-Hamiltonian systems | Formal energy-balance and stability foundation |

The primary contribution beyond a raw netlist or MNA formulation is the
**inference layer**: given port domain and range specifications, the framework
identifies missing components, their classes, derivable parameter values, power
ratings, and topology-dependent safety hazards — before simulation.

---

## 15. Open Problems

**Differential factor nodes**: the factor-graph treatment of dynamic elements
requires either time-discretisation (consistent with companion models, loses
continuous-time analytics) or a first-class differential factor node type (preserves
continuous-time formulation, increases solver complexity). This choice is unresolved.

**Non-linear operating point for inference**: inference for non-linear components
requires operating point convergence before value derivation proceeds. The algorithm
— initial linearisation followed by Newton-Raphson refinement — is standard but is
not yet specified as a formal part of the inference procedure.

**Topology-dependent safety rule completeness**: flyback and pathological-topology
rules are instances of a larger class of graph-pattern safety checks. A complete
rule catalogue and the algorithm for applying them is not yet specified.

**Hierarchical composition type system**: the axioms for port exposure, parametric
instantiation, and cross-hierarchy ground-domain rules (Section 10) are stated
informally. A formal type system for component interfaces — covering parameterised
port lists, domain constraints, and composition validity rules — is required for a
complete specification.

**Validation against SPICE and DRC**: for the class of circuits where both apply
(linear time-invariant, single ground domain, no coupling factor nodes), the framework
should provably agree with SPICE and formal DRC. The agreement class and its
boundaries are not yet formally characterised.

**General SCC abstraction**: computing a closed-form external constitutive relation
for a cyclic sub-circuit is feasible for linear systems (state-space reduction) and
finite-state discrete systems (state-machine abstraction). For non-linear SCCs and
hybrid SCCs, no general algorithm exists. The SR latch example is tractable because
its abstraction target is a finite-state machine, not a continuous relation — this
should not be taken as evidence that the general case is tractable.

**Optimal component inference**: the minimum-cardinality satisfiability formulation
of component inference is NP-hard in general. Practical inference is tractable for
well-typed circuits through domain-typed pattern matching and algebraic value
derivation, as described in Section 12. Finding a globally optimal insertion set
under multi-objective constraints — minimum component count, power budget, cost,
area — is not addressed and has no known polynomial-time algorithm in the general
case.

---

## 16. Mechanisation via Formal Methods

The framework stratifies into three layers with distinct mechanisation tractability.
The structural layer is immediately amenable to proof-assistant formalisation; the
continuous-mathematics layer is achievable with significant effort; the non-linear
and inference layers are out of scope for current mechanisation.

### Layer 1 — Structural and Type-Theoretic (High Tractability)

The axioms A1–A10, the graph structure, SCC decomposition, and the port and
ground-domain type system are discrete mathematics — the native domain of Coq,
Lean, and Isabelle.

The most direct application encodes "well-formed circuit" as a dependent type.
A circuit representation in which structural validity is enforced by the type
checker — rather than asserted at runtime — provides a machine-checked guarantee
that the structural axioms hold. Lean 4 is particularly well suited: Mathlib has
extensive graph theory, and dependent types express constraints such as "a junction
node in domain D connects only to nodes in domain D or via coupling factor nodes"
as type constraints rather than runtime assertions.

Specific targets within this layer:

**Structural axioms (A1–A10)**: formalise `Circuit` as a dependent type; define
`WellFormed : Circuit → Prop` as the conjunction of A1–A10; produce a verified
decision procedure `check : (c : Circuit) → Decidable (WellFormed c)`. A passing
check yields a machine-checked proof of structural validity — analogous to what
CompCert provides for C compilation.

**SCC decomposition**: Tarjan's algorithm has existing formalisations in both Coq
and Isabelle. The property that the condensation of any directed graph is a DAG
is provable directly from the SCC definition.

**Tree-cotree state counting**: the theorem that dim(state) = #C + #L (minus
pathological cases) is a combinatorial graph result. The pathological cases —
all-C loops and all-L cutsets — are decidable graph properties. Mechanising the
proof would give a verified static checker for state-space rank.

**Ground domain isolation**: the property that no electrical current path exists
between nodes in different ground domains is a reachability property on the
constraint graph restricted to electrical edges — decidable and provable.

### Layer 2 — Linear Algebra and Continuous Mathematics (Medium Tractability)

KCL and KVL from the incidence matrix are linear algebra and formalise
straightforwardly. The DAE formulation for linear time-invariant circuits,
companion model error bounds, and Lyapunov stability for linear feedback SCCs are
achievable but require real analysis libraries.

**Tool selection**: Isabelle/HOL has the strongest applied analysis library
(HOL-Analysis, including measure theory and ODEs); Lean has Mathlib's analysis
tower; Coq has Coquelicot. All three can support this layer.

Specific targets:

**KCL and KVL from incidence matrix**: A·i = 0 and v = Aᵀ·e are provable as
consequences of the graph structure. Standard linear algebra over ℝ.

**Companion model correctness**: prove that the backward Euler companion model
for a capacitor or inductor approximates the continuous-time solution to within
a bounded error proportional to Δt (backward Euler) or Δt² (trapezoidal rule).
This is a standard numerical analysis result formalised in terms of ODEs.

**Linear SCC stability**: for a linear feedback SCC, convergence of fixed-point
iteration is equivalent to all eigenvalues of the loop gain matrix having magnitude
less than one. This is a standard linear algebra result provable in HOL-Analysis
or Mathlib.

The investment for this layer is significant. The payoff is a verified claim that
the companion-model simulation agrees with the continuous-time DAE solution to
within a formally characterised error bound.

### Layer 3 — Non-Linear Dynamics and Inference (Out of Scope)

Newton-Raphson convergence for general non-linear circuits is not provable without
circuit-specific Lipschitz conditions — a consequence of the non-linear SCC
abstraction problem listed as open in Section 15. The NP-hard inference problem
(Section 15) is a complexity result, not a verification target. Bond graph and
port-Hamiltonian formalisation has been explored in Isabelle but remains
research-level work.

These are not excluded on principle. They are excluded because the required
mathematical infrastructure either does not exist in current libraries or requires
circuit-specific conditions that cannot be stated in the general framework.

### Existing Relevant Work

| Area | Tool | Status |
|---|---|---|
| Digital circuit verification | ACL2, HOL4, Isabelle | Mature; industrial use |
| Hybrid systems (cyber-physical) | KeYmaera X, dL logic | Active; covers ODEs + discrete |
| Tarjan SCC formalisation | Coq, Isabelle | Exists in standard libraries |
| Graph theory | Lean 4 (Mathlib), Isabelle | Extensive coverage |
| ODE and real analysis | Isabelle/HOL-Analysis, Lean/Mathlib | Sufficient for linear DAE |
| Bond graph formalisation | Isabelle | Partial; not mainstream |
| Analog circuit formal verification | — | Sparse; no standard framework |

### Recommended Strategy

**Phase 1 — Structural layer in Lean 4**: formalise the circuit type, the ten
axioms, SCC decomposition, and the verified structural checker. This is achievable
without continuous mathematics and produces an immediately useful result: any circuit
passing the checker carries a machine-checked proof of structural validity.

**Phase 2 — Linear mathematics**: add KCL/KVL provenance from the incidence matrix,
companion model error bounds, and linear SCC stability. Isabelle/HOL or Lean 4 with
Mathlib are the appropriate tools.

**Phase 3 — Non-linear and inference**: contingent on progress in hybrid systems
verification and formal complexity theory. Not a near-term target.

The structural layer alone — a dependently typed circuit representation with a
verified well-formedness checker — would be a novel and substantive result for
circuit modelling frameworks. No equivalent exists for the class of framework
described here.

---

## 17. Extension: Neuromorphic Network Modelling

Neuromorphic networks can be modelled within this framework with four targeted
extensions: a spike domain, stochastic factor nodes, hybrid factor nodes for
threshold events, and a non-local plasticity layer. The core primitives — junction
nodes, factor nodes, ground domain tags, graph structure, SCC decomposition, and
hierarchical composition — are unchanged.

---

### 17.1 What Carries Over Unchanged

**Memristors** fit the existing framework directly. A memristor is a two-terminal
nonlinear differential factor node with bounded internal state:

```
V = M(w) · I
dw/dt = f(w, I)
```

where w is the internal state variable (physically: charge, flux, or a dimensionless
state variable normalised to [0, 1]) and M(w) is the state-dependent memristance.
The DAE formulation of Section 7 handles this. Gap 3 (non-linear operating point)
is no longer a corner case — it is the primary mode of operation.

**Graph structure and hierarchy** apply without modification. A neuromorphic network
is a directed graph of neuron and synapse components; layers and sub-networks are
hierarchical compositions.

**KCL and KVL** hold for charge flow at every junction. Synaptic currents, leak
currents, and injected stimulus currents sum at the membrane node of each neuron.

---

### 17.2 Spike Domain

A spike domain is added alongside the existing analog, digital, power, thermal, and
mechanical domains.

**Domain variables:**
- Effort: membrane potential V_m (volts)
- Flow: spike event stream — a sequence of discrete events {(t_k, a_k)} where t_k
  is spike time and a_k is amplitude (often normalised to 1)

Spike-domain signals are not continuous functions of time. They are point processes.
The spike domain does not carry continuous current; it carries timed events.

**Spike-domain edges** connect a neuron's output port to synapse input ports.
A single spike-domain edge may fan out to multiple synapses; each synapse
independently transforms the incoming event stream into a postsynaptic current.

**Domain conversion:**
- Analog → spike: integrate-and-fire neuron (Section 17.3)
- Spike → analog: synapse (Section 17.4)
- Spike → spike: spike routing, delay elements

---

### 17.3 Extended Constitutive Relation Table

The edge-relation table of Section 6 is extended with neuromorphic components.

| Component | Constitutive relation | Internal state |
|---|---|---|
| Memristor | V = M(w)·I ; dw/dt = f(w, I) | w(t) ∈ [0,1] |
| Leaky integrate-and-fire (LIF) | C_m·dV_m/dt = −(V_m−V_rest)/R_m + I | V_m(t) |
| Exponential integrate-and-fire (EIF) | C_m·dV_m/dt = −g_L(V_m−E_L) + g_L·Δ_T·exp((V_m−V_T)/Δ_T) + I | V_m(t) |
| Conductance synapse | I = g·(V_m−E_syn) ; dg/dt = −g/τ + w·Σδ(t−t_k) | g(t) |
| Current synapse | I = w·Σδ(t−t_k) | none |
| Spike delay | {(t_k+d, a_k)} = delay({(t_k, a_k)}, d) | none |

The integrate-and-fire rows are **hybrid factor nodes** — they have continuous
dynamics plus a discrete threshold event. The threshold is not captured by the
constitutive relation alone; see Section 17.4.

---

### 17.4 Hybrid Factor Nodes and Event-Driven Evaluation

Integrate-and-fire neurons are hybrid systems: continuous membrane dynamics
punctuated by discrete spike events. A hybrid factor node carries both a
continuous constitutive relation and a threshold condition:

```
Continuous:   C_m · dV_m/dt = f(V_m, I, t)
Threshold:    when V_m ≥ θ:
                  emit spike event on output port
                  V_m ← V_reset              (discrete reset)
Refractory:   V_m held at V_reset for duration τ_ref
```

The threshold condition and reset constitute a **guard and action** pair — standard
in hybrid automata. The factor node has three modes: integrating, spiking, refractory.

**Event-driven evaluation** replaces or supplements the companion-model timestep
approach of Section 7.3 for networks containing hybrid factor nodes:

1. Maintain a priority queue of pending spike events sorted by time
2. Advance continuous dynamics (adaptive ODE integration) to the next event time
3. Process the event: update discrete state, apply reset, generate downstream events,
   insert new events into the queue
4. Repeat

Between events the continuous subsystem is a standard ODE solvable by any
adaptive-step integrator (RK45, Dormand-Prince). The event queue handles
the discrete layer. This is the strategy used by NEST, Brian2, and NEURON.

**Interaction with SCC evaluation:** cycles in the spike-domain graph (recurrent
networks) are SCCs. Fixed-point iteration does not apply to spike-domain SCCs —
spike timing is the state, not a scalar to converge. Recurrent spike-domain SCCs
require simulation over time rather than algebraic fixed-point resolution. The
convergence axiom of Section 5 is suspended for spike-domain SCCs; stability
analysis uses Lyapunov methods on the continuous subsystem between events.

---

### 17.5 Stochastic Factor Nodes

Real neurons and many neuromorphic devices exhibit stochastic behaviour: thermal
noise in membrane voltage, probabilistic vesicle release at synapses, and
noise-driven threshold crossing. Stochastic factor nodes extend the deterministic
constitutive relation with a noise process:

**Langevin form** (additive noise in continuous dynamics):
```
f(v_k, i_k, ẋ_k, x_k, t) = σ_k · ξ_k(t)
```
where ξ_k(t) is a noise process (white noise: ξ ~ N(0,1); coloured noise:
Ornstein-Uhlenbeck). For a stochastic LIF neuron:
```
C_m · dV_m = [−(V_m−V_rest)/R_m + I] dt + σ · dW
```
where W is a standard Wiener process (Brownian motion).

**Probabilistic firing form** (stochastic threshold):
```
P(spike in [t, t+dt) | V_m) = r(V_m) · dt
```
where r(V_m) is a firing rate function (e.g. sigmoid or exponential). This replaces
the deterministic threshold with a hazard rate.

**Solver extension:** stochastic factor nodes require SDE integrators rather than
Newton-Raphson. Euler-Maruyama (strong order 0.5) and Milstein (strong order 1.0)
are standard. The companion-model framework of Section 7.3 extends straightforwardly:
the companion current source acquires a noise term proportional to √Δt.

**Statistical validation:** stochastic circuits are validated over ensembles. The
convergence axiom of Section 5 is reinterpreted as convergence in distribution
rather than to a fixed point.

---

### 17.6 Plasticity as a Non-Local Update Layer

Synaptic plasticity — weight changes driven by activity — is not a constitutive
relation in the standard sense. The weight w of a synapse between neuron A and
neuron B depends on the spike history of both A and B, which may be topologically
distant in the graph. This non-local dependency cannot be expressed as a factor
node connecting only adjacent variable nodes.

Plasticity is modelled as a **separate update layer** operating on weight variables
after each simulation epoch or event:

**Spike-timing dependent plasticity (STDP):**
```
Δw = A+ · exp(−Δt/τ+)    if Δt > 0   (pre before post: potentiation)
Δw = −A− · exp( Δt/τ−)    if Δt < 0   (post before pre: depression)
```
where Δt = t_post − t_pre is the relative spike timing.

**Trace variables:** STDP is implemented efficiently via eligibility traces — each
neuron maintains a decaying trace of its recent spike history:
```
dx_pre/dt  = −x_pre/τ+  + Σδ(t−t_pre)
dx_post/dt = −x_post/τ− + Σδ(t−t_post)
Δw = x_post · δ(t−t_pre) − x_pre · δ(t−t_post)
```
Traces are local state variables on each neuron node; the weight update reads
both traces at the synapse. This localises the dependency to the synapse's two
adjacent neurons.

**Modelling structure:** the plasticity layer is a second graph over the same
junction nodes, with weight-variable nodes and STDP factor nodes. It operates
asynchronously with the simulation graph — reading spike timestamps from the
event queue and updating weight variables between simulation steps.

**Weight bounds:** synaptic weights are constrained to [w_min, w_max]. This is a
box constraint on the weight variable node, enforced by clamping after each update.

---

### 17.7 Bond Graph Correspondence for Neuromorphic Components

The Hodgkin-Huxley model — the biophysically detailed antecedent of all
integrate-and-fire models — maps to bond graph elements. The following table
extends Section 13 for neuromorphic components.

The effort/flow assignment for the neural domain: membrane potential V_m is effort;
ionic current I is flow.

| Neural component | Bond graph element |
|---|---|
| Membrane capacitance | C-element (effort storage) |
| Leak conductance | R-element (dissipation) |
| Ion channel (voltage-gated) | Nonlinear R-element (state-dependent conductance) |
| Nernst / reversal potential | Se-element (effort source) |
| Ion pump | Sf-element (flow source) |
| Memristor | Nonlinear R-element with internal state |
| Synaptic conductance | Modulated R-element (controlled by spike events) |
| Threshold-and-reset | Hybrid event — no standard bond graph element |

The threshold-and-reset mechanism has no standard bond graph equivalent. It is a
hybrid automaton element outside the continuous bond graph formalism. This is the
boundary of the bond graph extension for neuromorphic systems.

---

### 17.8 Structural Axiom Notes

Axioms A1–A10 apply without modification to the neuromorphic extension, with the
following clarifications:

**A3 (Edge):** constitutive relations now include stochastic (Langevin) and hybrid
(threshold-and-reset) types in addition to algebraic and differential. The DAE
becomes a stochastic DAE (SDAE) for stochastic factor nodes.

**A8 (System boundary):** spike-domain input edges are signal inputs; spike-domain
output edges are signal outputs. The soft rules apply per domain as stated.

**Convergence axiom (Section 5):** suspended for recurrent spike-domain SCCs.
Stability for these is analysed by Lyapunov methods on the continuous subsystem;
stochastic stability uses moment analysis or Fokker-Planck methods.

---

### 17.9 Open Problems Specific to Neuromorphic Modelling

**Stochastic SCC convergence:** the convergence axiom for recurrent stochastic
networks requires reformulation. Convergence in distribution to a stationary
measure (if one exists) replaces fixed-point convergence. Conditions for existence
of the stationary measure for spiking networks are not fully characterised.

**Non-Markovian plasticity:** some biological plasticity rules depend on spike
history beyond a fixed time window. Representing infinite-history dependencies
within the finite-state trace-variable framework is an open problem.

**Formal methods for stochastic factor nodes:** Section 16's mechanisation strategy
applies to the deterministic layer. Formal verification of stochastic neuromorphic
circuits — proving distributional properties of network behaviour — requires
probabilistic model checking (PRISM, Storm) rather than Coq/Lean/Isabelle.
