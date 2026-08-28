# Van der Pol publication proof audit: 2026-08-28

**Verdict:** the audit supplies a publication-facing source map for the
model-specific V1--V5A seams and the positive NHIM-pole terminal.  The V6
compact-family step is a **conditional local transfer interface**: it assumes
the frozen fixed-system endpoint and matching equations, together with their
clean finite physical-event data.  Under those precisely bounded inputs, the
local construction refines the algebraic carrier, replaces the protected
pole gate by the V3 \(x=10\) carrier through an event-free slide, and
performs the marked-cover transfer.  This audit does not claim an independent
reconstruction of every imported fixed-system row.  The resulting V6--V7
statement therefore remains conditional in publication prose on the frozen
RFSN-II inputs until their source and computer-assisted evidence closure is
anonymously accessible.

This audit does not change `CLAIM_REGISTER.md`, certify the explicit Issue #7
box, or assert temporal stability, Turing selection, canard identification,
or experimental realization.

## 1. Publication-facing local interfaces

### CF: conditional compact-family saddle passage and first-hit transfer

[`COMPACT_FAMILY_FIRST_HIT_THEOREM.md`](../theory/COMPACT_FAMILY_FIRST_HIT_THEOREM.md)
records the parameter-uniform transfer used in the application.  Conditional
on its marked compact-family and fixed-system matching data, its decisive
clauses are:

- the already constructed Kato-oriented zero-energy passage, endpoint maps,
  matching inverse, and fixed-domain cross forms as explicit hypotheses;
- retention of every member of the supplied finite competing-event list
  \(q_{ef}=t_e-t_f\), including its prescribed pairwise ties and order data;
- the coverwise rate quantifier

  \[
   \varkappa<\varkappa_i^+
    <\frac{2\pi\inf_{U_i}\alpha}{\sup_{U_i}\beta},
  \]

  and the whole-cell mixed-\(C^2\) estimate, Proposition 2.1, (8)--(9);
- preservation of the supplied incidence complex, first-event assignment,
  selector and cross forms before finite-atlas descent.

The interface assumes rather than reproduces the fixed-system endpoint and
matching equations, the clean/neat frozen physical rows, and the completed
cross-form/coding modules recorded in `RETURN_EXIT_CODING_IMPORT.md`.  It
supplies the compact-family quantifier order and conditional transfer once
those data are given; it is not a standalone enumeration or independent
reproof of the imported fixed-system block.

### PT: positive NHIM-pole terminal

V3 proves the terminal asymptotics, while V6, Section 3.2 and Lemma V6.1
record the extra interface actually consumed by whole-cell composition:

- the boundary equilibrium NHIM and spectra
  \(\{-1,-4,0,0,+1\}\) and \(\{-1,0,0,1,4\}\);
- the open physical pole basin and unique labels \((Z_0,W_0,c_4)\);
- the energy derivative
  \(\partial_{c_4}\mathcal G=-30\epsilon\delta^4\ne0\);
- physical remaining distance and Laurent--log action potentials with one
  spare entry derivative, V6 (34a)--(36); and
- finite-cutoff exact composition followed by terminal subtraction in V6,
  Section 5.

The source-trace identity (P-trace) makes the V3
one-dimensional source window exactly the zero-action trace of the V6
two-dimensional pole aperture.  No isolated-sink pole theorem and no
relative overflowing-NHIM theorem is used.

## 2. Arrow-by-arrow dependency audit

| arrow | exact input | output used next | decisive estimate / transversality | proof source |
|---|---|---|---|---|
| V1 \(\to\) V2 | exact central scaling, Hamiltonian, reverser, clocks; frozen selected core homoclinic and compact central cells | compact positive wedge with saddle-focus, selected homoclinic, exact passage, central event family | V2 (8), homoclinic transversality (12), passage (13)--(14), state-\(C^3\)/parameter-\(C^2\) finite-flow bounds in §5, controlled isotopy (41)--(43) | `MODEL_AND_CENTRAL_CHART.md`; `CENTRAL_CORE_IMPORT.md`; `CENTRAL_CONTINUATION.md` §§2--6 |
| V2 \(\to\) V3 | finite pole gate, transported true-unstable source arc, strict finite first-hit margins | genuine finite-distance positive pole, open basin, labels, finite part | invariant cone and finite blow-up in V3 §§2--3; Fuchsian field (25)--(33); physical-coordinate determinant (43); source trace (P-trace) | `POSITIVE_POLE_FINITE_PART.md`; V6 §3.2 |
| V1 \(\to\) V4 | full positive-parameter physical field and primitive | positive outer future-staying hypersurface | exact outer compactification, graph cone, normal expansion and third-order bunching on the compact box | `OUTER_FUTURE_STAYING.md`, Theorem V4 and its graph-transform proof |
| V2 + V4 + T1 \(\to\) V5 | finite algebraic gate; local positive outer graph; relative overflowing NHIM for the auxiliary \(K_1\) center graph; frozen singular comparison/Jost data | resolved \(K_2\to K_1\to\) outer matching tube and arrival labels | endpoint-anchored adjoint, nonzero exchange coefficient, uniformly invertible matching operator, source incidence (A-inc)--(A-pb), moving-cut covariance | `CENTRAL_OUTER_MATCHING.md`; `RELATIVE_OVERFLOWING_NHIM.md`; `CENTRAL_OUTER_MATCHING.md` §2 import boundary |
| V5 \(\to\) V5A | matched positive outer orbit family and fixed physical primitive | reference-normalized outer length/action finite parts | same-\(Q\) flat shadowing with two parameter derivatives; V5 arrival interval lies strictly inside the V5A terminal domain; exact finite-cut covariance | `OUTER_ALGEBRAIC_FINITE_PART.md`, Theorem V5A and (7c) |
| V2 + V3 + V5A + frozen fixed-system data \(\to\) V6, locally (conditional) | exact marked saddle passages; homoclinic H1; fixed endpoint/matching equations and clean finite physical rows; actual algebraic and pole terminals; their finite parts | chartwise high-winding return--first-exit relation and branch potentials, conditional on the supplied fixed-system block | H1--H1'; existing-block refinements (B1)--(B2); grouped imported event table; (H2-rank), (H2-dyn), (H2-reg); coverwise (39) and whole-cell (40); pole composition estimate | V6 §§3--5 and Lemma V6.1; CF Proposition 2.1 |
| conditional local V6 + T2 \(\to\) physical V6 | locally constructed event relations, terminals, cross forms, actions, and coding branches under the fixed-system inputs | one physical relation on \(\Sigma_{T_*}\), compatible periods/actions | winding--residence comparison (40a), initial local thresholds, final truncation (40b), bounded overlap recoding | V6 §4 after (40); `FINITE_MARKED_ATLAS_DESCENT.md`, Proposition 1 |
| V6 \(\to\) V7 | completed branch rectangles and contraction bounds inside \(\Sigma_{T_*}\) | periodic, localized multipulse, and aperiodic stationary PDE solutions | cross form (12)--(15), finite-word endpoint solve, exact physical scaling (5), period/action formulas (29)--(30) | V6 Theorem V7 and §6; `RETURN_EXIT_CODING_IMPORT.md` bounded coding interface |

No arrow uses T2 to construct a missing local object.  No V3 conclusion is
obtained by persisting a singular-core pole.  No V5 conclusion substitutes
the invariant algebraic label for a transverse event carrier.  The two V6
rows above are conditional on the explicitly named fixed-system data; the
table does not upgrade those imports to a local independent proof.

## 3. Whole-cell first-event audit

V6 now records a grouped model-facing event table immediately after (38).
Its row classes are:

1. the four source-rectangle boundary functions;
2. the old homoclinic opening and outgoing laterals;
3. the transverse algebraic carrier, its matched internal label, and two
   tangential patch faces;
4. the V3 \(x=10\) carrier and its four product-window faces;
5. the nested homoclinic-return rows, including two target signs, stable cut,
   and return-box laterals; and
6. the supplied finite family of competing-time rows \(q_{ef}\).

For the new algebraic and pole label rows, the table gives the ambient
domain, coorientation, allowed incidences and priority,
forbidden sets and gap, order function, and protected anchor.  The construction
distinguishes:

- a **physical carrier**, whose flow derivative supplies an event speed;
- an **internal label** on the carrier, whose source-pullback conormal
  identifies the terminal stratum.

The H-u and H-r classes refer to the frozen V2 event lists, and the Q class
refers to the supplied finite competing-event list; the table does not expand
those imported lists item by item.  Conditional on that frozen census, the
source rank minimum includes nonempty tie conormals, while empty tie classes
have a positive \(|q_{ef}|\) gap.  No false positive order gap is claimed near
a genuine tie.  Exhaustiveness comes from the frozen V2 block together with
the exact A and P refinements; compact first-hit stability plus the signs of
the imported \(q_{ef}\) recover the physical event order after isotopy.  The
return isotopy is constructed on the fixed nested homoclinic cell and
extended by a boundary-tangent field
supported inside its product collar.  Thus it does not alter the outgoing
arrangement elsewhere.

## 4. Interface corrections made during the audit

1. Only the free root-four pole label is renamed \(c_4\) in V3 and V6, so it
   is not confused with the established spectral scale
   \(\kappa=\epsilon^{1/4}\).
2. The undefined V6 derivative \(D_\zeta\) is replaced by derivatives in
   the declared pole-entry coordinates \(D_{\mathbf e_{\rm p}}\).
3. The compact-transfer interface records the mixed-total-three
   event/finite-flight bound it consumes; this audit does not alter the V2
   theorem statement to add that stronger clause.
4. V6 uses the coverwise rate bound
   \(2\pi\inf_{U_i}\alpha/\sup_{U_i}\beta\), not only the pointwise
   infimum of \(2\pi\alpha/\beta\).
5. Algebraic-label transversality and carrier speed are no longer conflated.
6. The final radius is chosen below one finite minimum of all V3--V5A
   upper-radius thresholds before the positive annulus is frozen; the pole
   thickness is selected afterward and the radius is not decreased again.

## 5. Claim boundary and remaining blockers

Conditional on the frozen inputs itemized above, the analytic conclusion is
existential on some compact positive annular box.  The formal Issue #7
candidate box

\[
 [0.04,0.08]\times[-0.25,0.25]\times[0.8,1.2]
\]

is not yet a theorem box.  `V2.EXACT_CHART` still has five open explicit
interval-validation children, and the aggregate candidate contract remains
`INCONCLUSIVE`, `claim_bearing=false` until all parent obligations and the
release replay policy pass.

> **Later status note.**  This paragraph records the audit-date frontier.
> Subsequent atom-specific proofs now give all seven P2d children and the local
> parent `V2.EXACT_CHART` mathematical `PASS` on their declared domains.  P2e
> and later obligations remain open, and the aggregate remains `INCONCLUSIVE`
> and non-claim-bearing at independent replay 1/2; see
> [`P2D_CHART_OVERLAPS_REPORT.md`](../validation/rigorous/P2D_CHART_OVERLAPS_REPORT.md).

The frozen core homoclinic, singular comparison/Jost data, and fixed-system
matching/coding modules are bound to an immutable local revision with exact
hashes.  Anonymous access to that complete source/evidence closure returned
404 on the audit date.  Accordingly the publication-safe principal wording
remains:

> Assuming the frozen RFSN-II core and fixed-system return--exit modules
> recorded in the import statements, the present repository proves the
> positive-parameter van der Pol two-end return--first-exit theorem and the
> resulting stationary spatial pattern families.

This audit does not upgrade the compact-family transfer or its fixed-system
data to an unconditional local theorem.  The accessibility issue therefore
triggers the publication stop rule: a polished unconditional van der Pol
manuscript must wait for an accessible immutable release or for the remaining
imported fixed-system modules to be reproduced locally with their
computer-assisted inputs.
