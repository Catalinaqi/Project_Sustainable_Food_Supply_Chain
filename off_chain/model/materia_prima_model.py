from dataclasses import dataclass


@dataclass
class MateriaPrimaModel:
    id : int
    id_azienda : int
    id_prodotto : int
    quantita : int
    nome : str

    