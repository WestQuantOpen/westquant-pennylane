from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class OperatorTransform:
    name: str
    function: Callable[[Any], Any]
    metadata: dict[str, Any] = field(default_factory=dict)


def operator_metrics(operator: Any) -> dict[str, Any]:
    coeffs = getattr(operator, "coeffs", None)
    ops = getattr(operator, "ops", None)
    terms = None
    if coeffs is not None:
        try: terms = len(coeffs)
        except Exception: pass
    if terms is None and ops is not None:
        try: terms = len(ops)
        except Exception: pass
    wires = getattr(operator, "wires", ())
    return {"n_terms": terms, "n_wires": len(wires), "native_type": type(operator).__name__}


class OperatorTransformationProvider:
    """Extensible hook for chemistry/operator transformations.

    WestQuant intentionally does not hard-code unstable chemistry transforms.
    Registered functions are versionable actions and can later cover active-space,
    fermion mapping, tapering, grouping and factorization while keeping the same
    RepGraph policy contract.
    """
    def __init__(self) -> None:
        self._transforms: dict[str, OperatorTransform] = {}

    def register(self, transform: OperatorTransform) -> None:
        if transform.name in self._transforms:
            raise ValueError(f"duplicate operator transform: {transform.name}")
        self._transforms[transform.name] = transform

    def apply(self, name: str, operator: Any) -> Any:
        return self._transforms[name].function(operator)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._transforms))
