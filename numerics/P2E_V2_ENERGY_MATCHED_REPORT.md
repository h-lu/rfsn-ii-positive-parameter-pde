# Energy-preserving v2 algebraic matched centerline

At the unchanged exploratory point

\[
  (r,a_2,\epsilon)=(3/200,0,1),
\]

the central--`K1`--outer solve now produces one accepted floating-point
centerline.  It remains `COMPUTED/E1_NON_RIGOROUS` and does not validate V5 or
materialize the V2 event atlas.

## What was wrong

The old coupled BVP had eight state unknowns and two scalar parameters.  Its
ten boundary rows matched only `(Pi,Omega)` at the central--`K1` seam.  It
fixed `H=0` and expected the omitted `q1` row to follow automatically from
energy conservation.  A central collocation residual of order `1e-4` broke
that implication and amplified to an order-one `q1` seam error.

The repaired system removes the central collocation leg.  A direct
high-accuracy central IVP reaches `U=-4`, and a four-state reduced
`K1`--outer BVP solves for two scalar parameters `(source phase,H)`.  Its six
boundary rows are exactly

1. central--`K1` matching of `Pi`, `Omega`, and `q1`;
2. `K1`--outer matching of the two positive-`pi` coordinates;
3. the finite-horizon terminal equation `alpha(Q_end)=0`.

The resolved `K1` energy root uses the solved `H` at every collocation point;
the outer root uses the same physical energy.  No physical parameter, phase
bracket, section, outer leaf, or terminal condition was changed.

## Result

- source phase: `5.756767223284979`;
- central flight time: `9.895162060961962`;
- solved energy: `H=1.6531401306609465e-14`;
- solver residual: `9.9041e-7` at the predeclared `1e-6` tolerance;
- six-row boundary residual: `1.470e-12`;
- central energy: `6.911e-14`;
- exact resolved-`K1` energy-equation residual: `3.553e-15`;
- outer energy-equation residual: `5.551e-17`;
- full central--`K1` state seam residual: `5.162e-12`;
- `K1`--outer normal seam residual: `4.659e-21`;
- independent same-section Gamma residual: `4.235e-22`;
- positive branch margins: `min Pi=0.30429`, `min q1=1.15490`,
  `min pi_outer=1.36931e-4`.

The central cut has `P=-1.15437` and `Q=-9.23920`, so it is the algebraic
first-hit branch, not the neighboring return branch.  The saved NPZ contains
401 samples on each of the central, resolved-`K1`, and outer pieces.

Reproduce and test with:

```bash
python3 -m numerics.vdp_p2e_energy_matched
python3 -m unittest numerics.test_vdp_p2e_energy_matched -v
```
