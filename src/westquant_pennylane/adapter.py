from __future__ import annotations

from typing import Any
from westquant_core import Representation, RepresentationKind


class PennyLaneAdapter:
    framework = "pennylane"

    def import_native(self, tape: Any, *, representation_id: str = "pennylane:circuit") -> Representation:
        operations = []
        for op in tape.operations:
            operations.append({
                "name": op.name,
                "wires": [str(w) for w in op.wires],
                "n_params": len(op.parameters),
            })
        payload = {
            "n_operations": len(operations),
            "operations": operations,
            "n_measurements": len(tape.measurements),
            "wires": [str(w) for w in tape.wires],
        }
        return Representation(
            id=representation_id,
            kind=RepresentationKind.CIRCUIT,
            framework=self.framework,
            payload=payload,
            metadata={"native_type": type(tape).__name__},
        )
