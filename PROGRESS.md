# Progress log

The running memory of this Ralph loop. Each iteration appends one line below —
what it did and what is next — newest at the bottom. A fresh agent reads this
before starting, to see what the iterations before it already did.

## Log

<!-- iterations append one line each below this line -->
- F1 done: `render_session` now parses the full document with ElementTree.fromstring and raises a clear ValueError on malformed XML (`_assert_well_formed`); added pass/raise tests. Next: F2 forks conservation guard.
