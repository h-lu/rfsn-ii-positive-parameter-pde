#!/usr/bin/env python3
"""Generate a build-only fold probe with the promoted physical C0 budget."""

from pathlib import Path
import sys


source = Path(sys.argv[1])
destination = Path(sys.argv[2])
text = source.read_text()
old = "const interval rho=robust ? interval(-1e-8,1e-8) : interval(0.);"
new = (
    "const interval rho=robust "
    "? interval(-3.359232e-10,3.359232e-10) : interval(0.);"
)
if text.count(old) != 1:
    raise RuntimeError("unexpected upstream fold source: target value line not unique")
text = text.replace(old, new)
old_iteration = """    const IVector contractionImage=remainder*(X-centre);
    const IVector krawczyk=centre-preconditioner*residual+contractionImage;
"""
new_iteration = """    IVector contractionImage=remainder*(X-centre);
    IVector krawczyk=centre-preconditioner*residual+contractionImage;
    if(!(capd::vectalg::subsetInterior)(krawczyk,X))
      throw std::runtime_error("first Krawczyk iterate failed");
    for(int iteration=0;iteration<3;++iteration) {
      contractionImage=remainder*(krawczyk-centre);
      krawczyk=centre-preconditioner*residual+contractionImage;
    }
"""
if text.count(old_iteration) != 1:
    raise RuntimeError("unexpected upstream fold source: Krawczyk block not unique")
destination.write_text(text.replace(old_iteration, new_iteration))
