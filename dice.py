
from __future__ import annotations
from qiskit import QuantumCircuit
from qiskit.providers.backend import Backend
AerSimulator = None  
try:
    from qiskit_aer import AerSimulator as _AerSim
    AerSimulator = _AerSim
except ImportError:
    pass  

if AerSimulator is None:
    try:
        from qiskit.providers.aer import AerSimulator as _AerSim  # type: ignore
        AerSimulator = _AerSim
    except ImportError:
        AerSimulator = None  

try:
    from qiskit_ibm_provider import IBMProvider  
    _has_ibm = True
except ImportError:
    _has_ibm = False

__all__ = ["QuantumDie"]


class QuantumDie:
    _CIRCUIT = QuantumCircuit(4, 4)
    _CIRCUIT.h(range(4))
    _CIRCUIT.measure(range(4), range(4))

    def __init__(self, backend: Backend | str | None = "aer_simulator"):
        if backend is None or backend == "aer_simulator":
            if AerSimulator is None:
                raise ImportError(
                    "Cannot import AerSimulator.  Install with:\n"
                    "    pip install qiskit-aer\n"
                    "or supply an IBM backend name via BACKEND in __main__.py"
                )
            self.backend: Backend = AerSimulator()
        elif isinstance(backend, str):
            if not _has_ibm:
                raise ImportError(
                    "qiskit-ibm-provider not installed → pip install qiskit-ibm-provider"
                )
            provider = IBMProvider()
            self.backend = provider.get_backend(backend)
        else:
            self.backend = backend  

    def roll(self) -> int:
        while True:
            job = self.backend.run(QuantumDie._CIRCUIT, shots=1)
            bits = next(iter(job.result().get_counts()))
            value = int(bits[::-1], 2)  # little‑endian → int
            if value <= 10:
                return value