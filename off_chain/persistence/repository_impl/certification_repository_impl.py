import datetime
from abc import ABC
from typing import List

from configuration.database import Database
from model.certification_model import CertificationModel
from model.lotto_for_cetification_model import LottoForCertificaion
from model.certification_for_lotto import CertificationForLotto
from persistence.query_builder import QueryBuilder
from configuration.log_load_setting import logger


class CertificationRepositoryImpl(ABC):
    """
    Repository implementation for handling certifications.
    """

    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()

    def get_certifications_by_product_interface(self, id_prodotto: int) -> List:
        """
        Get all certifications related to a specific product.
        """
        query, values = (
            self.query_builder
            .select(
                "Certificato.Id_certificato", "Prodotto.Nome",
                "Certificato.Descrizione", "Azienda.Nome", "Certificato.Data"
            )
            .table("Certificato")
            .join("Azienda", "Certificato.Id_azienda_certificatore", "Azienda.Id_azienda")
            .join("Prodotto", "Certificato.Id_prodotto", "Prodotto.Id_prodotto")
            .where("Certificato.Id_prodotto", "=", id_prodotto)
            .get_query()
        )
        return self.db.fetch_results(query, values)

    def get_numero_certificazioni(self, id_azienda: int) -> int:
        """
        Count the number of certifications by a given company.
        """
        query, values = (
            self.query_builder
            .table("Certificato")
            .select("COUNT(*)")
            .where("Id_azienda_certificatore", "=", id_azienda)
            .get_query()
        )
        try:
            result = self.db.fetch_results(query, values)
            return int(result[0]) if result else 0
        except (IndexError, TypeError, ValueError) as err:
            logger.error(f"Errore nel conteggio delle certificazioni: {err}")
            raise ValueError("Impossibile recuperare il numero di certificazioni") from err

    def is_certificato(self, id_prodotto: int) -> bool:
        """
        Check if a product has been certified.
        """
        query, values = (
            self.query_builder
            .table("Certificato")
            .select("*")
            .where("Id_prodotto", "=", id_prodotto)
            .get_query()
        )
        return bool(self.db.fetch_results(query, values))

    def get_certificazione_by_prodotto(self, id_prodotto: int) -> List:
        """
        Retrieve certification info for a product.
        """
        query, values = (
            self.query_builder
            .select(
                "Certificato.Id_certificato", "Prodotto.Nome",
                "Certificato.Descrizione", "Azienda.Nome", "Certificato.Data"
            )
            .table("Certificato")
            .join("Azienda", "Certificato.Id_azienda_certificatore", "Azienda.Id_azienda")
            .join("Prodotto", "Certificato.Id_prodotto", "Prodotto.Id_prodotto")
            .where("Certificato.Id_prodotto", "=", id_prodotto)
            .get_query()
        )
        return self.db.fetch_results(query, values)

    def get_certificati_catena(self, id_lotto: int) -> List[CertificationModel]:
        """
        Get all certifications for a batch and its input batches recursively.
        """
        certificati: List[CertificationModel] = []
        try:
            query, values = (
                self.query_builder
                .select("Id_certificato", "Id_lotto", "Descrizione", "az.Nome", "Data")
                .table("Certificato")
                .join("Azienda AS az", "Id_azienda_certificatore", "az.Id_azienda")
                .where("Id_lotto", "=", id_lotto)
                .get_query()
            )
            result = self.db.fetch_results(query, values)
            certificati.extend(CertificationModel(*row) for row in result)

            lotti_input = self.db.fetch_results(
                "SELECT id_lotto_input FROM ComposizioneLotto WHERE id_lotto_output = ?",
                (id_lotto,)
            )
            for (id_lotto_input,) in lotti_input:
                certificati.extend(self.get_certificati_catena(id_lotto_input))

        except Exception as err:
            logger.error(f"Errore durante la conversione dei certificati: {err}")
        return certificati

    def get_lotti_certificabili(self) -> List[LottoForCertificaion]:
        """
        Get all batches that can be certified (excluding transport and sales).
        """
        try:
            query, values = (
                self.query_builder
                .select(
                    "o.Id_lotto", "o.Tipo", "o.Data_operazione",
                    "o.Consumo_CO2", "a.Nome", "p.Nome"
                )
                .table("Operazione AS o")
                .where("o.Tipo", "!=", "trasporto")
                .where("o.Tipo", "!=", "vendita")
                .join("Prodotto AS p", "o.Id_prodotto", "p.Id_prodotto")
                .join("Azienda AS a", "o.Id_azienda", "a.Id_azienda")
                .get_query()
            )
            result = self.db.fetch_results(query, values)
            return [LottoForCertificaion(*row) for row in result]
        except Exception as err:
            logger.error(f"Errore nel recupero dei lotti: {err}")
            return []

    def get_certificati_lotto(self, id_lotto: int) -> List[CertificationForLotto]:
        """
        Retrieve certifications related to a specific batch.
        """
        try:
            query, values = (
                self.query_builder
                .select("Descrizione", "az.Nome", "Data")
                .table("Certificato")
                .join("Azienda AS az", "Id_azienda_certificatore", "az.Id_azienda")
                .where("Id_lotto", "=", id_lotto)
                .get_query()
            )
            result = self.db.fetch_results(query, values)
            if not result:
                logger.warning(f"Nessuna certificazione trovata per il lotto {id_lotto}")
            return [CertificationForLotto(*row) for row in result]
        except Exception as err:
            logger.error(f"Errore nel recupero dei certificati: {err}")
            return []

    def aggiungi_certificazione(self, id_lotto: int, descrizione: str, id_azienda: int) -> None:
        """
        Insert a new certification into the database.
        """
        try:
            query = """
                INSERT INTO Certificato (Id_lotto, Descrizione, Id_azienda_certificatore)
                VALUES (?, ?, ?)
            """
            values = (id_lotto, descrizione, id_azienda)
            self.db.execute_query(query, values)
        except Exception as err:
            logger.error(f"Errore nell'aggiunta del certificato: {err}")
