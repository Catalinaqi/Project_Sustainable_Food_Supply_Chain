# pylint: disable=no-name-in-module
# # pylint: disable=import-error
import datetime
from abc import ABC
from typing import Optional, List
from configuration.database import Database
from configuration.log_load_setting import logger
from persistence.query_builder import QueryBuilder
from model.compensation_action_model import CompensationActionModel


class CompensationActionRepositoryImpl(ABC):
    """
    Repository implementation for managing compensation actions.
    """

    def __init__(self) -> None:
        super().__init__()
        self.db = Database()

    def get_lista_azioni(
        self,
        id_azienda: int,
        data_start: Optional[datetime.datetime] = None,
        data_end: Optional[datetime.datetime] = None,
        ordinamento: Optional[str] = None,
    ) -> List[CompensationActionModel]:
        """
        Retrieve compensation actions for a company within an optional date range,
        optionally ordered.

        Args:
            id_azienda (int): Company ID.
            data_start (Optional[datetime.datetime]): Start date filter (exclusive).
            data_end (Optional[datetime.datetime]): End date filter (exclusive).
            ordinamento (Optional[str]): Sort field, e.g. "DESC" for descending by CO2 compensated.

        Returns:
            List[CompensationActionModel]: List of compensation actions.
        """
        try:
            query_builder = QueryBuilder()
            query_builder.select(
                "Id_azione",
                "Id_azienda",
                "Data",
                "Co2_compensata",
                "Nome_azione",
            ).table("Azioni_compensative").where("Id_azienda", "=", id_azienda)

            if data_start is not None:
                query_builder.where("Data", ">", data_start)
            if data_end is not None:
                query_builder.where("Data", "<", data_end)

            if ordinamento is not None and ordinamento.upper() == "DESC":
                query_builder.order_by("Co2_compensata", "DESC")

            query, values = query_builder.get_query()
            results = self.db.fetch_results(query, values)

            return [
                CompensationActionModel(
                    Id_azione=row[0],
                    Id_azienda=row[1],
                    Data_azione=row[2],
                    Co2_compensata=row[3],
                    Nome_azione=row[4],
                )
                for row in results
            ]
        except Exception as exc:
            logger.error(f"Errore nel recupero delle azioni compensative: {exc}")
            return []

    def get_co2_compensata(self, id_azienda: int) -> float:
        """
        Retrieve the total CO2 compensated by a given company.

        Args:
            id_azienda (int): Company ID.

        Returns:
            float: Total CO2 compensated.
        """
        query_builder = QueryBuilder()
        query_builder.select("SUM(Co2_compensata)").table("Azioni_compensative").where(
            "Id_azienda", "=", id_azienda
        )
        query, values = query_builder.get_query()
        try:
            result = self.db.fetch_one(query, values)
            return float(result) if result is not None else 0.0
        except (TypeError, ValueError) as exc:
            logger.error(f"Errore nel recupero della CO2 compensata: {exc}")
            raise ValueError("Impossibile convertire il valore CO2 compensata in float")

    def inserisci_azione(
        self,
        data: datetime.datetime,
        azienda: int,
        co2_compensata: float,
        nome_azione: str,
    ) -> None:
        """
        Insert a new compensation action and update the company's compensated CO2.

        Args:
            data (datetime.datetime): Date of the action.
            azienda (int): Company ID.
            co2_compensata (float): Amount of CO2 compensated.
            nome_azione (str): Name of the action.

        Raises:
            Exception: If insertion fails.
        """
        try:
            queries = []

            query_azione = """
                INSERT INTO Azioni_compensative (Data, Id_azienda, Co2_compensata, Nome_azione)
                VALUES (?, ?, ?, ?);
            """
            values_azione = (data, azienda, co2_compensata, nome_azione)
            queries.append((query_azione, values_azione))

            query_update_azienda = """
                UPDATE Azienda SET Co2_compensata = Co2_compensata + ?
                WHERE Id_azienda = ?;
            """
            values_update = (co2_compensata, azienda)
            queries.append((query_update_azienda, values_update))

            self.db.execute_transaction(queries)
            logger.info("Azione compensativa aggiunta con successo")
        except Exception as exc:
            logger.error(f"Errore nell'inserimento di una azione compensativa: {exc}")
            raise
