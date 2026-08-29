# Direct-IVP check of the finite-boundary canard candidates

## Definition and outcome

For each of the two successful finite-boundary families from the frozen
three-boundary experiment, fix \((u_*,q_0,a_2)\), set

\[
v_*=g_r(u_*),\qquad H_2(u_*,p_*,v_*,q_*)=0,
\]

and select the unique negative root \(p_*<0\).  Direct integration of the
exact central field to the first \(p_2=0\) event then gives the unambiguous
finite-boundary splitting value

\[
S(a_2)=q_2\bigl(t_{\rm hit}(a_2)\bigr).
\]

This calculation uses the already frozen offsets
\(a_2-a_{2,c}=0,\pm10^{-5},\pm2\times10^{-5}\).  Every orbit at both numerical
resolutions reaches a first, transverse, increasing \(p_2=0\) event.  The
sampled open segment has \(p_2<0\) and \(q_2<0\), and the largest Hamiltonian
error is below \(3\times10^{-11}\).

The saved A.3 BVP parameters do **not** give zeros of this direct-IVP
splitting:

| \(q_0\) | \(a_{2,c}\) from BVP | \(S(a_{2,c})\), frozen IVP | tight replay |
|---:|---:|---:|---:|
| \(-80\) | -0.00833819526706 | -8.1452444911 | -8.5312287408 |
| \(-100\) | -0.00833693853356 | -24.6518626504 | -24.4403489568 |

Thus neither family is a boundary-selected simple-zero candidate under the
direct definition above.

## Parameter variation

Along with the state, the code integrates

\[
z'=D_yF(y,a_2)z+\partial_{a_2}F,
\]

starting with the derivative of the negative zero-energy root.  At the event,
the time correction is

\[
t_{\rm hit}'=-\frac{z_p}{p_2'},\qquad
\frac{dS}{da_2}=z_q+q_2't_{\rm hit}'.
\]

At the BVP centers the resulting values are about
\(7.75\times10^{14}\) and \(5.52\times10^{13}\), respectively.  They disagree
with both predeclared symmetric differences by relative error essentially
one.  The two high-accuracy resolutions also change the center splitting by
0.386 and 0.212.  The unstable amplification therefore overwhelms the
accuracy of the saved collocation candidates; the large tangent values are
not reported as derivatives of a verified splitting zero.

The fail-closed status is
`DIRECT_IVP_DID_NOT_SHADOW_BOUNDARY_BVP_CANDIDATES`.  It does not prove that a
finite-boundary or intrinsic maximal canard is absent.  In particular, it
does not replace the missing intrinsic \(W^{cu}\) branch selector and closes
none of C1, C2, or the high-winding connection claims.

The computation and saved output are
[`vdp_canard_direct_splitting.py`](vdp_canard_direct_splitting.py) and
[`report.json`](results/vdp_canard_direct_splitting/report.json).

```bash
python3 -B numerics/vdp_canard_direct_splitting.py \
  --output /tmp/vdp-canard-direct-splitting.json
python3 -B -m unittest numerics.test_vdp_canard_direct_splitting -v
```
