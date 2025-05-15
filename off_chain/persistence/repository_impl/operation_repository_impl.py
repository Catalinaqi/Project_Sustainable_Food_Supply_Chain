import datetime
import os
from abc import ABC
from typing import Final, List, Optional, Tuple

from pydantic import BaseModel

from configuration.database import Database
from configuration.log_load_setting import logger
from model.operation_estesa_model import OperazioneEstesaModel
from persistence.query_builder import QueryBuilder


class FirmaRequest(BaseModel):
    tipo_operazione: str
    id_prodotto: int
    soglia_massima: int


class VerificaRequest(FirmaRequest):
    signature: str


SECRET_KEY: str = os.getenv("_KEY", "default_dev_key")


class OperationRepositoryImpl(ABC):
    """
    Repository for operation management.
    """

    QUERY_UPDATE_AZIENDA: Final[str] = (
        """
        UPDATE Azienda
        SET Co2_emessa = Co2_emessa + ?, Token = Token + ?
        WHERE Id_azienda = ?;
        """
    )

    def __init__(self) -> None:
        super().__init__()
        self.db: Database = Database()

    def get_operazioni_by_azienda(self, azienda: int) -> List[OperazioneEstesaModel]:
        """
        Retrieve all operations for a given company.

        Args:
            azienda (int): Company ID.

        Returns:
            List[OperazioneEstesaModel]: List of operations.
        """
        try:
            query_builder = QueryBuilder()
            query_builder.select(
                "Operazione.Id_operazione",
                "Prodotto.Id_prodotto",
                "Prodotto.Nome",
                "Operazione.Data_operazione",
                "Operazione.Consumo_CO2",
                "Operazione.Tipo",
                "Operazione.quantita",
            ).table("Operazione").join(
                "Prodotto", "Operazione.Id_prodotto", "Prodotto.Id_prodotto"
            ).where("Operazione.Id_azienda", "=", azienda)

            query, values = query_builder.get_query()
            results = self.db.fetch_results(query, values)

            return [
                OperazioneEstesaModel(
                    Id_operazione=row[0],
                    Id_prodotto=row[1],
                    Nome_prodotto=row[2],
                    Data_operazione=row[3],
                    Consumo_CO2=row[4],
                    Nome_operazione=row[5],
                    Quantita_prodotto=row[6],
                )
                for row in results
            ]
        except Exception as exc:
            logger.error("Error fetching operations by company: %s", exc, exc_info=True)
            return []

    def inserisci_operazione_azienda_rivenditore(
        self,
        azienda: int,
        prodotto: int,
        data: datetime.datetime,
        co2: float,
        evento: str,
        id_lotto_input: int,
        quantita: int,
    ) -> None:
        """
        Insert a retailer operation with stock update and token calculation.

        Args:
            azienda (int): Company ID.
            prodotto (int): Product ID.
            data (datetime.datetime): Operation date.
            co2 (float): CO2 consumed.
            evento (str): Operation type.
            id_lotto_input (int): Input lot ID.
            quantita (int): Quantity used.

        Raises:
            Exception: If insertion fails.
        """
        try:
            queries: List[Tuple[str, Tuple]] = []

            value_output_lotto = self.get_next_id_lotto_output()

            queries.append((
                "INSERT INTO ComposizioneLotto (id_lotto_output, id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)",
                (value_output_lotto, id_lotto_input, quantita),
            ))

            queries.append((
                """
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Data_operazione, Consumo_CO2, Tipo, quantita)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (azienda, prodotto, value_output_lotto, data, co2, evento, quantita),
            ))

            queries.append((
                "UPDATE Magazzino SET quantita = quantita - ? WHERE Id_azienda = ? AND Id_lotto = ?",
                (quantita, azienda, id_lotto_input),
            ))

            token_assegnati = self.token_operazione(co2_consumata=co2, tipo_operazione=evento, id_prodotto=prodotto)

            queries.append((self.QUERY_UPDATE_AZIENDA, (co2, token_assegnati, azienda)))

            self.db.execute_transaction(queries)
        except Exception as exc:
            logger.error("Errore inserimento operazione rivenditore: %s", exc, exc_info=True)
            raise Exception(f"Errore inserimento operazione rivenditore: {exc}") from exc

    def get_next_id_lotto_output(self) -> int:
        """
        Get the next ID for output lot.

        Returns:
            int: Next output lot ID.
        """
        try:
            result: Optional[int] = self.db.fetch_one("SELECT IFNULL(MAX(id_lotto_output), 0) + 1 FROM ComposizioneLotto;")
            return int(result) if result is not None else 1
        except Exception as exc:
            logger.error("Errore nell'ottenimento del nuovo id lotto: %s", exc, exc_info=True)
            raise ValueError("Errore nell'ottenimento del nuovo id lotto") from exc

    def token_operazione(self, co2_consumata: float, tipo_operazione: str, id_prodotto: int) -> int:
        """
        Calculate tokens assigned for an operation.

        Args:
            co2_consumata (float): CO2 consumed in operation.
            tipo_operazione (str): Operation type.
            id_prodotto (int): Product ID.

        Returns:
            int: Tokens assigned.
        """
        try:
            soglia = self.recupera_soglia(tipo_operazione, id_prodotto)
            tokens = soglia - int(co2_consumata)
            return max(tokens, 0)
        except Exception as exc:
            logger.error("Errore nel calcolo dei token: %s", exc, exc_info=True)
            return 0

    def recupera_soglia(self, tipo_operazione: str, id_prodotto: int) -> int:
        """
        Retrieve the maximum threshold for a given operation and product.

        Args:
            tipo_operazione (str): Operation type.
            id_prodotto (int): Product ID.

        Returns:
            int: Threshold value.
        """
        try:
            result = self.db.fetch_results(
                "SELECT Soglia_Massima FROM Soglie WHERE Operazione = ? AND Prodotto = ?",
                (tipo_operazione, id_prodotto),
            )
            return int(result[0][0]) if result else 0
        except Exception as exc:
            logger.error("Errore nel recupero soglia: %s", exc, exc_info=True)
            return 0
