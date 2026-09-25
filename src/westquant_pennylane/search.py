from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Sequence

from westquant_core import Action, DeterministicBeamSearch, Evaluation, Objective
from .metrics import tape_metrics


STAGES = ("commute", "cancel", "merge", "cleanup")


@dataclass(frozen=True)
class PennyLaneSearchSpace:
    commute: tuple[str, ...] = ("none", "commute_right", "commute_left")
    cancel: tuple[str, ...] = ("none", "cancel_inverses")
    merge: tuple[str, ...] = ("none", "merge_rotations")
    cleanup: tuple[str, ...] = ("none", "remove_barrier")

    def choices(self, stage: str) -> tuple[str, ...]:
        return tuple(getattr(self, stage))


def _get_transform(qml: Any, name: str):
    for owner in (getattr(qml, "transforms", None), qml):
        if owner is not None and hasattr(owner, name):
            return getattr(owner, name)
    raise AttributeError(f"PennyLane transform not found: {name}")


def _normalize_transform_result(result: Any) -> Any:
    if hasattr(result, "operations"):
        return result
    if isinstance(result, tuple) and len(result) == 2:
        tapes = result[0]
        if isinstance(tapes, (list, tuple)) and len(tapes) == 1:
            return tapes[0]
    if isinstance(result, (list, tuple)) and len(result) == 1 and hasattr(result[0], "operations"):
        return result[0]
    raise TypeError(f"transform returned unsupported result type: {type(result).__name__}")


def _apply(qml: Any, tape: Any, name: str, **kwargs: Any) -> Any:
    transform = _get_transform(qml, name)
    try:
        return _normalize_transform_result(transform(tape, **kwargs))
    except TypeError as first:
        try:
            bound = transform(**kwargs)
            return _normalize_transform_result(bound(tape))
        except Exception:
            raise first


class PennyLaneCompiler:
    def compile(self, tape: Any, prefix: Sequence[Action]) -> Any:
        import pennylane as qml
        out = tape
        for action in prefix:
            if action.name == "none":
                continue
            if action.name == "commute_right":
                out = _apply(qml, out, "commute_controlled", direction="right")
            elif action.name == "commute_left":
                out = _apply(qml, out, "commute_controlled", direction="left")
            elif action.name == "cancel_inverses":
                out = _apply(qml, out, "cancel_inverses")
            elif action.name == "merge_rotations":
                out = _apply(qml, out, "merge_rotations")
            elif action.name == "remove_barrier":
                out = _apply(qml, out, "remove_barrier")
            else:
                raise ValueError(f"unknown PennyLane action: {action.name}")
        return out


class PennyLaneVerifier:
    def __init__(self, *, max_matrix_qubits: int = 7) -> None:
        self.max_matrix_qubits = max_matrix_qubits

    def verify(self, original: Any, candidate: Any) -> dict[str, Any]:
        n = len(getattr(original, "wires", ()))
        if n != len(getattr(candidate, "wires", ())):
            return {"equivalence": "unknown", "verified": False, "reason": "wire_count_changed"}
        if n > self.max_matrix_qubits:
            return {"equivalence": "unknown", "verified": False, "reason": "matrix_limit"}
        if getattr(original, "measurements", ()) or getattr(candidate, "measurements", ()):
            return {"equivalence": "unknown", "verified": False, "reason": "measurements_present"}
        try:
            import numpy as np
            import pennylane as qml
            u = np.asarray(qml.matrix(original), dtype=complex)
            v = np.asarray(qml.matrix(candidate), dtype=complex)
            overlap = np.vdot(u.ravel(), v.ravel())
            phase = 1.0 if abs(overlap) < 1e-15 else overlap / abs(overlap)
            ok = bool(np.allclose(u, phase * v, atol=1e-8, rtol=1e-8))
            return {"equivalence": "exact" if ok else "invalid", "verified": True, "method": "qml.matrix"}
        except Exception as exc:
            return {"equivalence": "unknown", "verified": False, "reason": type(exc).__name__, "message": str(exc)}


class PennyLaneSequentialSearch:
    def __init__(self, *, search_space: PennyLaneSearchSpace | None = None, beam_width: int = 3,
                 compiler: Any | None = None, verifier: Any | None = None) -> None:
        self.search_space = search_space or PennyLaneSearchSpace()
        self.compiler = compiler or PennyLaneCompiler()
        self.verifier = verifier or PennyLaneVerifier()
        self.engine = DeterministicBeamSearch(
            stages=STAGES,
            beam_width=beam_width,
            objectives=(Objective("two_qubit_gates"), Objective("depth"), Objective("n_operations")),
        )

    def run(self, tape: Any, *, challenge_id: str = "pennylane-challenge"):
        def actions(stage, prefix):
            return [Action(stage, name) for name in self.search_space.choices(stage)]

        def evaluate(prefix):
            start = time.perf_counter()
            try:
                compiled = self.compiler.compile(tape, prefix)
                return Evaluation(
                    success=True,
                    metrics=tape_metrics(compiled),
                    verification=self.verifier.verify(tape, compiled),
                    cost={"compile_seconds": time.perf_counter() - start},
                )
            except Exception as exc:
                return Evaluation(success=False, error={"type": type(exc).__name__, "message": str(exc)}, cost={"compile_seconds": time.perf_counter()-start})

        return self.engine.run(challenge_id=challenge_id, actions=actions, evaluate=evaluate)
