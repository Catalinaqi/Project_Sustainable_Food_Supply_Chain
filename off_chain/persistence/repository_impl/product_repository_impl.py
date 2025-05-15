# pylint: disable=no-name-in-module
# # pylint: disable=import-error
from abc import ABC
from typing import List, Optional, Tuple, Union

from configuration.database import Database
from configuration.log_load_setting import logger
from model.prodotto_finito_model import ProdottoLottoModel
from model.info_product_for_choice_model import ProductForChoiceModel
from model.lotto_composizione_model import Composizione, Lotto
from model.prodotto_finito_cliente import ProdottoFinito
from model.product_standard_model import ProductStandardModel
from persistence.query_builder import QueryBuilder
from persistence.repository_impl import db_default_string


class ProductRepositoryImpl(ABC):
    """
    Implementazione del repository per prodotti.
    """

    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()

    def co2_consumata_prodotti(self, prodotti: List[Tuple[int]]) -> List[Tuple[Tuple[int], float]]:
        """
        Calcola la CO2 consumata per ogni prodotto dato in input.
        :param prodotti: lista di tuple contenenti id prodotto
        :return: lista di tuple (prodotto, totale_co2)
        """
        lista_con_co2 = []
        for prodotto in prodotti:
            storico = self.get_storico_prodotto(prodotto[0])
            totale_co2 = sum(t[4] for t in storico)
            lista_con_co2.append((prodotto, totale_co2))
        return lista_con_co2

    def get_prodotti_standard_agricoli(self) -> List[ProductStandardModel]:
        """
        Restituisce lista prodotti agricoli (stato = 0).
        """
        try:
            result = self.db.fetch_results("SELECT Id_prodotto, Nome FROM Prodotto WHERE Stato = 0")
            logger.info(f"Prodotti standard agricoli trovati: {result}")
            return [ProductStandardModel(*x) for x in result] if result else []
        except Exception as err:
            logger.warning(f"Nessun prodotto agricolo trovato: {err}")
            return []

    def get_prodotti_standard_trasformazione(self) -> List[ProductStandardModel]:
        """
        Restituisce lista prodotti trasformazione (stato = 1).
        """
        try:
            result = self.db.fetch_results("SELECT Id_prodotto, Nome FROM Prodotto WHERE Stato = 1")
            logger.info(f"Prodotti standard trasformazione trovati: {result}")
            return [ProductStandardModel(*x) for x in result] if result else []
        except Exception as err:
            logger.warning(f"Nessun prodotto di trasformazione trovato: {err}")
            return []

    def get_materie_prime_magazzino_azienda(self, id_azienda: int) -> List[ProdottoLottoModel]:
        """
        Restituisce materie prime disponibili in magazzino per azienda.
        """
        query, value = (
            self.query_builder
            .select(
                "Prodotto.id_prodotto",
                "Magazzino.id_azienda",
                "Magazzino.quantita",
                "Prodotto.nome",
                "Operazione.id_lotto"
            )
            .table("Magazzino")
            .join("Operazione", "Magazzino.id_lotto", "Operazione.id_lotto")
            .join("Prodotto", "Operazione.id_prodotto", "Prodotto.id_prodotto")
            .where("Magazzino.id_azienda", "=", id_azienda)
            .where("Prodotto.stato", "=", 0)  # Materia prima
            .get_query()
        )

        try:
            logger.info(f"Query get_materie_prime_magazzino_azienda: {query} - Valori: {value}")
            result = self.db.fetch_results(query, value)
        except Exception as err:
            logger.error(f"Errore in get_materie_prime_magazzino_azienda: {err}")
            return []

        if not result:
            logger.warning("Nessun risultato per get_materie_prime_magazzino_azienda")
            return []

        try:
            return [ProdottoLottoModel(*x) for x in result]
        except Exception as err:
            logger.error(f"Errore conversione in ProdottoLottoModel: {err}")
            return []

    def get_prodotti_finiti_magazzino_azienda(self, id_azienda: int) -> List[ProdottoLottoModel]:
        """
        Restituisce prodotti finiti disponibili in magazzino per azienda.
        """
        query, value = (
            self.query_builder
            .select(
                "Prodotto.id_prodotto",
                "Magazzino.id_azienda",
                "Magazzino.quantita",
                "Prodotto.nome",
                "Operazione.id_lotto"
            )
            .table("Magazzino")
            .join("Operazione", "Magazzino.id_lotto", "Operazione.id_lotto")
            .join("Prodotto", "Operazione.id_prodotto", "Prodotto.id_prodotto")
            .where("Magazzino.id_azienda", "=", id_azienda)
            .where("Prodotto.stato", "=", 1)  # Prodotto finito
            .get_query()
        )

        try:
            logger.info(f"Query get_prodotti_finiti_magazzino_azienda: {query} - Valori: {value}")
            result = self.db.fetch_results(query, value)
        except Exception as err:
            logger.error(f"Errore in get_prodotti_finiti_magazzino_azienda: {err}")
            return []

        if not result:
            logger.warning("Nessun risultato per get_prodotti_finiti_magazzino_azienda")
            return []

        try:
            return [ProdottoLottoModel(*x) for x in result]
        except Exception as err:
            logger.error(f"Errore conversione in ProdottoLottoModel: {err}")
            return []

    def get_prodotti_ordinabili(self, tipo_prodotto: int = 0) -> List[ProductForChoiceModel]:
        """
        Restituisce prodotti ordinabili filtrati per tipo prodotto.
        :param tipo_prodotto: 0 = agricolo, 1 = trasformazione
        """
        self.query_builder \
            .select(
                "Azienda.Nome",
                "Prodotto.nome",
                "Magazzino.quantita",
                "Prodotto.id_prodotto",
                "Azienda.Id_azienda",
                "Operazione.Consumo_CO2"
            ) \
            .table("Magazzino") \
            .join("Operazione", "Magazzino.id_lotto", "Operazione.id_lotto") \
            .join("Azienda", "Operazione.id_azienda", "Azienda.id_azienda") \
            .join("Prodotto", "Operazione.id_prodotto", "Prodotto.id_prodotto") \
            .where("Magazzino.quantita", ">", 0)

        if tipo_prodotto == 0:
            self.query_builder.where("Prodotto.stato", "=", 0) \
                              .where("Azienda.Tipo", "=", db_default_string.TIPO_AZIENDA_AGRICOLA)
        elif tipo_prodotto == 1:
            self.query_builder.where("Prodotto.stato", "=", 1) \
                              .where("Azienda.Tipo", "=", db_default_string.TIPO_AZIENDA_TRASPORTATORE)
        else:
            raise ValueError("Tipo di prodotto non identificato")

        query, value = self.query_builder.get_query()

        try:
            logger.info(f"Query get_prodotti_ordinabili: {query} - Valori: {value}")
            result = self.db.fetch_results(query, value)
        except Exception as err:
            logger.error(f"Errore in get_prodotti_ordinabili: {err}")
            return []

        if not result:
            logger.warning("Nessun risultato in get_prodotti_ordinabili")
            return []

        try:
            return [ProductForChoiceModel(*x) for x in result]
        except Exception as err:
            logger.error(f"Errore conversione in ProductForChoiceModel: {err}")
            return []

    def carica_lotto_con_composizione(self, id_lotto: int) -> Optional[Lotto]:
        """
        Carica un lotto e la sua composizione ricorsivamente.
        :param id_lotto: id del lotto
        :return: oggetto Lotto o None se non trovato
        """
        query, value = (
            self.query_builder
            .select("Id_lotto", "Tipo", "quantita", "Consumo_CO2")
            .table("Operazione")
            .where("Id_lotto", "=", id_lotto)
            .get_query()
        )

        try:
            rows = self.db.fetch_results(query, value)
            if not rows:
                logger.warning(f"Nessuna operazione trovata per id_lotto: {id_lotto}")
                return None

            lotto = Lotto(*rows[0])
        except Exception as err:
            logger.error(f"Errore recupero operazione: {err}")
            return None

        query, value = (
            self.query_builder
            .select("id_lotto_input", "quantità_utilizzata")
            .table("ComposizioneLotto")
            .where("id_lotto_output", "=", id_lotto)
            .get_query()
        )

        try:
            rows = self.db.fetch_results(query, value)
            composizioni_raw = [Composizione(*x) for x in rows] if rows else []
        except Exception as err:
            logger.error(f"Errore recupero composizione: {err}")
            return None

        for comp in composizioni_raw:
            input_lotto = self.carica_lotto_con_composizione(comp.id_lotto_input)
            composizione = Composizione(
                id_lotto_input=comp.id_lotto_input,
                quantita_utilizzata=comp.quantita_utilizzata,
                lotto_input=input_lotto
            )
            lotto.composizione.append(composizione)

        return lotto

    def get_lista_prodotti(self) -> List[ProdottoFinito]:
        """
        Recupera lista prodotti venduti (tipo operazione = vendita).
        :return: lista di ProdottoFinito
        """
        query, value = (
            self.query_builder
            .select(
                "Prodotto.nome",
                "Operazione.Id_lotto",
                "Azienda.nome",
                "Operazione.Id_prodotto"
            )
            .table("Operazione")
            .join("Azienda", "Operazione.Id_azienda", "Azienda.Id_azienda")
            .join("Prodotto", "Operazione.Id_prodotto", "Prodotto.Id_prodotto")
            .where("Operazione.Tipo", "=", db_default_string.TIPO_OP_VENDITA)
            .get_query()
        )

        try:
            results = self.db.fetch_results(query, value)
            if results:
                return [ProdottoFinito(*r) for r in results]

            logger.warning("Nessun risultato trovato in get_lista_prodotti")
            return []
        except Exception as err:
            logger.error(f"Errore in get_lista_prodotti: {err}")
            return []

    # Metodo mancante in originale: serve definire get_storico_prodotto se usato in co2_consumata_prodotti
    def get_storico_prodotto(self, id_prodotto: int) -> List[Tuple]:
        """
        Recupera storico consumi CO2 per prodotto.
        :param id_prodotto: ID prodotto
        :return: lista di tuple con dati storici (definire struttura in base a DB)
        """
        query = "SELECT * FROM Storico WHERE id_prodotto = ?"
        try:
            result = self.db.fetch_results(query, (id_prodotto,))
            return result if result else []
        except Exception as err:
            logger.error(f"Errore in get_storico_prodotto per id {id_prodotto}: {err}")
            return []
