import datetime
import hashlib
import hmac
import os
import sqlite3
from abc import ABC
from typing import Final

from pydantic import BaseModel

from configuration.database import Database
from configuration.log_load_setting import logger
from model.operation_estesa_model import OperazioneEstesaModel
from model.prodotto_finito_model import ProdottoLottoModel
from persistence.query_builder import QueryBuilder
from persistence.repository_impl import db_default_string


class FirmaRequest(BaseModel):
    tipo_operazione: str
    id_prodotto: int
    soglia_massima: int


class VerificaRequest(FirmaRequest):
    signature: str


SECRET_KEY = os.getenv("_KEY", "default_dev_key")


class OperationRepositoryImpl(ABC):
    QUERY_UPDATE_AZIENDA: Final = (
        """
        UPDATE Azienda
        SET Co2_emessa = Co2_emessa + ?, Token = Token + ?
        WHERE Id_azienda = ?;
        """
    )

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()

    def get_operazioni_by_azienda(self, azienda: int) -> list[OperazioneEstesaModel]:
        query, value = (
            self.query_builder
            .select(
                "Operazione.Id_operazione",
                "Prodotto.Id_prodotto",
                "Prodotto.Nome",
                "Operazione.Data_operazione",
                "Operazione.Consumo_CO2",
                "Operazione.Tipo",
                "Operazione.quantita",
            )
            .table("Operazione")
            .join("Prodotto", "Operazione.Id_prodotto", "Prodotto.Id_prodotto")
            .where("Operazione.Id_azienda", "=", azienda)
            .get_query()
        )

        try:
            results = self.db.fetch_results(query, value)
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
        except Exception as e:
            logger.error("Error fetching operations by company: %s", e, exc_info=True)
            return []

    def inserisci_operazione_azienda_rivenditore(
        self, azienda: int, prodotto: int, data: datetime.datetime, co2: float,
        evento: str, id_lotto_input: int, quantita: int
    ) -> None:
        try:
            queries = []
            value_output_lotto = self.get_next_id_lotto_output()

            queries.append((
                "INSERT INTO ComposizioneLotto (id_lotto_output, id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)",
                (value_output_lotto, id_lotto_input, quantita)
            ))

            queries.append((
                """
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Data_operazione, Consumo_CO2, Tipo, quantita)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (azienda, prodotto, value_output_lotto, data, co2, evento, quantita)
            ))

            queries.append((
                "UPDATE Magazzino SET quantita = quantita - ? WHERE Id_azienda = ? AND Id_lotto = ?",
                (quantita, azienda, id_lotto_input)
            ))

            token_assegnati = self.token_operazione(co2, evento, prodotto)
            queries.append((self.QUERY_UPDATE_AZIENDA, (co2, token_assegnati, azienda)))

            self.db.execute_transaction(queries)

        except Exception as e:
            raise Exception(f"Errore inserimento operazione rivenditore: {str(e)}") from e

    def get_next_id_lotto_output(self) -> int:
        try:
            result = self.db.fetch_one("SELECT IFNULL(MAX(id_lotto_output), 0) + 1 FROM ComposizioneLotto;")
            return result or 1
        except Exception as e:
            raise ValueError("Errore nell'ottenimento del nuovo id lotto") from e

    def token_operazione(self, co2_consumata: int, tipo_operazione: str, id_prodotto: int) -> int:
        try:
            return self.recupera_soglia(tipo_operazione, id_prodotto) - co2_consumata
        except Exception as e:
            logger.error("Errore nel calcolo dei token: %s", e)
            return 0

    def recupera_soglia(self, tipo_operazione: str, id_prodotto: int) -> int:
        try:
            result = self.db.fetch_results(
                "SELECT Soglia_Massima FROM Soglie WHERE Operazione = ? AND Prodotto = ?",
                (tipo_operazione, id_prodotto)
            )
            return result[0][0] if result else 0
        except Exception as e:
            logger.error("Errore nel recupero soglia: %s", e)
            return 0