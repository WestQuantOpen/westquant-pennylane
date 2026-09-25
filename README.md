# westquant-pennylane

WestQuant representation search for PennyLane 0.45.x.

The alpha search policy operates on transform decisions rather than inventing a
new execution backend:

```text
commute -> cancel -> merge -> cleanup
```

Actions use PennyLane's public transform layer (`commute_controlled`,
`cancel_inverses`, `merge_rotations`, `remove_barrier`). A separate
`OperatorTransformationProvider` is included so chemistry/operator
representations can add versioned active-space, mapping, tapering, grouping and
factorization transformations without changing the policy schema.

Small measurement-free tapes attempt exact matrix verification. All other
cases are conservatively marked `unknown`.

Requires Python 3.11+ because current PennyLane 0.45.1 does.

## Native smoke

```bash
pip install -e ../westquant-core -e .[test]
pytest -q
python integration/smoke.py
```
