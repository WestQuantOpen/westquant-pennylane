from westquant_pennylane.adapter import PennyLaneAdapter


class Op:
    name = "RX"
    wires = [0]
    parameters = [0.5]

class Tape:
    operations = [Op()]
    measurements = [object()]
    wires = [0]


def test_import():
    r = PennyLaneAdapter().import_native(Tape())
    assert r.payload["n_operations"] == 1
    assert r.framework == "pennylane"
