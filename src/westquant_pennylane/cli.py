from __future__ import annotations
import argparse, json
from pathlib import Path
from westquant_core import write_jsonl
from .search import PennyLaneSequentialSearch


def main() -> None:
    p = argparse.ArgumentParser(description="WestQuant sequential transform search for PennyLane")
    p.add_argument("--module", required=True, help="Python module path containing make_tape()")
    p.add_argument("--beam-width", type=int, default=3)
    p.add_argument("--output", default="results/westquant-pennylane")
    args = p.parse_args()
    import importlib.util
    spec = importlib.util.spec_from_file_location("wq_user_circuit", args.module)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load module")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    tape = mod.make_tape()
    result = PennyLaneSequentialSearch(beam_width=args.beam_width).run(tape, challenge_id=Path(args.module).stem)
    out=Path(args.output); out.mkdir(parents=True, exist_ok=True)
    (out/"summary.json").write_text(json.dumps({"best": result.best.to_dict() if result.best else None, "n_states": len(result.states)}, indent=2), encoding="utf-8")
    write_jsonl(out/"trajectory.jsonl", result.records(framework="pennylane"))

if __name__ == "__main__": main()
