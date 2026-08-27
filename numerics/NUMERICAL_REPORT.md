# Numerical atlas report

**Evidence status: Numerically observed / COMPUTED-E1.**  The results below
come from ordinary double-precision collocation and shooting on the current
computer.  They are reproducible numerical evidence, not outward-rounded
interval validation and not a substitute for task #7.

## Main outcome

The computations recover the two most visible quantitative consequences of
the analytic results:

1. the positive-diffusion Brusselator homoclinic profiles obey the amplitude
   and width powers in Theorem B; and
2. sampled members of two reversible zero-energy van der Pol periodic families
   approach the continued homoclinic in initial offset, with physical period
   increment agreeing with the V7 coefficient to about
   \(1.2\times10^{-3}\) in relative error.

This is the concrete bridge

\[
\text{abstract spatial orbit}
\longrightarrow
\text{computed positive-parameter orbit}
\longrightarrow
\text{stationary PDE profile}.
\]

It does not yet supply the next bridge from a stationary profile to temporal
selection, stability, or experimental observation.

## Brusselator: scaling test

The exact scaled system was solved on the symmetric half-line
\(0\le\xi\le24\), with \(P(0)=Q(0)=0\) and a two-dimensional stable-space
projection at the far boundary.  Continuation starts from the midpoint
reconstruction of the certified universal-core homoclinic.

For the displayed samples:

| \(r=d^{1/4}\) | \(d\) | \(\|u-1\|_\infty\) | \(\|v-1\|_\infty\) | \(W_u\) | \(W_v\) |
|---:|---:|---:|---:|---:|---:|
| 0.025000 | \(3.90625\times10^{-7}\) | 0.00305829 | \(3.10977\times10^{-6}\) | 0.0320918 | 0.0831905 |
| 0.035355 | \(1.56250\times10^{-6}\) | 0.00613515 | \(1.24827\times10^{-5}\) | 0.0453613 | 0.117638 |
| 0.050000 | \(6.25000\times10^{-6}\) | 0.0123456 | \(5.02838\times10^{-5}\) | 0.0640839 | 0.166335 |
| 0.070711 | \(2.50000\times10^{-5}\) | 0.0250001 | \(2.04032\times10^{-4}\) | 0.0904370 | 0.235152 |
| 0.100000 | \(1.00000\times10^{-4}\) | 0.0513043 | \(8.40547\times10^{-4}\) | 0.127339 | 0.332357 |
| 0.141421 | \(4.00000\times10^{-4}\) | 0.108457 | 0.00358048 | 0.178401 | 0.469671 |

Fitting the four smallest-\(d\) samples on logarithmic axes gives

| Observable | Computed power | Theorem B power |
|---|---:|---:|
| activator amplitude | 0.505112 | \(1/2\) |
| inhibitor amplitude | 1.005886 | \(1\) |
| activator half-height width | 0.249131 | \(1/4\) |
| inhibitor half-height width | 0.249852 | \(1/4\) |

The scaled curves

\[
U_r(\xi)=\frac{u_d(x)-1}{d^{1/2}},\qquad
V_r(\xi)=\frac{v_d(x)-1}{d},\qquad
\xi=\frac{x}{d^{1/4}}
\]

nearly collapse, which is the visual form of convergence to the universal
core profile.  All six physical samples remain positive.  Across them, the
normalized scaled-ODE residual is below \(6.8\times10^{-8}\), while the
truncated tail norm is below \(5.8\times10^{-7}\).

The separate domain check at \(r=0.1\) uses
\(L_\xi=16,20,24,28\).  The tail norm decreases from
\(1.63\times10^{-4}\) to \(3.29\times10^{-8}\); all reported common
observables agree between \(L_\xi=24\) and \(28\) to double-precision scale.

## van der Pol: winding and period law

The exact central system was evaluated at

\[
(r,a_2,\epsilon)=(0.08,0,1),\qquad d=r^4=4.096\times10^{-5},\qquad a=1.
\]

On \(\operatorname{Fix}\mathcal R\), the zero-energy set is the union of the
vertical branch \(U=0\) and the nonvertical branch

\[
P=Q=0,\qquad
V=-\frac13U^2+\frac{r^2}{12}U^3.
\]

The latter is the homoclinic-center branch used to parameterize the initial
point.  The second symmetry point of family B lies on the vertical branch.

A bracketed first stage selects the desired reversible family.  Family A uses
a transverse \(Q=0\) event with \(P\) as scalar residual.  Because \(Q=0\) is
nontransverse at the family-B target, family B instead uses the transverse
\(P=0\) event with \(Q\) as residual.  A two-variable refinement then solves
\(P(T)=Q(T)=0\).  Reflection gives the full period
\(2T\), and the physical period is \(L=2rT\).

| Family | Relative winding \(k\) | Physical period \(L\) | Physical action | closure residual |
|:---:|---:|---:|---:|---:|
| A | 0 | 0.740101 | \(4.73393\times10^{-5}\) | \(2.45\times10^{-13}\) |
| A | 1 | 1.448810 | \(4.79082\times10^{-5}\) | \(2.92\times10^{-12}\) |
| A | 2 | 2.159661 | \(4.79093\times10^{-5}\) | \(2.49\times10^{-11}\) |
| B | 0 | 1.093207 | \(4.79344\times10^{-5}\) | \(3.92\times10^{-13}\) |
| B | 1 | 1.804230 | \(4.79093\times10^{-5}\) | \(1.00\times10^{-11}\) |

Using a separate intercept for each reversible family and one common slope
gives

\[
\frac{\Delta L}{\Delta k}=0.71002834.
\]

Here \(c=0\), hence \(\beta=2^{-1/2}\), and V7 predicts

\[
\frac{2\pi r}{\epsilon^{1/4}\beta}=0.71086127.
\]

The relative discrepancy is \(1.17\times10^{-3}\).  The plot also shows what
the winding integer means physically: increasing \(k\) adds a small
near-equilibrium spatial oscillation and lengthens the nearly homogeneous
part of the profile.  It does not simply add another macroscopic pulse; the
macro-pulse count is controlled by the code word length.

Step-halving the periodic integration gives independent closure residuals
between \(5.0\times10^{-13}\) and \(6.0\times10^{-11}\).  The Hamiltonian
drift of every displayed periodic half-orbit is below \(7.3\times10^{-14}\).

## Turing and canard interpretation

The context figure deliberately separates three facts.

- The exact formulas shown are finite-wavenumber neutral/Turing curves, not a
  numerical continuation of the stationary branches.  For van der Pol,
  \(a=1\) is also the \(k=0\) Hopf/marginality line, and near-zero modes are
  already weakly unstable at the displayed finite-wave neutral curve.  The
  computed paths are located relative to the curves only; no branch
  connection to a Turing point is proved.
- The \(K_2\to K_1\to\) outer algebraic route is canard-organized geometry.
  The local high winding plotted here is saddle-focus geometry and is not, by
  itself, a canard.
- The bounded periodic profiles use returns.  The pole and outer algebraic
  branches are exits and therefore do not themselves define bounded patterns.

Consequently these computations explain the shapes and spacing of stationary
patterns, but do not determine which profile a time-dependent PDE solution
selects.  That question requires temporal spectrum/Bloch--Evans calculations
and direct time evolution.

## Reproduction and artifacts

```bash
python3 numerics/run_atlas.py
python3 numerics/check_convergence.py
python3 -m unittest numerics/test_numerics.py
```

The output directory `numerics/results/atlas/` contains five figures in PDF,
SVG, and PNG formats, the sampled arrays, `manifest.json`, and
`convergence.json`.  The manifest records parameters, solver settings,
software versions, source hashes, residuals, and explicit nonclaims.
