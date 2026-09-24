# westquant-pennylane

Wave 1 PennyLane integration targeting PennyLane 0.45+.

The native integration surface is `qml.transform` / `CompilePipeline` rather
than a WestQuant-specific execution backend. v0.1 starts with QuantumScript
import and representation tracing. v0.2 will search transform sequences and
resource/measurement representations.
