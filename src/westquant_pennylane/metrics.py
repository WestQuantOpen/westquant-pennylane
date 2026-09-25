from __future__ import annotations
from collections import Counter
from typing import Any


def tape_metrics(tape: Any) -> dict[str, Any]:
    ops = list(getattr(tape, "operations", ()))
    counts = Counter(str(getattr(op, "name", type(op).__name__)) for op in ops)
    wire_depth: dict[str, int] = {}
    two_qubit = 0
    n_params = 0
    for op in ops:
        wires = [str(w) for w in getattr(op, "wires", ())]
        if len(wires) == 2:
            two_qubit += 1
        n_params += len(getattr(op, "parameters", ()))
        layer = 1 + max((wire_depth.get(w, 0) for w in wires), default=0)
        for w in wires:
            wire_depth[w] = layer
    return {
        "n_operations": len(ops),
        "two_qubit_gates": two_qubit,
        "depth": max(wire_depth.values(), default=0),
        "n_measurements": len(getattr(tape, "measurements", ())),
        "n_wires": len(getattr(tape, "wires", ())),
        "n_parameters": n_params,
        "operations": dict(counts),
    }
