# Exhaustive positive-parameter two-end theorem and stationary PDE coding

**Evidence status: Proved.**  This note proves claims V6 and V7.  It first
replaces both finite end gates of V2 on whole compact event cells, pulls the
actual end and return faces to one source section, and proves a componentwise
exhaustive high-winding first-event relation.  It then attaches the genuinely
positive pole finite part from V3 and the genuinely positive algebraic
length/action finite parts from V5A.  Finally, it translates the bounded
spatial codes back to stationary solutions of the original PDE.

The analytic high-winding and coding modules are imported with a strict
boundary in
[RETURN_EXIT_CODING_IMPORT.md](RETURN_EXIT_CODING_IMPORT.md).  In particular,
the flagship's concrete end compactifications are not used here.

## 1. Final parameter box, physical conventions, and source section

The radius is selected in the following noncircular order.  First, at the
closed V2/V5 comparison face \(r=0\), fix the algebraic, homoclinic, and
return pullback cells and their positive clean-arrangement margins.  Next,
use the \(O(r)\) V2/V5 comparison to choose \(r_{\rm V}>0\) once.  Then
freeze the positive box below and rerun V3--V5A on it.  Only after that box
is fixed do we thicken the pole window by V3 compactness and take its
positive margins.  The radius is not decreased again.  Retain the notation

\[
 \mathcal P_{\rm V}
 =\left[\frac12r_{\rm V},r_{\rm V}\right]
   \times[-A,A]\times[\epsilon_-,\epsilon_+],
 \qquad \mu=(r,a_2,\epsilon),
\tag{1}
\]

with

\[
 d=r^4>0,\qquad \delta=r^2>0,\qquad
 a=1+\sqrt\epsilon\,r^3a_2,\qquad \epsilon>0.
\tag{2}
\]

The phrase "rerun" is important: the box in (1) need not be a subset of a
preceding annular box.  The existential constructions V3--V5A apply with
the new positive lower bound \((r_{\rm V}/2)^2\); no pole thickness or pole
margin at \(r=0\) is used.  The comparison face selects the central and
algebraic geometry only.

The physical stationary system and primitive are

\[
 \delta u_{\mathsf x}=p,\qquad
 \delta p_{\mathsf x}=f(u)-v,\qquad
 v_{\mathsf x}=q,\qquad
 q_{\mathsf x}=\epsilon(u-a),
 \qquad f(u)=\frac13u^3-u,
\tag{3}
\]

\[
 \lambda_\delta=\epsilon p\,du-\delta^{-1}q\,dv.
\tag{4}
\]

In the universal central chart, the exact clock and primitive identities are

\[
 d\mathsf x=r\epsilon^{-1/4}\,d\xi,
 \qquad
 \lambda_\delta=\epsilon^{9/4}r^5(P\,dU-Q\,dV).
\tag{5}
\]

Let \((\phi,\nu)\) be the V2 exact action--angle coordinates on the fixed
physical incoming saddle face, expressed in the common transported phase
lift.  Once \(N\) and \(\nu_N\) have been chosen below, put

\[
 \Sigma_\sigma=I_s^\circ\times
   \{\nu:0<\sigma\nu<\nu_N\},\qquad
 \Sigma_N=\Sigma_+\sqcup\Sigma_-.
\tag{6}
\]

The half-open residual-angle interval inherited from V2 assigns every point
of (6) one current sign \(\sigma\) and one winding \(n\ge N\).  No point on
an angular cut is duplicated.  This \(\Sigma_N\), rather than the
zero-action true-unstable source circle \(S_\mu(\phi)\) used to anchor V3
and V5, is the high-winding source section.

For later rates, fix

\[
 0<\varkappa<
 \inf_{\mu\in\mathcal P_{\rm V}}
 {2\pi\alpha_\mu\over\beta_\mu},
\tag{7}
\]

where

\[
 \alpha_\mu=\frac12\sqrt{2+c_\mu},\qquad
 \beta_\mu=\frac12\sqrt{2-c_\mu},\qquad
 c_\mu=2ra_2+\sqrt\epsilon\,r^4a_2^2.
\tag{8}
\]

## 2. Theorems V6 and V7

### Theorem V6: exhaustive two-end return--first-exit relation

There are an integer \(N\), a width \(\nu_N>0\), and constants
\(0<\vartheta<1\), \(m_{\rm cf}>0\), \(m_{\rm ev}>0\), and \(C<\infty\),
uniform on (1), with the following properties.

1. **One actual limiting event arrangement.**  For each source sign, all
   actual outgoing faces, the actual algebraic entrance, the actual open
   pole window, and, inside the homoclinic aperture, all return-band faces
   pull back to one compact reference cell

   \[
    Z_{\rm exit}=I_s\times\overline J_0.
   \tag{9}
   \]

   The pullbacks are state-\(C^3\), mixed-\(C^2\) in \(\mu\), clean and
   neat at the boundary.  Every active conormal least singular value, empty
   incidence gap, event speed, inactive sign, earlier-event exclusion,
   strict event-order gap, flow-domain buffer, and anchor-to-boundary
   distance is at least \(m_{\rm ev}\) after fixed normalization.  Their
   labelled connected sign strata exhaust (9).  Common faces and corners
   are separate lower-dimensional strata with one fixed priority.

2. **Literal component census.**  The physical flow gives the disjoint
   identity

   \[
   \begin{aligned}
    \Sigma_N={}&
      \bigsqcup_{\substack{\sigma,\sigma'\in\{+,-\}\\n\ge N}}
         \mathcal V_{\sigma,n}^{\sigma'}
      \ \sqcup\!
      \bigsqcup_{\substack{\sigma\in\{+,-\}\\n\ge N}}
         \mathcal I_{\sigma,n}\\
     &\sqcup
      \bigsqcup_{\substack{\mathsf t\in
          \{\mathrm a,\mathrm p,\mathrm{out},\mathrm{rbox}\}\\
          \sigma\in\{+,-\},\ n\ge N,\ \ell}}
          E_{\mathsf t,\sigma,n,\ell}.
   \end{aligned}
   \tag{10}
   \]

   Every union in (10) is over nonempty connected components only.  Every
   point has exactly one winding, current sign, connected-cell label, and
   first event.  Every return also has exactly one next sign.  The stable
   cut \(\mathcal I_{\sigma,n}\) is a first-exit face and belongs to neither
   adjacent return component.  There is no unnamed high-winding component.

   For every \((\sigma,n)\), both target-sign returns and their common cut
   are nonempty.  Fix the unique limiting connected cells containing the
   actual end anchors and denote their labels by

   \[
    (\sigma_{\rm a},\ell_{\rm a}),\qquad
    (\sigma_{\rm p},\ell_{\rm p}).
   \tag{11}
   \]

   Then
   \(E_{\mathrm a,\sigma_{\rm a},n,\ell_{\rm a}}\) and
   \(E_{\mathrm p,\sigma_{\rm p},n,\ell_{\rm p}}\) are nonempty for every
   \(n\ge N\).  No nonemptiness is asserted for every other source sign or
   cell label.

3. **Cross forms and mixed two-jets.**  For
   \(a_\star=(\sigma,n,\sigma')\), the return map has a completed cross
   form on one fixed rectangle,

   \[
    x'=f_{a_\star}(x,y'),\qquad y=g_{a_\star}(x,y'),
   \tag{12}
   \]

   and, with

   \[
    \varepsilon_{\mu,a_\star}=\nu_N^{-1}
       \exp\!\left(-{2\pi\alpha_\mu\over\beta_\mu}n\right),
    \qquad \widetilde g_{a_\star}
       =g_{a_\star}/\varepsilon_{\mu,a_\star},
   \tag{13}
   \]

   the cross-form contraction is at most \(\vartheta\) and

   \[
    m_{\rm cf}\le\widetilde g_{a_\star}\le m_{\rm cf}^{-1},
    \qquad g_{a_\star}\le1-m_{\rm cf},
    \qquad \|Dg_{a_\star}\|_{C^1}
       \le C\varepsilon_{\mu,a_\star}.
   \tag{14}
   \]

   For each sign pair there are limiting cross forms and

   \[
    \|f_{a_\star}-f_{\mu,\sigma,\sigma',\infty}\|_{C^2_{z,\mu}}
    +\|\widetilde g_{a_\star}
       -\widetilde g_{\mu,\sigma,\sigma',\infty}\|_{C^2_{z,\mu}}
    \le C(1+n)^3e^{-\varkappa n}.
   \tag{15}
   \]

   Here and below mixed \(C^2_{z,\mu}\) means all derivatives
   \(D_z^iD_\mu^j\) with \(i+j\le2\), \(j\le2\), in the fixed component
   charts.

4. **Physical spatial length and action.**  Put

   \[
    c_{\mathsf x}(\mu)=r\epsilon^{-1/4},\qquad
    c_{\mathsf A}(\mu)=\epsilon^{9/4}r^5.
   \tag{16}
   \]

   Let

   \[
    \iota_{\mu,a_\star}(x,y')
       =(x,g_{a_\star}(x,y'))
   \]

   be the source inclusion from the fixed cross-form rectangle.  In
   (17)--(18), \(L_{a_\star}\), \(\widehat L_{a_\star}\), and
   \(\mathscr A_{a_\star}\) denote the physical branch functions pulled
   back by \(\iota_{\mu,a_\star}\).  They satisfy

   \[
    L_{a_\star}
      ={2\pi c_{\mathsf x}(\mu)\over\beta_\mu}n
        +\widehat L_{a_\star},
    \qquad
    \mathscr A_{a_\star}=\int_{a_\star}\lambda_\delta,
   \tag{17}
   \]

   and, for each sign pair, have mixed-\(C^2\) limits with

   \[
   \begin{aligned}
    &\|\widehat L_{a_\star}
       -\widehat L_{\mu,\sigma,\sigma',\infty}\|_{C^2_{z,\mu}}
     +\|\mathscr A_{a_\star}
       -\mathscr A_{\mu,\sigma,\sigma',\infty}\|_{C^2_{z,\mu}}\\
    &\hspace{42mm}\le C(1+n)e^{-\varkappa n}.
   \end{aligned}
   \tag{18}
   \]

   Each first-exit family has a normalized physical length and action.  At
   the algebraic end these are, with the V5A coordinate
   \(Q=z^{-2}\),

   \[
   \begin{aligned}
    L^{\rm ren}_{\mathrm a}
      &=\lim_{Q\to\infty}
        \{L_{\mathrm{source}\to Q}-C_{\mathsf x,\mu}(Q)\},\\
    \mathscr A^{\rm ren}_{\mathrm a}
      &=\lim_{Q\to\infty}
        \left\{\int_{\mathrm{source}\to Q}\lambda_\delta
                     -C_{\mathsf A,\mu}(Q)\right\},
   \end{aligned}
   \tag{19}
   \]

   where \(C_{\mathsf x,\mu}\) and \(C_{\mathsf A,\mu}\) are the complete
   V5A reference-tail integrals, not finite Taylor polynomials.  Their
   leading sizes are

   \[
    C_{\mathsf x,\mu}(Q)
      =q_*(\epsilon)^{-1}Q^{1/2}+O_{C^2_\mu}(\log Q),
    \qquad
    C_{\mathsf A,\mu}(Q)
      =-{q_*(\epsilon)\over5\delta}Q^{5/2}
         +O_{C^2_\mu}(Q^2).
   \tag{20}
   \]

   At the pole, physical remaining distance
   \(s=\mathsf x_{\rm b}-\mathsf x\) is finite and no length counterterm is
   used.  Here and below
   \(\log s=\log(s/s_{\rm ref})\) with the frozen nondimensional reference
   \(s_{\rm ref}=1\).  The action is

   \[
    \mathscr A^{\rm ren}_{\mathrm p}
      =\lim_{s\downarrow0}\left[
       \int_{\mathrm{source}}^{\mathsf x_{\rm b}-s}\lambda_\delta
       -2\epsilon\delta^3s^{-3}
       +2\epsilon\delta s^{-1}
       -\sqrt6\,\epsilon Z_0\log s\right].
   \tag{21}
   \]

   Lateral, return-box, and cut events use ordinary finite length/action and
   zero end counterterm.  For every fixed nonempty terminal cell,

   \[
   \begin{aligned}
    &\left\|L^{\rm ren}_{\mathsf t,\sigma,n,\ell}
       -{2\pi c_{\mathsf x}(\mu)\over\beta_\mu}n
       -L^{\rm ren}_{\mathsf t,\sigma,\infty,\ell}
      \right\|_{C^2_{z,\mu}}\\
    &\quad+
      \|\mathscr A^{\rm ren}_{\mathsf t,\sigma,n,\ell}
       -\mathscr A^{\rm ren}_{\mathsf t,\sigma,\infty,\ell}
      \|_{C^2_{z,\mu}}
       \le C(1+n)^3e^{-\varkappa n}.
   \end{aligned}
   \tag{22}
   \]

5. **Exact branch cocycle.**  On every finite branch
   \(P_\gamma:\Sigma^-_\gamma\to\Sigma^+_\gamma\),

   define the shifted physical Hamiltonian

   \[
    H_{\rm ph}=-{\mathcal G-\mathcal G(O)\over\delta},
    \qquad H_{\rm ph}(O)=0.
   \tag{23}
   \]

   At each fixed \(\mu\), before restricting energy, the exact identity is

   \[
    P_\gamma^*\lambda_\delta-\lambda_\delta
       =d_Z\mathscr A_\gamma+T_\gamma\,d_ZH_{\rm ph}.
   \tag{24}
   \]

   Hence on the translated zero-energy source and target sections,

   \[
    P_\gamma^*(\lambda_\delta|_{\Sigma^+_\gamma})
       -\lambda_\delta|_{\Sigma^-_\gamma}
       =d_{\Sigma^-_\gamma}\mathscr A_\gamma.
   \tag{25}
   \]

   For two composable branches,

   \[
    \mathscr A_{\gamma_2\circ\gamma_1}
       =\mathscr A_{\gamma_1}
         +\mathscr A_{\gamma_2}\circ P_{\gamma_1}.
   \tag{26}
   \]

   At an end, (26) is imposed at every finite cutoff first; only the final
   terminal term receives the counterterm in (19) or (21), and only then is
   the cutoff limit taken.  Moving any subordinate finite cut transfers one
   actual finite orbit segment between adjacent terms, so the total is
   unchanged.  Admissible exact gauges whose gauge functions have the
   controlled mixed terminal limits required in V3/V5A, and
   event-preserving slides through compact event-free tubes, add only
   endpoint coboundaries.  Closed spatial actions are invariant under those
   admissible changes.

### Theorem V7: coding and stationary PDE patterns

For every \(\mu\in\mathcal P_{\rm V}\), let \(\mathcal G_N\) be the
two-vertex graph with vertices \(\{+,-\}\) and all edges

\[
 a_\star=(\sigma,n,\sigma'),\qquad
 \sigma,\sigma'\in\{+,-\},\qquad n\ge N.
\tag{27}
\]

Then:

1. the two-sided edge shift \(\Sigma_{\mathcal G_N}\) is homeomorphic and
   conjugate to the set \(K_\mu\subset\Sigma_N\) whose return iterates exist
   in both directions; one-sided future words give stable plaques, and every
   point outside the forward trapped set has a finite return word followed by
   its unique first-exit component;
2. the physical roof and action potentials on recurrent codes have summable
   variations;
3. every primitive periodic edge word gives one bounded spatially periodic
   orbit of (3), hence a smooth spatially periodic stationary solution of
   the PDE; every nonperiodic bi-infinite word gives a bounded, nonperiodic
   stationary spatial solution;
4. in the simultaneous stable/unstable section normalization, every finite
   admissible edge word admits a unique closed-box solution with its first
   endpoint on the selected primary unstable-image trace in the completed
   section and its last endpoint on the local stable trace;
   the resulting orbit is homoclinic to the homogeneous state and makes the
   prescribed finite sequence of high-winding visits through the global
   homoclinic tube.  Arbitrarily long words therefore give localized
   multipulse stationary PDE profiles; and
5. the coding is a statement about the independent spatial variable
   \(\mathsf x\).  Its symbolic dynamics or spatial entropy is not temporal
   chaos of the parabolic PDE, and no temporal spectral or nonlinear
   stability is asserted.

For a fixed cyclic sign word
\(\boldsymbol\sigma=(\sigma_0,\ldots,\sigma_m)\),
\(\sigma_m=\sigma_0\), and windings
\(\mathbf n=(n_0,\ldots,n_{m-1})\), assume that the induced cyclic edge
word \(a_j=(\sigma_j,n_j,\sigma_{j+1})\) is primitive and put

\[
 \Delta_{\varkappa}(\mathbf n)
  =\max_j(1+n_j)^3e^{-\varkappa n_j}.
\tag{28}
\]

The corresponding periodic stationary profile has physical spatial period
and closed action

\[
 \begin{aligned}
  L(\gamma_{\mathbf n})
   &={2\pi r\over\epsilon^{1/4}\beta_\mu}
       \sum_{j=0}^{m-1}n_j
     +\mathcal L_{\boldsymbol\sigma,\mu}
     +O(\Delta_{\varkappa}(\mathbf n)),\\
  \oint_{\gamma_{\mathbf n}}\lambda_\delta
   &=\mathcal A_{\boldsymbol\sigma,\mu}
     +O(\Delta_{\varkappa}(\mathbf n)).
 \end{aligned}
\tag{29}
\]

The constants are the sums of the limiting branch potentials evaluated at
the limiting cyclic cross-form fixed point.  A nonempty finite cylinder of
return windings \(n_0,\ldots,n_{m-1}\), followed by a terminal winding
\(n_m\), similarly has

\[
 \begin{aligned}
  L^{\rm ren}_{\rm exit}
   &={2\pi r\over\epsilon^{1/4}\beta_\mu}
       \sum_{j=0}^{m}n_j
     +\mathcal L^{\rm exit}
     +O\!\left(\max_{0\le j\le m}
         (1+n_j)^3e^{-\varkappa n_j}\right),\\
  \mathscr A^{\rm ren}_{\rm exit}
   &=\mathcal A^{\rm exit}
     +O\!\left(\max_{0\le j\le m}
         (1+n_j)^3e^{-\varkappa n_j}\right),
 \end{aligned}
\tag{30}
\]

in the fixed mixed-\(C^2\) component chart.  Formula (30) is asserted only
for cylinders that are nonempty; it does not infer every terminal label
after every finite word.  The implicit constants in (29)--(30) may depend
on the fixed cyclic-word or finite-path length \(m\); no estimate uniform in
an increasing number of composed branches is asserted.

## 3. Construction of the actual end events on whole cells

V2 supplies compact outgoing and return bands \(B^u_\mu\) and
\(B^r_\mu\), a compact homoclinic flight between their designated
apertures, the stable cut on \(B^r_\mu\), and a finite clean arrangement
with normalized margin at least \(m_0/2\).  Its two end labels at this stage
are only finite gates.  We now replace those labels before taking any
high-winding limit.  Unless an energy-thick identity is explicitly written,
all cells and section maps in Sections 3--4 are restricted to the translated
zero-energy surface \(H_{\rm ph}=0\).

### 3.1 The algebraic event hypersurface

On the fixed V5 central section, choose a compact subordinate patch

\[
 \mathcal A_\mu
  \Subset\mathcal W^{\rm match}_{\mathrm{out},\mu}
       \cap\{H_{\rm ph}=0\}
\tag{31}
\]

which contains the V5 selected connection in its relative interior.  Choose
it small enough that its V5 arrival labels on the V5A cut \(z=z_*\) lie in
the interior of the interval \(I_\beta\) used by V5A.  This is possible
because the selected label is interior and the compact arrival map is
mixed-\(C^2\).  More precisely, choose a small ambient neighborhood
\(\mathcal U_{{\rm c},\mu}\) of the selected target point in the fixed
central section and take
\(\mathcal A_\mu\Subset\mathcal U_{{\rm c},\mu}\).  Shrink this
neighborhood so that every intersection of \(\mathcal A_\mu\) with the
source trace is the image of a point in the preselected phase--time shooting
domain used in V5, equations (58)--(60).  We do not claim that the
one-dimensional event patch is contained in the one-dimensional source
trace; they meet transversely.  Thus (31) is the slice of the matched graph
by both that section and the translated zero-energy surface; no energy-thick
conclusion from V5A is being used.

Let \(g_{\mathrm a,\mu}=0\) be a cooriented defining function for (31).
Pull it backward by the common finite first-hit maps through the V5 central
flowbox to \(B^u_\mu\), retain the same symbol for the pulled-back defining
function, and denote the pulled-back event patch by
\(\widehat{\mathcal A}^{u}_\mu\Subset B^u_\mu\).  V5 gives

\[
 \|g_{\mathrm a,\mu}-g_{\mathrm a,0}\|_{C^2}
   \le C r
\tag{32}
\]

after the fixed flowbox pullback, with two parameter derivatives bounded.
Nonvanishing of this target conormal alone would not prove transversality
after pullback to the limiting source.  Let
\(\widetilde g_{{\rm c},\mu}\) be the V5 flowbox extension and let
\(h_{\rm c}=0\) define the fixed central section.  Along
\(y_\mu(\phi,t)=\Phi_\mu^tS_\mu(\phi)\), V5 proves throughout the
preselected neighborhood, on the zero set of the two shooting equations,

\[
 \det D_{(\phi,t)}
 \begin{pmatrix}
  \widetilde g_{{\rm c},\mu}(y_\mu(\phi,t))\\
  h_{\rm c}(y_\mu(\phi,t))
 \end{pmatrix}
   =s_\mu\chi_\mu,
 \qquad |s_\mu|\ge s_*>0,
 \qquad |\chi_\mu|\ge\chi_*>0.
\tag{A-inc}
\]

Here \(s_\mu=dh_{\rm c}(F_\mu)\) is the section speed and
\(\chi_\mu\) is the source-phase incidence, not the outer exchange
pairing.  The phase coordinate in this shooting neighborhood and the phase
coordinate of each signed limiting source-exit template are related by one
fixed compact state-\(C^3\) coordinate change with uniformly bounded
inverse.  Shrinking \(\mathcal A_\mu\) inside that already selected
neighborhood, but not changing the parameter box, therefore gives

\[
 \inf_{\substack{\mu\in\mathcal P_{\rm V},\ \sigma\in\{+,-\}\\
       Z\in Z_{\rm exit}:\;
       \Pi_{\mu,\sigma,\infty}(Z)
          \in\widehat{\mathcal A}^{u}_\mu,\;
       g_{{\rm a},\mu}(\Pi_{\mu,\sigma,\infty}(Z))=0}}
 \left|d_Z\bigl(g_{{\rm a},\mu}
              \circ\Pi_{\mu,\sigma,\infty}\bigr)(Z)\right|
 \ge c_{\rm a}>0
\tag{A-pb}
\]

whenever this incidence is nonempty.  Patch-boundary and simultaneous-face
ranks are chosen after this pullback in Section 4.  Every
point of (31) follows the unique V5 matching tube into the V4 future-staying
graph and hence satisfies \(u\to+\infty\) only at infinite physical
distance.  Thus the entire pulled-back patch, rather than one shooting
orbit, is a genuine algebraic terminal event.

Choose a compact range for its tangential boundary inside the old V2 gate
flowbox; the actual regular level is fixed after source pullback in Section
4.  Points in the adjacent complement are assigned to named finite lateral
flowbox exits.  The old algebraic gate is no longer retained as a terminal
label.

### 3.2 The open pole window

Choose a closed phase subarc

\[
 I_{\rm p}'\Subset(-0.2,0.2)
\tag{33}
\]

containing the V3 anchor.  V3 proves on the whole compact family
\(S_\mu(I_{\rm p}')\) a unique first hit of \(x=10\), strict absence of an
earlier pole, strict entry into its invariant cone, and then entry into the
open local pole basin.  All of these inequalities have positive uniform
margins.

The finite first-hit map is state-\(C^3\) and mixed-\(C^2\).  Openness of
the cone and local basin and compactness of
\(\mathcal P_{\rm V}\times I_{\rm p}'\) therefore give one
\(\eta_{\rm p}>0\) such that the two-dimensional product window

\[
 \mathcal P^u_\mu
 =\{(\phi,\nu_u):\phi\in\operatorname{int}I_{\rm p}',
                         |\nu_u|<\eta_{\rm p}\}
 \Subset B^u_\mu
\tag{34}
\]

has the same unique first-hit, cone-entry, and basin-entry conclusions on
its closure after replacing the strict inequalities in (34) by a slightly
smaller closed product.  This is the required open pole aperture.  The
local stable projection of V3 is mixed-\(C^2\) on this compact thickening,
so its end labels \((Z_0,W_0,\kappa)\), finite remaining distance, and pole
finite part are mixed-\(C^2\) on every pole component.

One spare label derivative, needed below for a quantitative mixed-\(C^2\)
composition estimate, follows from the same regular-singular equation.  At
fixed \(s\), the V3 Green operator

\[
 (\mathscr K f)(s)
  =s^{-1}\int_0^s t^4
       \left(\int_0^t\rho^{-5}f(\rho)\,d\rho\right)dt
\tag{35}
\]

is bounded on the V3 conormal remainder space.  Differentiate its
fixed-point equation once more in the finite entry labels, allowing all
mixed derivatives \(D_\zeta^iD_\mu^j\) with
\(i+j\le3\), \(j\le2\).  The contraction part is unchanged; the only
limited-smoothness coefficient \(s^4\log s\) is independent of the entry
labels, and every differentiated **state-equation forcing** retains the
conormal bound \(Cs^5(1+|\log s|)^2\).  The inverse chart at a fixed
positive pole section is uniformly state-\(C^3\) and parameter-\(C^2\).
After the resulting state jet is substituted into the action density and
the three singular density terms are removed, every differentiated
**density remainder** is bounded by \(C(1+|\log s|)^2\), which is
integrable.  Differentiating the finite-part formula under that integrable
majorant therefore gives

\[
 \sup_{i+j\le3,\ j\le2}
 \left(
  \|D_\zeta^iD_\mu^jL_{\rm p}\|
  +\|D_\zeta^iD_\mu^j\mathscr A_{\rm p}^{\rm ren}\|
 \right)<\infty
\tag{36}
\]

on the compact thickened entry window.  No extra derivative in the
singular variable \(s\) is asserted.  This is precisely the spare state
derivative required to compose the pole potential with two \(C^2\)-close
arrival maps while retaining their exponential rate in a mixed-\(C^2\)
norm.

Use fixed product-coordinate faces for the boundary of (34).  Relabel the
remainder of the old V2 pole-gate flowbox by named finite lateral exits.  A
small transverse lateral face placed before the uncertified continuation
makes this a first exit of the prescribed physical tube; no global fate is
claimed for a point after that lateral exit.

### 3.3 One finite actual arrangement

The V2 phase gaps

\[
 0.052407,\qquad0.16324,\qquad0.110835
\tag{37}
\]

separate the algebraic, homoclinic, and pole traces in the common lift.
Choose provisional algebraic and pole neighborhoods with closures strictly
inside those gaps.  There are only finitely many old faces.  The actual
tangential and lateral levels are selected *after* all faces have been
pulled back to \(Z_{\rm exit}\), by the successive Sard construction in
Section 4; target-flowbox transversality by itself is not used as a
substitute for source-level neatness.

The selection order is the one fixed in Section 1.  At the comparison face
\(r=0\), first perform the source-level refinement of the algebraic,
homoclinic, and return faces described below.  It gives a number
\(m_{\rm core}>0\), the minimum of the normalized source-pullback ranks,
empty-incidence gaps, phase separations, containment margins, hit speeds,
inactive signs, event-order gaps, flow-domain buffers, and anchor distances
for this finite core family.  Equations (32) and (A-pb), together with the
V2 continuation estimates, then determine \(r_{\rm V}\) so that the moving
core family remains within the corresponding controlled-isotopy
neighborhood.  At this point the positive box (1) is frozen.

Only on that frozen box do we invoke V3 to choose \(\eta_{\rm p}\) and the
pole product window (34).  Its phase faces lie inside a component separated
from the algebraic and homoclinic closures by (37); its normal faces are the
fixed product levels \(\nu_u=\pm\eta_{\rm p}\).  V3 compactness gives the
positive first-hit, cone-entry, basin-entry, and anchor margins for this
whole window.  Product coordinates and the already fixed phase gaps give
the remaining geometric pole margins directly.  These pole margins are not
obtained from an \(r\to0\) pole thickening.  The radius is not decreased
again.  Section 4 takes the final finite minimum \(m_{\rm ev}>0\) and proves
the limiting source arrangement and its exact-winding continuation.

## 4. Pullback to one source cell and high-winding stratification

We first freeze the target H1 constants.  Write the compact homoclinic
transition in the V2 exact section coordinates as

\[
 (\bar\phi,\bar\nu)
 =\bigl(F^{\rm hom}_\mu(\psi,\nu_u),
        G^{\rm hom}_\mu(\psi,\nu_u)\bigr).
\tag{H1}
\]

V2 transversality modulo flow is exactly
\(\partial_\psi G^{\rm hom}_\mu\ne0\) after fixing the transverse section
directions.  Choose a compact interval \(J_\psi\) about the continued
homoclinic point and then the final parameter box so that

\[
 d_*:=\inf_{\mu,\psi\in J_\psi}
       |\partial_\psi G^{\rm hom}_\mu(\psi,0)|>0.
\tag{H1'}
\]

Its image contains one common interior interval
\([-\nu_*,\nu_*]\).  Choose \(I_s\) inside the V2 proper phase arc so
that, for both source signs, the lifted solution of the second matching row
stays a positive distance from \(\partial\overline J_0\).  Compactness gives
one target-range endpoint margin and one lifted-angle margin.  The finite
transition and these constants are mixed-\(C^2\) in \(\mu\).  Thus
\(J_\psi,I_s,\nu_*,d_*\) are fixed before \(n\).  This H1 operator is the
homoclinic return selector; it is not the V5 outer matching operator.

Let

\[
 \Pi_{\mu,\sigma,\infty}:Z_{\rm exit}\longrightarrow B^u_\mu
\tag{38}
\]

be the V2 signed limiting source-exit template.  Pull back the functions in
the following table.

| physical target | defining data pulled to \(Z_{\rm exit}\) | source |
|---|---|---|
| actual algebraic entrance | \(g_{\mathrm a,\mu}\circ\Pi_{\mu,\sigma,\infty}\) and its patch-boundary faces | V5 and (31)--(32) |
| actual pole aperture | the four product-boundary functions of (34) composed with \(\Pi_{\mu,\sigma,\infty}\) | V3 and (33)--(34) |
| homoclinic aperture and outgoing laterals | their V2 functions composed with \(\Pi_{\mu,\sigma,\infty}\) | V2 |
| re-entry, target signs, stable cut, return laterals | return-band functions composed first with the compact homoclinic flight and then with \(\Pi_{\mu,\sigma,\infty}\) | V2 |

Here is the source-level H2 verification.  For each \(\sigma\), enumerate
the rows of the table and all of their patch and lateral boundary functions
as

\[
 \mathscr h^0_\sigma
   =(h^0_{1,\sigma},\ldots,h^0_{q,\sigma})
       \quad\hbox{on }Z_{\rm exit},
 \qquad
 \mathbf r_Z=(r_1^Z,\ldots,r_4^Z),
\tag{H2-ref}
\]

where \(\mathbf r_Z\) are fixed boundary defining functions for the four
sides of the rectangle.  The superscript \(0\) means *reference
arrangement*: its algebraic, homoclinic, and return rows are the \(r=0\)
core pullbacks fixed before choosing \(r_{\rm V}\), while its pole rows are
the fixed product-coordinate reference faces inserted only after the
positive box and \(\eta_{\rm p}\) have been fixed.  No limiting pole basin
at \(r=0\) is asserted.

The new algebraic patch-boundary and outgoing-lateral levels in (H2-ref) are
chosen on \(Z_{\rm exit}\), not merely in their target flowboxes.  Starting
with the main algebraic face, whose pullback conormal has the bound (A-pb),
apply Sard's theorem successively to the restrictions of each candidate
level function to every compact old face and to every active boundary
tangent stratum.  Because only finitely many restrictions occur, the levels
can be chosen simultaneously regular and away from every old
reference-empty incidence.  Perform the same finite construction, relative
to the homoclinic-cell boundary, for the pulled-back return, cut, and return
lateral levels.  The pre-existing rows in this step are exactly the frozen
V2 clean, neat H2 family.  Thus the procedure neither assumes nor obtains
neatness merely from a target-space flowbox.

For every face set \(S\) and closed boundary face \(B\) whose reference
incidence is nonempty, let \(A^0_{S,B}(Z)\) be the matrix consisting of the
conormals \(D h^0_{j,\sigma}(Z)\), \(j\in S\), together with the active
boundary conormals from \(D\mathbf r_Z(Z)\).  For every reference-empty
pair \((S,B)\), measure the simultaneous zero gap on \(B\).  The successive
regular-value choices, (A-pb), and the frozen V2 H2 margins give

\[
 \begin{aligned}
  \gamma_0
   &:=\min_{\sigma,S,B}
      \inf_{Z\in B\cap\bigcap_{j\in S}\{h^0_{j,\sigma}=0\}}
       s_{\min}\!\left(A^0_{S,B}(Z)
               \big|_{T_Z Z_{\rm exit}}\right)>0,\\
  a_{\rm emp}
   &:=\min_{\substack{\sigma,S,B:\,
              B\cap\bigcap_{j\in S}\{h^0_{j,\sigma}=0\}=\varnothing}}
      \inf_{Z\in B}
       \left(\sum_{j\in S}|h^0_{j,\sigma}(Z)|^2\right)^{1/2}>0.
 \end{aligned}
\tag{H2-rank}
\]

Only compatible face sets are included in the first minimum, and only
nonempty face sets in the second.  The convention is that an absent class
does not enter a finite minimum.  This is precisely the clean/neat rank
test, including the boundary conormals, on the common source rectangle.

For completeness, the pole part of (H2-rank) is direct.  By the proper
phase-arc bound and the compact coordinate inverse fixed in H1, the pullbacks
of its two phase faces are transverse level sets of the common phase
coordinate.
The limiting template has \(\nu_u=0\), so the two product-normal faces
\(\nu_u=\pm\eta_{\rm p}\) are reference-empty and have gap
\(\eta_{\rm p}\).  Equation (37) makes the closures of the algebraic,
homoclinic, and pole apertures pairwise disjoint.  Their complementary
relative interiors are covered by finitely many compact pre-event tubes;
the part outside those tubes ends on the named outgoing or return laterals.
The frozen V2 first-hit package supplies the old and return-tube speeds and
order gaps, (A-inc)--(A-pb) supply the algebraic incidence, and V3 supplies
the pole hit, cone-entry, basin-entry, and earlier-event margins on the
already frozen positive box.  Compactness therefore gives a further
positive finite minimum

\[
 a_{\rm dyn}:=\min\{\hbox{inactive-sign, first-hit speed,
 earlier-event, event-order, flow-buffer, and containment margins}\}>0.
\tag{H2-dyn}
\]

Choose one interior algebraic anchor and one interior pole anchor before
forming connected sign strata.  Their current-sign and connected-component
labels are retained, their distances from all inactive and boundary faces
are positive, and they define the pairs in (11).  This is label uniqueness
inside the chosen finite arrangement, not uniqueness of all physical end
connections.  The labelled sign cells, their common faces, and their
corners exhaust \(Z_{\rm exit}\): every relative interior belongs to one
of the compact pre-event tubes or to a named lateral cell, and the fixed
priority assigns every simultaneous lower-dimensional stratum once.

Now move the core rows from their reference values to the already selected
positive box.  The choice of \(r_{\rm V}\) in Section 3.3 keeps the
algebraic, homoclinic, and return functions inside the controlled
neat-isotopy neighborhood determined by (H2-rank)--(H2-dyn).  Insert the pole rows
directly in their phase-separated product cell and use their independent V3
margins.  Denote the resulting moving limiting pullback family by
\(\mathscr h_{\mu,\sigma}\).  Since this family is compact, all its
nonempty incidence ranks,
empty-incidence gaps, dynamic gaps, aperture separations, and anchor
distances have one lower bound.  Fix

\[
 m_{\rm ev}:={1\over4}\min
  \{\gamma_0,a_{\rm emp},a_{\rm dyn},
       \hbox{all retained positive moving margins}\}>0.
\tag{H2-margin}
\]

All physical face functions and finite first-hit maps can be chosen with
the one spare mixed derivative

\[
 \sup_{\substack{i+j\le3\\j\le2}}
   \|D_Z^iD_\mu^j\mathscr h_{\mu,\sigma}\|<\infty.
\tag{H2-reg}
\]

For the old rows this is part of the state-\(C^5\), parameter-\(C^2\)
V2 finite-flow package; for the algebraic row it follows from the resolved
V5 graph and its compact flowbox, and for the pole rows it is immediate in
the product chart followed by the V3 finite first-hit map.  In particular,
all rows refer to the same physical flow, are state-\(C^3\), and have the
mixed regularity needed below; (H2-reg), rather than the phrase
``mixed-\(C^2\)'' alone, is what preserves the quantitative \(C^2\) rate
under composition.

Let \(\Pi_{\mu,\sigma,n}\) be the exact normalized exit map on the complete
\(n\)-th winding cell.  Choose a rate

\[
 \varkappa<\varkappa_+<
 \inf_{\mu\in\mathcal P_{\rm V}}
 {2\pi\alpha_\mu\over\beta_\mu}.
\tag{39}
\]

The V2 weighted-log local passage, the opposite-endpoint mixed-passage
lemma, and the compact finite flights give the whole-cell estimate

\[
 \|\Pi_{\mu,\sigma,n}-
      \Pi_{\mu,\sigma,\infty}\|_{C^2_{Z,\mu}}
 \le C(1+n)^3e^{-\varkappa_+n}.
\tag{40}
\]

Indeed, clock inversion gives
\(|\nu|\asymp e^{-2\pi\alpha_\mu n/\beta_\mu}\).  Each of two parameter
derivatives produces at most two polynomial powers of \(n\); the strict
rate gap in (39) absorbs them.  Composition with any row of the table has
the same estimate by the chain rule and the uniform spare mixed derivative
(H2-reg); bounded mixed two-jets alone would give qualitative convergence
but would not justify retaining this quantitative \(C^2\) rate.

Increase \(N\) until the right side of (40), after composition with every
finite defining function, is smaller than the controlled-isotopy threshold
set by \(m_{\rm ev}\).  Apply the isotopy first to the whole outgoing cell
and then, relative to its homoclinic-cell boundary, to the pulled-back
return faces.  Compact first-hit stability preserves every strict ordering
inequality.  This gives a componentwise bijection between every limiting
sign cell and every exact \(n\)-cell, including all faces and corners.

The transverse homoclinic in V2 verifies the limiting matching hypothesis
by the frozen Proposition 2.11.  The selector therefore gives both target
signs for every source sign and winding, while \(\bar\nu=0\) gives their
common stable cut.  Applying the frozen complete local decomposition now
proves (10)--(11).  This proof is whole-cell: it does not extrapolate a
component census from the two selected end orbits.

The same clock inversion and finite-dimensional matching equations give
(12)--(15).  Thus items 1--3 of Theorem V6 follow.

## 5. Physical length, the two finite parts, and exact composition

The imported saddle-passage clock is \(\xi\), and its normalized action
uses \(P\,dU-Q\,dV\).  Multiplying by the exact factors (5) gives (16)--
(18); on the positive compact box these factors and all of their parameter
derivatives are bounded.  In a local exact gauge the action density
vanishes quadratically at the saddle, so the action-gluing lemma applies.

On an algebraic component, the compact arrival map from Section 3.1 lands
inside the V5A label interval.  Compose the finite source-to-\(z_*\) branch
with the actual V5A tail at a finite value of \(Q\).  Ordinary physical
length and line-integral additivity give one exact equality there.  Subtract
the reference integrals \(C_{\mathsf x,\mu}(Q)\) and
\(C_{\mathsf A,\mu}(Q)\) from that terminal tail only.  V5A gives the
mixed-\(C^2\) limits (19)--(20), including composition with the moving
arrival label.

On a pole component, Section 3.2 lands in one compact V3 stable-fiber
block.  The physical remaining distance is finite.  V3 gives the density

\[
 \lambda_\delta(\partial_{\mathsf x})
  ={6\epsilon\delta^3\over s^4}
   -{2\epsilon\delta\over s^2}
   -{\sqrt6\,\epsilon Z_0\over s}
   +O_{C^2}((1+|\log s|)^2),
\tag{41}
\]

whose integral yields exactly the subtraction in (21).  Again, compose at
finite \(s>0\), subtract only from the terminal pole segment, and then take
\(s\downarrow0\).

The finite central matching data vary from their limiting data by (40).
Composing these data with the mixed-\(C^2\) end potentials proves (22).
For the algebraic end, V5A already supplies one spare total derivative; for
the pole it is (36).  Thus the composition estimate retains the explicit
rate after two derivatives.  Equation (24) is the ambient endpoint
derivative of one orbit integral; its restriction proves (25), and
splitting the same integral proves (26).  The moving-cut identities of V3,
V5, and V5A show that all intermediate segment transfers cancel exactly.
This proves Theorem V6(4)--(5).

For a fixed finite itinerary, repeated use of (26) gives (30).  For a
cyclic word, the cross-form equations on the product of its section
rectangles are a contraction with constant at most \(\vartheta\).  Their
fixed point differs from the limiting cyclic fixed point by
\(O(\Delta_\varkappa)\).  Summing (17)--(18) and using exact telescoping
gives (29).

## 6. Coding, multipulses, and the original PDE

The return strips in (10), the full sign adjacency, (12)--(15), and the
strict first-exit partition satisfy the frozen countable coding theorem.
This proves Theorem V7(1)--(2), the periodic codes, and the bi-infinite
aperiodic codes.

For completeness, multipulses use the completed, not merely open, branch
boxes.  Let \(\overline\Sigma\) be the completed section; its regular part
excludes the face \(y=0\).  The simultaneous symplectic section shear in the
frozen cross-form construction straightens the two selected traces to

\[
 \Gamma^u_{\rm prim,\mu}
   =\{x=0\}\subset W^u_\mu(O_\mu)\cap\overline\Sigma,
 \qquad
 \Gamma^s_{\rm loc,\mu}
   =\{y=0\}\subset W^s_\mu(O_\mu)\cap\overline\Sigma.
\tag{42}
\]

Here \(x=0\) has a fixed interior margin in the angular interval.  The
first set is the image of the chosen local unstable axis through the primary
homoclinic flight, not the whole intersection of the global unstable
manifold with the section; later multipulse sheets need not have \(x=0\).
The second set is the removed stable cut face.

For a finite admissible word \(a_0\cdots a_{m-1}\), solve

\[
 x_{j+1}=f_{a_j}(x_j,y_{j+1}),\qquad
 y_j=g_{a_j}(x_j,y_{j+1}),
 \qquad x_0=0,\quad y_m=0.
\tag{43}
\]

The same product-box map as in the two-sided coding proof is a contraction,
now on a finite product with the two boundary values fixed.  Hence (43) has
one solution.  The seam estimate gives \(y_j>0\) at every regular internal
edge, and the angular image stays in the interior.  The first boundary
condition puts the backward orbit on \(W^u_\mu(O_\mu)\); the last puts its
forward orbit on \(W^s_\mu(O_\mu)\).  The terminal value \(y_m=0\) is used
only in the closed extension and is counted as the cut first exit, not as a
regular return.  It is therefore a homoclinic orbit.
Each symbol forces another high-winding passage through the fixed global
homoclinic flight tube.  Taking words of arbitrary finite length gives the
claimed multipulse family.

Every coded orbit remains in the compact saddle block and finite global
flight tube.  Branch times have a positive lower bound, so no finite
physical-\(\mathsf x\) accumulation is possible.  The exact inverse central
change is

\[
 \begin{aligned}
  u&=a-\sqrt\epsilon\,r^2U,&
  p&=-\epsilon^{3/4}r^3P,\\
  v&=f(a)-\epsilon r^4V,&
  q&=-\epsilon^{5/4}r^3Q,&
  \mathsf x&=r\epsilon^{-1/4}\xi.
 \end{aligned}
\tag{44}
\]

Thus a bounded complete central orbit gives a bounded complete physical
orbit with the physical spatial clock, not merely a desingularized formal
curve.  Equations (3) then give
an entire bounded smooth state \((u,p,v,q)(\mathsf x)\).  Eliminating
\(p,q\) yields

\[
 0=v-f(u)+d u_{\mathsf x\mathsf x},\qquad
 0=\epsilon(a-u)+v_{\mathsf x\mathsf x},
\tag{45}
\]

so \((u(\mathsf x),v(\mathsf x))\) is a stationary solution of the
original PDE.  Periodic codes give periodic profiles; nonperiodic
bi-infinite codes give bounded aperiodic profiles by injectivity of the
itinerary; and (43) gives profiles converging to
\((a,f(a))\) at both spatial infinities, with arbitrarily many separated
core excursions.

## 7. Dependency and interpretation audit

The proof uses the following chain and no shorter one:

\[
 \mathrm{V1}\longrightarrow\mathrm{V2}
 \longrightarrow
 \begin{cases}
  \mathrm{V3},\\
  \mathrm{V4}\longrightarrow\mathrm{V5}\longrightarrow\mathrm{V5A}
 \end{cases}
 \longrightarrow\mathrm{V6}\longrightarrow\mathrm{V7}.
\tag{46}
\]

- V1 supplies the physical exact Hamiltonian structure and primitive.
- V2 supplies the saddle-focus, transverse homoclinic, local passage,
  compact event atlas, common phases, and finite return targets.
- V3 supplies the actual thickened pole channel, finite physical distance,
  and pole finite part.
- V4--V5 supply the actual matched algebraic event patch and its whole
  future-staying tube.
- V5A supplies the reference-normalized algebraic physical-length and
  action finite parts.
- The frozen modular import supplies only H1--H2 high-winding selection,
  component persistence, exact local gluing, cross forms, and coding.

The following are not conclusions of V6--V7:

- classification of the flow outside the fixed physical return--exit tube;
- nonemptiness of every possible end label or every end source sign;
- persistence of either positive end from its singular-core analogue;
- temporal spectral or nonlinear stability of any stationary profile;
- temporal chaos or temporal entropy of the PDE semiflow; or
- experimental realization.

Thus V6 is a two-end **continuation and assembly** theorem on the positive
box (1), not a claim that the singular ends persist unchanged.  V7 concerns
stationary spatial dynamics only.
