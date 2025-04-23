from dataclasses import dataclass


@dataclass
class MateriaPrimaModel:
    id_prodotto : int
    id_azienda : int
    quantita : int
    nome : str

    