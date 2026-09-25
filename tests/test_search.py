from westquant_pennylane.search import PennyLaneSequentialSearch

class Op:
    def __init__(self, name, wires): self.name=name; self.wires=wires; self.parameters=[]
class Tape:
    wires=(0,1,2); measurements=()
    operations=(Op('X',(0,)), Op('CNOT',(0,1)), Op('CNOT',(1,2)))

class Compiler:
    def compile(self, tape, prefix):
        t=Tape(); t._score=sum(0 if a.name in {'cancel_inverses','merge_rotations','commute_right','remove_barrier'} else 1 for a in prefix); return t
class Verifier:
    def verify(self,a,b): return {'equivalence':'exact','verified':True}

def test_search(monkeypatch):
    import westquant_pennylane.search as m
    monkeypatch.setattr(m, 'tape_metrics', lambda t: {'two_qubit_gates':t._score,'depth':t._score,'n_operations':t._score})
    r=PennyLaneSequentialSearch(beam_width=2, compiler=Compiler(), verifier=Verifier()).run(Tape())
    assert r.best is not None
    assert r.records(framework='pennylane')
