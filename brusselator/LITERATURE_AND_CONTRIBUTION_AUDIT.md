# Literature and contribution audit for the Brusselator theorem

**Audit date:** 2026-08-28  
**Status:** publication-positioning audit; not theorem evidence

This note compares Theorem B in
[LOCALIZED_PROFILE_PROOF.md](LOCALIZED_PROFILE_PROOF.md) with the closest
primary literature. Its purpose is to fix what the eventual paper may and
may not claim. It does not upgrade the imported computer-assisted core input,
prove temporal stability, or certify an explicit interval of diffusion
parameters.

## 1. Exact object under comparison

The repository fixes the classical one-dimensional Brusselator on the real
line,

\[
\begin{aligned}
 u_t&=d u_{xx}-2u+1+u^2v,\\
 v_t&=v_{xx}+u-u^2v,
\end{aligned}
\qquad x\in\mathbb R,
\tag{1}
\]

that is, \(A=B=1\), and lets \(d\to0^+\). If
\(\varepsilon=\sqrt d\), then the Turing threshold is

\[
 B_T=(1+\varepsilon)^2,
 \qquad B-B_T=-2\varepsilon-\varepsilon^2.
\tag{2}
\]

Thus the theorem follows a joint singular path: the diffusion ratio tends to
zero while the fixed value \(B=1\) approaches the Turing curve at a prescribed
rate. With \(r=d^{1/4}=\sqrt\varepsilon\), Theorem B proves, relative to its
frozen core input, a locally selected even homoclinic branch for every
sufficiently small \(d>0\), with

\[
 \|u_d-1\|_\infty=\Theta(d^{1/2}),\qquad
 \|v_d-1\|_\infty=\Theta(d),\qquad
 W_u(d),W_v(d)=\Theta(d^{1/4}),
\tag{3}
\]

uniform exponential localization and positive concentrations. Here the
widths are the central connected half-height widths defined in Theorem B, not
an arbitrary experimental width observable.

## 2. Closest prior results

| Source | What it establishes | Why it does not contain Theorem B as stated |
|---|---|---|
| Jencks--Doelman--Kaper--Vo (2026), Proposition 2.1 | For fixed positive \(A,\varepsilon\), with \(A\) in the stated subcriticality intervals, and \(B\) sufficiently close to \(B_T\), reversible \(1{:}1\) normal-form theory yields periodic, quasi-periodic, and, for \(B<B_T\), symmetric homoclinic solutions. The paper also identifies the singular Brusselator RFSN-II geometry and studies spatially periodic canards. | The normal-form neighborhood is not stated uniformly as \(\varepsilon\to0\). In particular, no bound ensuring \(\delta(\varepsilon)>2\varepsilon+\varepsilon^2\) is supplied, so one cannot substitute (2). The proposition also does not state the positive-concentration conclusion or the joint-limit amplitude, tail, and width laws (3). |
| Iooss--Pérouème (1993) | Perturbative homoclinic solutions near a reversible \(1{:}1\) resonance in a four-dimensional vector field. | This is the general fixed-resonance mechanism used by later Turing analyses. It does not provide uniform estimates for the additional singular limit in which the critical frequency and normal-form coefficients degenerate with \(d\). |
| Glebsky--Lerman (1997) | General existence/stability framework for small stationary localized and periodic solutions near a reversible Hopf bifurcation, with the Brusselator as an example; the paper proves instability of specified basic localized branches under its hypotheses. | Its Brusselator discussion crosses the Turing curve with the diffusion ratio fixed and relies for existence on ordinary reversible-Hopf theory (and an unpublished model calculation). It supplies no theorem uniform along (2). Its temporal-instability conclusion therefore cannot be transferred to the present singularly uniform branch without a separate hypothesis and spectral audit. |
| Villar-Sepúlveda--Champneys (2023) | Turing criticality and fifth-order normal-form coefficients near degenerate Turing points; for the Brusselator, asymptotic Maxwell points and a parameter wedge associated with the local birth of homoclinic snaking. | This is a different codimension-two parameter regime. It does not select the \(A=B=1\), \(d\to0\) core homoclinic or prove the uniform physical conclusions (3). |
| Al Saadi--Champneys--Verschueren (2021) | A broad asymptotic and numerical organization of Turing, snaking, and semi-strong spike regimes for activator--inhibitor systems, including the Brusselator. | The work deliberately combines weakly nonlinear analysis, semi-strong asymptotics, and numerical continuation. Its Brusselator spike and snaking regimes vary feed parameters and do not give the exact all-small-\(d\) theorem on the fixed path (2). |
| Tzou--Bayliss--Matkowsky--Volpert (2011); Tzou--Nec--Ward (2013) | Singularly perturbed stationary and slowly moving pulses, and stability of localized spikes, on bounded one-dimensional domains. | The 2011 problem uses boundary inhibitor feed and global activator feed; the 2013 paper treats related rescaled finite-domain spike systems both without and with inhibitor influx. Both concern strong spike scalings rather than (1)--(3). |
| Kolokolnikov--Erneux--Wei (2006) | Existence and stability asymptotics for periodic mesa patterns when the input and output reactions are slow. | Mesa states in the slow-feed regime are not the small-amplitude RFSN-II homoclinic branch at fixed \(A=B=1\). |
| Kostet et al. (2018) | Numerical continuation and delayed-feedback dynamics for localized structures in a two-dimensional Brusselator. | The domain, dimension, parameter values, and evidence type differ; it is not an infinite-line existence theorem in the regime (2). |
| Arioli (2022) | Computer-assisted branches of stationary and periodic Brusselator solutions and Hopf bifurcations. | The proof concerns a bounded domain with Dirichlet boundary conditions, not a homoclinic on \(\mathbb R\) or the joint limit (2). |

## 3. The decisive quantifier distinction

The closest apparent overlap is Proposition 2.1 of
Jencks--Doelman--Kaper--Vo. Abstractly, its homoclinic statement has the
form

\[
 \forall\,0<\varepsilon<\varepsilon_*\ \text{fixed},\quad
 \exists\,\delta(\varepsilon)>0:
 -\delta(\varepsilon)<B-B_T<0
 \Longrightarrow \text{a pair of local symmetric homoclinics exists}
\tag{4}
\]

where, after specializing Proposition 2.1(iii) to \(A=1\), one may take

\[
 \varepsilon_* = \frac{21-\sqrt{313}}{16}.
\]

The application needed here is

\[
 \exists\,\varepsilon_0>0\quad
 \forall\,0<\varepsilon<\varepsilon_0:
 B-B_T=-2\varepsilon-\varepsilon^2
 \Longrightarrow \text{the selected branch exists}.
\tag{5}
\]

Statement (5) does not follow from (4) unless
\(\delta(\varepsilon)>2\varepsilon+\varepsilon^2\) for all sufficiently small
\(\varepsilon\). The published proposition gives no such control. Theorem B
instead rescales the joint limit to the fixed
RFSN-II core, imports one rigorously transverse core homoclinic, and continues
that intersection in \(r=\sqrt\varepsilon\). This is the mathematical bridge
that distinguishes the result from an ordinary fixed-\(d\) Turing
bifurcation statement.

## 4. Contribution verdict

The audit does **not** support any claim that localized stationary states in
the Brusselator are new. They have a long analytic, asymptotic, and numerical
literature, and local Turing homoclinics for the same classical model are
already covered by reversible \(1{:}1\) normal-form theory.

No inspected primary source proves the following conjunction:

1. the fixed path \(A=B=1\) for every sufficiently small \(d>0\);
2. continuation of a specified transverse RFSN-II core homoclinic;
3. a positive-concentration infinite-line stationary profile;
4. uniform exponential tails; and
5. the nonzero amplitude and central-width laws (3).

The defensible positioning is therefore:

> a singularly uniform, quantitative strengthening of the local Brusselator
> homoclinic picture along the RFSN-II path, conditional only on the explicitly
> stated computer-assisted Core Lemma.

This is a focused application result, not a new general continuation
mechanism. The proof after the Core Lemma uses standard parameter-dependent
invariant manifolds, reversibility, and the implicit-function theorem. Its
publication value lies in closing the singular quantifiers and translating
the continued orbit into explicit positive PDE scale laws. A short applied
dynamical-systems paper is the appropriate format.

## 5. Permitted and forbidden manuscript claims

The abstract and introduction may say that the paper:

- proves existence along the fixed singular path for all sufficiently small
  positive \(d\), relative to the stated Core Lemma;
- obtains positive concentrations, uniform localization, and the scale laws
  (3); and
- complements fixed-diffusion reversible-Turing normal forms and the
  periodic-canard analysis of the 2026 Brusselator paper.

They must not say that the paper:

- discovers the first Brusselator localized state or the first Brusselator
  homoclinic;
- proves that a time evolution selects the profile;
- proves temporal, spectral, or nonlinear stability;
- proves that the localized branch bifurcates from a Turing branch uniformly
  in \(d\);
- identifies this particular homoclinic as a spatial canard; or
- establishes an experimental chemical pattern.

The 1997 instability result is a reason to treat temporal stability as a
substantive separate problem, not as a missing sentence in the present
proof. Whether its hypotheses capture the singularly continued branch must
be checked before drawing either a stability or instability conclusion.

## 6. Primary references used in this audit

- R. Jencks, A. Doelman, T. J. Kaper, and T. Vo, *Stable and Unstable
  Spatially-Periodic Canards Created in Singular Subcritical Turing
  Bifurcations in the Brusselator System*, Journal of Nonlinear Science 36,
  55 (2026), [doi:10.1007/s00332-026-10268-6](https://doi.org/10.1007/s00332-026-10268-6).
- G. Iooss and M.-C. Pérouème, *Perturbed homoclinic solutions in reversible
  1:1 resonance vector fields*, Journal of Differential Equations 102
  (1993), 62--88,
  [doi:10.1006/jdeq.1993.1022](https://doi.org/10.1006/jdeq.1993.1022).
- L. Yu. Glebsky and L. M. Lerman, *Instability of small stationary localized
  solutions to a class of reversible 1+1 PDEs*, Nonlinearity 10 (1997),
  389--407,
  [doi:10.1088/0951-7715/10/2/005](https://doi.org/10.1088/0951-7715/10/2/005).
- E. Villar-Sepúlveda and A. R. Champneys, *Degenerate Turing Bifurcation
  and the Birth of Localized Patterns in Activator-Inhibitor Systems*, SIAM
  Journal on Applied Dynamical Systems 22 (2023), 1673--1709,
  [doi:10.1137/22M1509734](https://doi.org/10.1137/22M1509734).
- F. S. H. Al Saadi, A. R. Champneys, and N. Verschueren, *Localized patterns
  and semi-strong interaction, a unifying framework for reaction--diffusion
  systems*, IMA Journal of Applied Mathematics 86 (2021), 1031--1065,
  [doi:10.1093/imamat/hxab036](https://doi.org/10.1093/imamat/hxab036).
- J. C. Tzou, A. Bayliss, B. J. Matkowsky, and V. A. Volpert, *Stationary and
  slowly moving localised pulses in a singularly perturbed Brusselator model*,
  European Journal of Applied Mathematics 22 (2011), 423--453,
  [doi:10.1017/S0956792511000179](https://doi.org/10.1017/S0956792511000179).
- J. C. Tzou, Y. Nec, and M. J. Ward, *The stability of localized spikes for
  the 1-D Brusselator reaction--diffusion model*, European Journal of Applied
  Mathematics 24 (2013), 515--564,
  [doi:10.1017/S0956792513000089](https://doi.org/10.1017/S0956792513000089).
- T. Kolokolnikov, T. Erneux, and J. Wei, *Mesa-type patterns in the
  one-dimensional Brusselator and their stability*, Physica D 214 (2006),
  63--77,
  [doi:10.1016/j.physd.2005.12.005](https://doi.org/10.1016/j.physd.2005.12.005).
- B. Kostet et al., *Stationary localized structures and the effect of the delayed
  feedback in the Brusselator model*, Philosophical Transactions of the Royal
  Society A 376 (2018), 20170385,
  [doi:10.1098/rsta.2017.0385](https://doi.org/10.1098/rsta.2017.0385).
- G. Arioli, *Computer assisted proof of branches of stationary and periodic
  solutions, and Hopf bifurcations, for dissipative PDEs*, Communications in
  Nonlinear Science and Numerical Simulation 105 (2022), 106079,
  [doi:10.1016/j.cnsns.2021.106079](https://doi.org/10.1016/j.cnsns.2021.106079).

The searches were directed at the exact model, reversible-Turing homoclinics,
singularly perturbed Brusselator pulses, spike/mesa limits, homoclinic
snaking, and computer-assisted stationary branches. The novelty statement
above is deliberately phrased as a comparison with the inspected literature,
not as an unqualified claim of bibliographic completeness.
