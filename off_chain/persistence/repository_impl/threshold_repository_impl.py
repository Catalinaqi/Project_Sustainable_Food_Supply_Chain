# pylint: disable=import-error
from abc import ABC
from typing import List

from configuration.database import Database
from configuration.log_load_setting import logger
from model.threshold_model import ThresholdModel
from persistence.query_builder import QueryBuilder
from persistence.repository_impl import db_default_string


class ThresholdRepositoryImpl(ABC):
    """Implementazione del repository per le soglie."""

    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()

    def get_lista_soglie(self) -> List[ThresholdModel]:
        """
        Recupera la lista delle soglie associate ai prodotti.

        Returns:
            List[ThresholdModel]: lista di modelli soglia.
        """
        self.query_builder.select(
            "P.Nome",
            "Soglia_Massima",
            "Operazione"
        ).table("Soglie").join(
            "Prodotto AS P",
            "P.Id_prodotto",
            "Prodotto"
        )

        query, value = self.query_builder.get_query()

        try:
            risultati = self.db.fetch_results(query, value)
            return [ThresholdModel(*record) for record in risultati]
        except Exception as e:
            logger.error(f"Errore durante il recupero delle soglie: {e}", exc_info=True)
            return []
