# P2c strict-run log snapshots

These four files are the fixed numeric-order concatenations produced by the
completed local strict P2c runs.  They are deliberately small summary logs,
not compiler binaries or per-cell checkpoints.  The P2c certificate checker
parses them and verifies their recorded SHA-256 digests, grid indices, counts,
strict margins, and terminal `PASS` records without rerunning the 16,384-cell
CAPD computations.

- `p2c_branch_v1.log`: frozen-core anchor, then branch slabs 0 through 31;
- `p2c_first_hit_v1.log`: first-hit slabs 0 through 31;
- `p2c_root_jets_v1.log`: actual-root C2 slabs 0 through 31;
- `p2c_middle_c2_v1.log`: continuous compact-middle C2 slabs 0 through 31.

They are local evidence snapshots.  They do not satisfy the repository's
independent-machine replay policy by themselves.
