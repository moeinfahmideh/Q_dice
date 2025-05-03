from __future__ import annotations
import pandas as pd
from dice import QuantumDie
__all__ = ["Composer"]

class Composer:
    _COLS = list("ABCDEFGHIJKLMNOPQRSTUVWXY")  

    def __init__(self, table: pd.DataFrame, die: QuantumDie | None = None):
        self.table = table
        self.die = die or QuantumDie()

    def generate(self) -> list[int]:
        seq = [int(self.table.loc[self.die.roll(), col]) for col in Composer._COLS]
        seq.append(188)  # fixed Z element
        return seq