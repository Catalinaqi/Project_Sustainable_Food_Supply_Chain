from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Lotto:
    id_lotto: int
    tipo: str
    quantita: float
    cons_co2: float
    composizione: List["Composizione"] = field(default_factory=list)
    co2_costo_composizione: float = 0.0
    co2_totale_lotto_unitario: float = 0.0

    def get_costo_totale_lotto_unitario(self) -> float:
        """
        Calcola il costo totale di CO2 unitario del lotto
        considerando la somma del consumo CO2 diretto più quello
        derivante dalla composizione.

        Returns:
            float: costo CO2 unitario per unità di quantità del lotto.
        """
        self.co2_costo_composizione = 0.0
        if len(self.composizione) > 0:
            for comp in self.composizione:
                self.co2_costo_composizione += comp.get_co2_consumata_quantità_utilizzata()

        self.co2_totale_lotto_unitario = (self.co2_costo_composizione + self.cons_co2) / self.quantita

        return self.co2_totale_lotto_unitario


@dataclass
class Composizione:
    id_lotto_input: int
    quantita_utilizzata: float
    lotto_input: Optional[Lotto] = None

    def get_co2_consumata_quantità_utilizzata(self) -> float:
        """
        Calcola la CO2 consumata in base alla quantità utilizzata
        e al costo CO2 unitario del lotto di input.

        Returns:
            float: CO2 consumata per la quantità utilizzata.
        """
        if isinstance(self.lotto_input, Lotto):
            return self.lotto_input.get_costo_totale_lotto_unitario() * self.quantita_utilizzata
        return 0.0
