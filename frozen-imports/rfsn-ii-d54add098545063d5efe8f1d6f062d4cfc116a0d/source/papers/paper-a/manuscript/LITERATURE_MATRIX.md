# Paper A literature matrix

Audit date: 2026-08-26.

This matrix records what Paper A may safely import from the primary literature
and what still has to be proved in Paper A.  It is a claim-boundary document,
not a priority search through the eventual submission date.  Bibliographic
keys are those in `references.bib`.

## Evidence scale

- **VOR + text**: bibliographic metadata and the relevant theorem, proposition,
  or statement were checked in the version of record or an official full-text
  rendering.
- **VOR + abstract**: metadata and the publisher abstract were checked; any
  stronger theorem-level qualifier is separately identified.
- **Author text**: an author-hosted manuscript or repository copy was checked
  in addition to the publisher record.
- **VOR + contents**: publisher metadata and the relevant section locator were
  checked, but the complete theorem text was not used to justify a stronger
  claim.
- **Metadata**: only the primary bibliographic record was checked.  No claim in
  this matrix rests on metadata alone.

## Saddle-focus, reversible, and RFSN-II background

| Key | Primary evidence and safe import | Boundary for Paper A | Audit status |
|---|---|---|---|
| `Devaney1976Homoclinic` | The [publisher DOI record](https://doi.org/10.1016/0022-0396(76)90130-3) and [Devaney's publication list](https://math.bu.edu/people/bob/publications.html) verify the 1976 JDE article and pp. 431--438.  A [later publisher-primary restatement](https://doi.org/10.1016/j.cnsns.2024.108189) confirms that, for every fixed finite \(N\), the transverse Hamiltonian saddle-focus homoclinic theorem supplies a compact hyperbolic invariant set conjugate to the \(N\)-shift on a local section. | Finite-\(N\) horseshoes, their entropy, and dense periodic points are classical.  This does **not** give a uniform \(N\to\infty\) atlas, countable-end topology, terminal first-event partition, or weighted cocycles. | **VOR metadata + primary restatement.**  The original typeset theorem pages were not independently reopened in this pass.  Use pp. 431--438; 431--439 appearing in some later bibliographies is not the primary metadata. |
| `Devaney1977BlueSky` | The [official IUMJ article page](https://iumj.org/article/2634/) and the article's first-page statement verify Theorem A: a nondegenerate symmetric homoclinic is approached by a one-parameter family of closed orbits whose periods diverge. | The blue-sky family is not new.  Only a theorem coupling it to Paper A's terminal channels or proving new uniform jet/action laws can contribute here. | **VOR + text.**  The DOI registry metadata are incomplete; title, volume, issue, and pp. 247--263 were taken from IUMJ, not inferred from Crossref. |
| `Lerman1991ComplexDynamics` | The [AIP DOI record](https://doi.org/10.1063/1.165859) and the primary abstract verify symbolic hyperbolic reconstructions and horseshoe bifurcations as the Hamiltonian value varies near a transverse saddle-focus homoclinic. | Energy-dependent horseshoe reconstruction is prior art.  Do not cite this paper alone for Paper A's split-end Hausdorff topology, exact transition grammar, or uniform field-to-atlas persistence. | **VOR + abstract; author text.**  Exact theorem numbers and all quantifiers have not been rechecked against the AIP typeset pages. |
| `Lerman1997HomoHeteroclinic` | The [official Regular and Chaotic Dynamics page](https://rcd.ics.org.ru/RD1997v002n04ABEH000054/) and the primary text verify the two-copy heteroclinic coding construction, including a coherent common-tail/doubled-origin pattern and existence and uniqueness for the coded orbits. | This is prior set-level symbolic organization.  It does not supply Paper A's first-event cells, weighted roof/action limits, or a perturbative field-to-atlas theorem.  Paper A must define and prove its own geometric topology rather than silently transferring one from a different alphabet. | **VOR + text.**  The official page assigns DOI `10.1070/RD1997v002n04ABEH000054`; automated DOI content negotiation currently fails, so the journal page is the controlling record. |
| `Lerman2000DynamicalPhenomena` | The [Springer record](https://link.springer.com/article/10.1023/A%3A1026411506781), together with the primary text and the 1997 proof source, supports a shift-intertwining set-level coding by signed isolated symbols and ideal labels, with explicit transition rules. | The printed 2000 single-copy neighborhood families do not satisfy neighborhood-basis refinement.  Paper A may import the grammar and orbit bijection, but may not attribute to this wording a section-topology conjugacy, compact metric realization, continuous transition indicator, or uniform hyperbolicity. | **VOR + text.**  This is a direct mathematical audit of the printed definitions, not a claim that the publisher or author issued an erratum. |
| `Lerman2000WIAS577` | The [official WIAS repository record](https://archive.wias-berlin.de/receive/wias_mods_00000965) verifies preprint 577 and its distinct homo-/heteroclinic title.  The author preprint independently confirms that the single-tail wording found in the 2000 journal version is not an OCR artifact. | Use only as corroborating primary text.  Do not merge its title or bibliographic identity with the Journal of Statistical Physics article. | **Author text + metadata.** |
| `Harterich1998Cascades` | The [ScienceDirect record](https://doi.org/10.1016/S0167-2789(97)00210-8) verifies that for each \(n\ge2\) there are infinitely many nearby \(n\)-homoclinic orbits and that each is accompanied by one or more periodic families. | Multipulse cascades and accompanying periodic families are classical and preclude a finite orbit census.  They do not by themselves classify all staying points or construct Paper A's terminal atlas. | **VOR + abstract.**  The stronger wording “reversible nondegenerate” is explicitly restated in Theorem 2.1 of `BarrientosRaibekasRodrigues2019Chaos`, but was not independently checked in the paywalled original theorem text. |
| `BarrientosRaibekasRodrigues2019Chaos` | The [publisher record](https://doi.org/10.1080/14689367.2019.1569592) and [official arXiv text](https://arxiv.org/html/1810.06359) verify: under (P1)--(P3), Theorem A gives, for every finite \(N\ge2\) and every sufficiently small tube, an invariant set mapping continuously and onto the **one-sided** \(N\)-shift, with dense periodic points and entropy at least \(\log N\).  Theorem B gives one-sided infinite switching by super-homoclinics and finite switching by symmetric homoclinic/periodic trajectories. | Their Theorem A does not assert compactness, hyperbolicity, injectivity, or two-sided conjugacy.  Those properties must not be silently strengthened.  Neither theorem couples the bifocal recurrence to RFSN-II ends or weighted time/action data. | **VOR metadata + author text.**  Hypotheses and theorem qualifiers were checked directly. |
| `VoDoelmanKaper2025Canards` | The [SIAM version of record](https://epubs.siam.org/doi/10.1137/24M1690722) and [official arXiv record](https://arxiv.org/abs/2409.02400) verify the reversible RFSN-II blow-up, algebraic orbit, and spatial-canard structure.  Published Proposition 6.2 gives three heteroclinic classes in the zero-energy half-space and identifies \(W^s(\Gamma_0^-)\) and \(W^u(\Gamma_0^+)\) as class boundaries. | RFSN-II, the algebraic separatrix, the zero-energy heteroclinic partition, and the model periodic family are prior art.  The source does not provide Paper A's bifocal first-event/terminal atlas, two-end counterterms, or field-level realization/persistence. | **VOR + text; author text.**  Published online 8 October 2025; volume 24(4), pp. 2618--2684. |
| `JencksDoelmanKaperVo2026Brusselator` | The [Springer version of record](https://link.springer.com/article/10.1007/s00332-026-10268-6) and [official arXiv record](https://arxiv.org/abs/2509.04835) verify the Brusselator RFSN-II/RFS canards, small- and large-amplitude spatially periodic canards, saddle-node branch, and PDE stability computations.  Section 7.3 gives the fixed-\(v_0\) takeoff/touchdown expansion on \(\lvert\xi\rvert<1/(\sqrt\varepsilon\lambda(v_0))\) and notes \(\Delta v=O(\varepsilon)\); section 7.4 invokes standard theory for periodic closure. | The first Brusselator RFSN-II, periodic canards, their folds, and the model touchdown calculation are not new.  “Standard theory may be used” is not a uniform field-to-atlas realization theorem.  Paper A v1 must not claim that the Brusselator has already been verified to lie in its weighted field class. | **VOR + text; author text.**  Journal of Nonlinear Science 36(3), article 55, published 19 May 2026; there is no page range to invent. |
| `Bolotin2025SlowFast` | The [official Regular and Chaotic Dynamics record](https://rcd.ics.org.ru/S1560354724590039/) verifies the slow--fast Hamiltonian saddle-focus hypotheses, the Shilnikov separatrix-map formulas, prescribed slow-variable evolution, and the three-body application stated in the abstract. | A slow--fast Hamiltonian separatrix map and prescribed slow drift are prior art.  This paper does not supply Paper A's complete first-return/first-exit decomposition or its algebraic/pole action counterterms. | **VOR + abstract.**  Volume 30(1), pp. 76--92; DOI `10.1134/S1560354724590039`. |
| `HomburgLambTuraev2025Entropy` | The [open ScienceDirect version of record](https://doi.org/10.1016/j.aim.2025.110131) verifies positive topological entropy for a strongly transverse symmetric homoclinic tangle associated with a normally hyperbolic family of symmetric periodic orbits in smooth reversible vector fields. | Natural reversible hypotheses and a system-level entropy conclusion provide a generality benchmark.  The theorem does not provide Paper A's singular two-end renormalization, while Paper A does not inherit its global entropy conclusion merely from local first-exit data. | **VOR + abstract; author text available as arXiv:2207.10624.**  Advances in Mathematics 464 (2025), article 110131. |
| `BaldomaGiraltGuardia2023L3` | The [publisher version](https://doi.org/10.1016/j.aim.2023.109218) and [author manuscript](https://arxiv.org/abs/2107.09941) verify an exponentially small asymptotic formula for the separation of the stable and unstable manifolds of \(L_3\) in the RPC3BP, obtained through an inner equation and complex matching. | This is a benchmark for a model-specific Hamiltonian theorem with one sharp reusable asymptotic mechanism.  Paper A neither imports nor claims a separatrix-splitting formula. | **VOR + text; author text.**  Advances in Mathematics 430 (2023), article 109218. |

## General tools that are also prior art

| Key | Primary evidence and safe import | Boundary for Paper A | Audit status |
|---|---|---|---|
| `HirschPughShub1977InvariantManifolds` | The [Springer primary record](https://doi.org/10.1007/BFb0092042) verifies Lecture Notes in Mathematics 583 and locates the (C^r) section theorem and Lipschitz-jet argument in Chapter 3, pp. 25--38. | The section theorem supplies the standard graph-transform regularity mechanism. Paper A still defines its global corridor transform, verifies the face and cone conditions, displays the state-jet rate gaps, and proves the anisotropic mixed state/parameter scale used here; the citation does not certify the RFSN-II numerical inequalities. | **VOR + contents.** The present proof cites the chapter-level mechanism and gives its corridor specialization rather than importing an unstated parameter theorem. |
| `Fenichel1971Persistence` | The [official IUMJ record](https://doi.org/10.1512/iumj.1971.21.21017) verifies the persistence and smoothness theorem for invariant manifolds of flows under normal hyperbolicity. | Normal-hyperbolic persistence is background.  It does not supply Paper A's graph over a fixed interval block with structural boundary faces, its explicit finite-time quotient inequalities, or the mixed (C^0_pC^3_x\cap C^1_pC^2_x\cap C^2_pC^1_x) corridor estimate. | **VOR + text.**  Volume 21(3), pp. 193--226. |
| `Mather2012Notes` | The [AMS version of record](https://doi.org/10.1090/S0273-0979-2012-01383-6) gives control data, controlled vector fields, and the first isotopy lemma for Whitney/Thom stratifications. | This supports the qualitative controlled-lift mechanism, not the stronger ambient (C^s) diffeomorphism with corners, quantitative closeness, labelled sign strata, and component census proved in Proposition 5.1. | **VOR + text.**  Sections 7--11 and Proposition 9.1 were checked. |
| `Verona1984Stratified` | The [Springer primary record](https://doi.org/10.1007/BFb0101672) and the monograph text treat controlled vector fields and stratified mappings on spaces with faces. | Verona supplies the closest general background for faces and control data.  Paper A still proves its finite normal-crossing ambient lift because a general stratified trivialization does not by itself yield the face-preserving (C^s) ambient diffeomorphism or uniform empty-incidence threshold used here. | **VOR + text.**  The relevant ranges are pp. 9--20 and 29--57. |
| `Wasow1965Asymptotic` | Wasow's monograph supplies classical regular-singular/Frobenius asymptotic background, including resonant logarithms. | Classical linear regular-singular expansions do not provide Paper A's nonlinear parameter-dependent finite recursion, remaining-time inversion, action-density subtraction, or coordinate uniqueness.  These are proved in Proposition D.8 and its supporting lemmas. | **Primary monograph + contents.** |
| `Sarig1999Thermodynamic` | The [Cambridge DOI record](https://doi.org/10.1017/S0143385799146820), [author publication page](https://www.weizmann.ac.il/math/sarigo/papers), and author manuscript verify thermodynamic formalism for countable-state topological Markov shifts, including pressure, recurrence, Ruelle--Perron--Frobenius theory, and Gibbs/equilibrium questions under the relevant regularity hypotheses. | Countable Markov shifts, summable-variation potentials, and their abstract thermodynamic formalism are not new.  Paper A must still derive its actual alphabet, topology, transition law, and summable-variation/weighted estimates from the RFSN-II first-event geometry; Sarig cannot supply those geometric hypotheses. | **VOR + abstract; author text.**  The verified DOI ends in `9146820`. |
| `DelshamsDeLaLlaveSeara2008Scattering` | The [ScienceDirect record](https://doi.org/10.1016/j.aim.2007.08.014) and [author manuscript](https://web.mat.upc.edu/people/tere.m-seara/articles/DelshamsLlS2008advmath.pdf) verify symplectic and exact-symplectic scattering maps for normally hyperbolic invariant manifolds.  In the exact case the primitive has a variational interpretation as an action difference; Hamiltonian-flow analogues are included. | Exact symplecticity and action primitives are not new.  A Paper A section-to-section germ is not automatically a scattering map in this NHIM sense.  Paper A's burden is the coordinate-compatible exact cocycle together with its algebraic/pole renormalization, two-end counterterms, first-event partition, and field realization. | **VOR + abstract; author text.** |

## Validated numerics and chart-production background

| Key | Primary evidence and safe import | Boundary for Paper A | Audit status |
|---|---|---|---|
| `Moser1958Liapunoff` | The [Wiley version-of-record page](https://doi.org/10.1002/cpa.3160110208) verifies Moser's analytic saddle construction and the bibliographic data: *Communications on Pure and Applied Mathematics* 11(2), 257--271 (1958). | Moser's construction is the historical source for the convergent solution family, but it does not by itself supply the convergent **canonical** normalizing transformation used in Paper A. The manuscript therefore cites Giorgilli for that step and proves its own reversible and parameter-dependent adaptation. | **VOR + metadata; theorem scope cross-checked against Giorgilli's account.** |
| `Giorgilli2001Unstable` | The [AIMS version-of-record page](https://doi.org/10.3934/dcds.2001.7.855) and the primary article verify Theorem 1 on p. 856: a convergent near-identity canonical transformation puts a complex-saddle Hamiltonian into the stated normal form. In two degrees of freedom the residual modes are absent, yielding the two-invariant form used in the local passage. | This is a fixed-system analytic canonical theorem. It does not state reverser-equivariance, a common domain for an external C^2 parameter family, an exact primitive gauge, or Paper A's weighted D_log bounds. Those points are proved in the local action--time proposition rather than attributed to the source. | **VOR + text.** The theorem statement and page were checked directly; DCDS 7(4), 855--871. |
| `KepleyMirelesJames2019Chaos` | The [ScienceDirect version of record](https://doi.org/10.1016/j.jde.2018.08.007) and [author manuscript](https://arxiv.org/abs/1711.06932) verify a computer-assisted proof of a transverse saddle-focus homoclinic in a two-degree-of-freedom Hamiltonian model, followed by Devaney's forcing theorem.  The validation also yields quantitative manifold and transport information. | This is direct precedent for validating the hypotheses of a general Hamiltonian homoclinic theorem in a concrete system.  It does not validate the universal RFSN-II core, either compactified end, or Paper A's first-event partition. | **VOR + text; author text.**  Journal of Differential Equations 266(4), 1709--1755 (2019). |
| `KapelaMrozekWilczakZgliczynski2021CAPD` | The [ScienceDirect version of record](https://doi.org/10.1016/j.cnsns.2020.105578), [official arXiv manuscript](https://arxiv.org/abs/2010.07097), and [CAPDGroup repository](https://github.com/CAPDGroup/CAPD) verify CAPD::DynSys as a C++ toolbox for rigorous ODE integration, variational equations, and Poincaré maps, with \(C^0\), \(C^1\), and higher-order validated solvers. | Validated integration software is not itself a proof of Paper A's orbit, first-event, transversality, or uniform-parameter claims.  Those claims rest on the source equations, outward-rounded boxes, Krawczyk inclusions, event inequalities, hashes, and replay contract in each certificate. | **VOR + text; author text; official software repository.**  The article is volume 101 (2021), article 105578; its DOI correctly contains `2020`. |
| `LerchTischlerWolffVonGudenbergHofschusterKramer2006FILIB` | The [ACM DOI record](https://doi.org/10.1145/1141885.1141893) verifies FILIB++ 32(2), 299--324 and its interval elementary-function bounds, extended containment mode, and portable C++ design. | This citation documents the interval-library lineage, not the identity of the binary used for Paper A.  The certificates must pin the CAPD commit, FILIB backend, compiler flags, and library hashes; a backend name alone is insufficient. | **VOR + abstract.**  Metadata and all five authors were checked in the ACM/Crossref record. |
| `Krawczyk1980IntervalIterations` | The [Springer version of record](https://doi.org/10.1007/BF02281718) verifies interval extensions and interval iterations that enclose solutions of operator equations. | The classical inclusion principle does not certify any Paper A box until the manuscript or replay gives the actual operator, preconditioner, interval Jacobian/slope enclosure, strict interior inclusion, and uniqueness or contraction quantifiers used. | **VOR + abstract.**  Computing 24(2--3), 119--129 (1980). |
| `Rump1990RigorousSensitivity` | The [AMS DOI record](https://doi.org/10.1090/S0025-5718-1990-1011445-5) and [author-institution copy](https://tore.tuhh.de/entities/publication/738cb3a4-e21e-4ec8-a7a4-d86713bcf8ad) verify rigorous sensitivity and guaranteed solution-set enclosures for linear and nonlinear systems with uncertain input data.  This is the direct standard background for uniform parameter boxes/parametric Krawczyk reasoning. | Parametric validated enclosures are prior art.  Paper A must still prove that its correlated graph/target uncertainties enter the chosen finite-dimensional residual and Jacobian enclosures correctly and that every declared parameter value is covered. | **VOR metadata + author text.**  Mathematics of Computation 54(190), 721--736. |
| `Tucker2011Validated` | The [Princeton/De Gruyter record](https://doi.org/10.1515/9781400838974) verifies the monograph's rigorous-numerics framework: outward-rounded interval arithmetic, validated zeros, and rigorous ODE computations. | It supplies methodological background, not a certificate for this paper.  Every claim-bearing package must still expose its equations, enclosures, rounding contract, dependency hashes, and replay gate. | **VOR + contents.** |
| `WilkinsonEtAl2016FAIR` | The [Nature Scientific Data version of record](https://doi.org/10.1038/sdata.2016.18) states the FAIR stewardship principles, including globally unique persistent identifiers, metadata, provenance, and reusable digital objects. | FAIR is not mathematical evidence.  Paper A's own release contract strengthens persistent identification to immutable candidate binding and machine-readable provenance; acceptance still depends on actual replay of the mathematical certificates. | **VOR + text.** |
| `CabreFontichDeLaLlave2003Parameters` | The [IUMJ DOI record](https://doi.org/10.1512/iumj.2003.52.2407) and [author-hosted journal text](https://web.mat.upc.edu/xavier.cabre/docs/indi2jour.pdf) verify parameter-dependent invariant-manifold parameterizations under uniform spectral/nonresonance assumptions.  The paper records joint regularity and sharper mixed state/parameter classes; its Theorem 2.1 preserves the declared mixed class rather than losing a derivative. | Smooth parameter dependence of invariant manifolds is standard.  Paper A must verify the uniform spectral hypotheses, its finite differentiability budget, the marked phase/cut normalization, reversibility, and exact-Hamiltonian compatibility; the citation cannot replace those checks. | **VOR + text; author text.**  Indiana University Mathematics Journal 52(2), 329--360. |
| `Meyer1981DiscreteSymmetry` | The [ScienceDirect record](https://doi.org/10.1016/0022-0396(81)90059-0) verifies the basic reversible-Hamiltonian fact that the fixed set of an anti-symplectic involution is Lagrangian. | This gives the Lagrangian symmetry geometry, not a parameter-uniform marked Darboux chart, chosen source cut, phase gauge, or exact primitive.  Those choices and their continuity must be constructed in Paper A. | **VOR + abstract.**  Journal of Differential Equations 41(2), 228--238. |
| `OrtegaRatiu2004MomentumMaps` | The [Springer book record](https://link.springer.com/book/10.1007/978-1-4757-3811-7) verifies the monograph metadata and its §7.3 \(G\)-relative Darboux theorem for proper **symplectic** group actions. | A reverser is anti-symplectic, so the cited equivariant theorem is not directly the marked reversible straightening required by Paper A.  At most it supplies the compact/proper-group Moser template; Paper A still needs a short relative anti-symplectic/marked-cut lemma or an exact source covering that variant. | **VOR + contents.**  No direct anti-symplectic conclusion is attributed to the book. |

## Cross-source novelty ledger

The following components are established background and must not be presented as
Paper A's standalone novelty:

1. fixed-\(N\) Hamiltonian saddle-focus horseshoes and blue-sky periodic
   families;
2. countable set-level critical coding, reversible multipulse cascades, and
   one-sided switching near a bifocus;
3. RFSN-II blow-up, algebraic separatrices, zero-energy heteroclinic classes,
   and the cited model's spatially periodic canards;
4. abstract countable Markov shifts, summable-variation thermodynamic
   formalism, exact-symplectic scattering maps, and action primitives;
5. validated ODE/Poincaré-map software, interval/Krawczyk inclusion methods,
   smooth parameter dependence of invariant manifolds, and ordinary
   symplectic equivariant-Darboux machinery.

The defensible Paper A contribution is instead the **coupled theorem**: from a
non-circular open class of reversible exact-Hamiltonian fields, construct the
RFSN-II first-event atlas (recurrent, algebraic, pole, lateral, gap, and boundary
components), realize its high-winding labels in fixed normalized charts, and
control the exact roof/action cocycles with the required algebraic and pole-end
counterterms, uniform weighted estimates, parameter jets, and field-level
persistence.  Each part of that sentence remains a theorem obligation; the
literature above supplies background inputs, not the assembled result.

## Items still requiring care before submission

1. If the manuscript cites an exact theorem number or all detailed quantifiers
   from Lerman 1991, inspect the AIP typeset theorem pages first.  The current
   audit supports its abstract-level scope but does not use it as the topology
   source.
2. If the manuscript needs Härterich's exact original nondegeneracy and
   reversibility wording, retrieve and check the theorem pages.  The publisher
   abstract establishes the cascade and periodic-family claims; the stronger
   qualifiers are presently cross-checked through the 2019 primary paper's
   restatement.
3. Retain the DOI printed on the official 1997 Regular and Chaotic Dynamics
   page even though DOI content negotiation currently fails; cite that journal
   page as the accessible primary record.
4. Describe the 2000 Lerman neighborhood issue as Paper A's audit of the printed
   definition, not as an official correction.  Import only the set-level
   grammar/bijection unless Paper A independently proves a topology.
5. The 2026 Brusselator item is article 55, not a page range.  Do not replace its
   journal year with the 2025 arXiv posting year.
6. Before making a priority claim in a submitted paper, update the search from
   this audit date through the submission date.  The present matrix is a
   theorem-scope audit, not an exhaustive novelty certification.
7. The apparent CAPD version conflict has a precise source.  At commit
   `731079217a9254ea2948d742df2b170895effe7f`, the official
   [`CAPDVersion.txt`](https://github.com/CAPDGroup/CAPD/blob/731079217a9254ea2948d742df2b170895effe7f/CAPDVersion.txt)
   declares CAPD 6.1.0, and the generated
   [`capd.pc`](https://github.com/CAPDGroup/CAPD/blob/731079217a9254ea2948d742df2b170895effe7f/capdMake/libcapd/capd.pc.in)
   sets its package `Version` from that value.  The
   [`capd-config` wrapper](https://github.com/CAPDGroup/CAPD/blob/731079217a9254ea2948d742df2b170895effe7f/capdMake/libcapd/capd-config.in)
   merely forwards its options to `pkg-config`.  Consequently,
   `capd-config --version` reports the **pkg-config program version** 2.5.1,
   whereas `capd-config --modversion` is the CAPD package-version query and
   reports 6.1.0 for this build.

   - The generating command is explicit in
     [`validation/fixed-fold-event-bridge/replay.py:308`](../../../validation/fixed-fold-event-bridge/replay.py#L308):
     it runs `capd-config --version`.  The finite-source builder also hard-codes
     2.5.1 at
     [`validation/finite-source-intermediate-collar/build_certificate.py:139`](../../../validation/finite-source-intermediate-collar/build_certificate.py#L139).
   - Directly affected JSON files are
     `validation/fixed-fold-event-bridge/certificate.json`
     (`capd_config_version`),
     `validation/finite-source-intermediate-collar/certificate.json`,
     `validation/finite-source-intermediate-collar/spiral_extension_certificate.json`,
     and `validation/future-target-fold/certificate.json`
     (`capd_pkg_config_version`), together with
     `validation/fundamental-annulus-overlap/certificate.json`,
     `validation/origin-unstable-pole-entry/certificate.json`,
     `validation/universal-core-periodic-return/certificate.json`, and
     `validation/universal-core-symmetric-homoclinic/certificate.json`
     (`capd_version`), and
     `validation/origin-algebraic-heteroclinic/certificate.json` (`capd`).
     The first two field names are also semantically misleading if read as a
     CAPD version obtained through pkg-config: their value is the pkgconf
     executable version, not the CAPD package version.
   - Directly affected prose is in the READMEs for
     `finite-source-intermediate-collar`, `fixed-fold-event-bridge`,
     `future-target-fold`, `origin-algebraic-heteroclinic`,
     `origin-unstable-pole-entry`, `universal-core-periodic-return`, and
     `universal-core-symmetric-homoclinic`, and in the replay paragraph of
     `papers/paper-a/manuscript/main.tex`.  The future-fold README already says
     “pkg-config version”; the others must not call 2.5.1 the CAPD source
     version or a CAPD compatibility version.
   - By contrast, the
     [pole-cone certificate](../../../validation/pole-cone-entry/certificate.json)
     records the source version 6.1.0.

   Do not silently rewrite claim-bearing certificates.  Use the unified prose
   “CAPD source 6.1.0 at commit `731079...`; pkgconf executable 2.5.1;
   FILIB backend; pinned library hashes,” then regenerate certificate metadata
   with both `--modversion` and `--version` fields in a future clean replay.
8. The present audit found standard symplectic equivariant-Darboux and
   anti-symplectic Lagrangian-fixed-set inputs, but not a single checked source
   that packages the precise parameter-uniform, exact, anti-symplectic,
   marked-cut straightening needed by Paper A.  State and prove that short
   relative-Moser/straightening lemma in the manuscript unless a closer primary
   source is subsequently verified.
