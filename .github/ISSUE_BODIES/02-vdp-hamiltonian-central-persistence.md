## Objective

Freeze the positive-parameter van der Pol stationary spatial Hamiltonian and
prove persistence of the compact central data required by the later return and
exit theorem.

## Proof obligations

- [ ] Fix the PDE, \(d\), \(\delta=\sqrt d\), \(r_2\), \(a_2\), \(\epsilon\),
      physical spatial variable, and every desingularized clock.
- [ ] Verify the first integral, exact symplectic form, primitive, Hamiltonian
      sign convention, and reverser by direct calculation.
- [ ] Give the exact conjugacy between the \(r_2=0\) central chart and the
      RFSN-II core used in the flagship paper.
- [ ] State a nonempty positive parameter wedge.
- [ ] Prove persistence of the saddle-focus and transverse homoclinic in that
      wedge.
- [ ] Prove persistence of local passage, compact first-hit faces, source
      phases, and their positive ordering margins.
- [ ] Track two external parameter derivatives wherever the final theorem will
      use mixed \(C^2\) estimates.

## Acceptance

Claim V1 is recorded as **Derived** by the direct calculation in
`van-der-pol/HAMILTONIAN_CHECK.md`; this issue must still reconcile its notation
with every blow-up chart.  Claim V2 becomes **Proved** only after the
parameter-uniform persistence theorem is complete.  Quantitative interval
claims require a separate rigorous validation.
