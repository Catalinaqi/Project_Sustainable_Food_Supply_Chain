from dataclasses import dataclass


@dataclass
class ProdottoFinitoModel:
    id_prodotto : int
    id_azienda : int
    quantita : int
    nome : str
    id_lotto : int

    