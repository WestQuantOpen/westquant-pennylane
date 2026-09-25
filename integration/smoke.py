import pennylane as qml
from westquant_pennylane import PennyLaneSequentialSearch
ops=[qml.Hadamard(0),qml.CNOT((0,1)),qml.CNOT((1,2)),qml.RZ(0.3,2),qml.RZ(-0.3,2)]
tape=qml.tape.QuantumScript(ops,[])
r=PennyLaneSequentialSearch(beam_width=2).run(tape,challenge_id='smoke-pennylane')
assert r.best is not None
print(r.best.to_dict())
