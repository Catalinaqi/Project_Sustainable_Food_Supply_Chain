from abc import ABC
from typing import Optional, List
from configuration.database import Database
from configuration.log_load_setting import logger
from model.company_model import CompanyModel
from persistence.query_builder import QueryBuilder
from persistence.repository_impl.database_standard import aziende_enum


class CompanyRepositoryImpl(ABC):
    """
    Implementation of the repository for managing Azienda entities.
    """

    def __init__(self) -> None:
        super().__init__()
        self.db = Database()

    def get_aziende_trasporto(self) -> List[CompanyModel]:
        """
        Retrieve all transport companies ("Trasportatore") from the database.

        Returns:
            List[CompanyModel]: List of transport companies.
        """
        query_builder = QueryBuilder()
        query_builder.select("*").table("Azienda").where("Tipo", "=", "Trasportatore")
        query, values = query_builder.get_query()

        try:
            results = self.db.fetch_results(query, values)
            return [CompanyModel(*row) for row in results]
        except Exception as exc:
            logger.error(f"Error retrieving transport companies: {exc}")
            return []

    def get_lista_aziende(
        self,
        tipo: Optional[aziende_enum] = None,
        nome: Optional[str] = None,
        id_azienda: Optional[int] = None,
    ) -> List[CompanyModel]:
        """
        Retrieve a list of companies filtered optionally by type, name, or ID.

        Args:
            tipo (Optional[aziende_enum]): Filter by company type.
            nome (Optional[str]): Filter by company name.
            id_azienda (Optional[int]): Filter by company ID.

        Returns:
            List[CompanyModel]: List of matching companies.
        """
        query_builder = QueryBuilder()
        query_builder.select("*").table("Azienda")

        if not tipo:
            query_builder.where("Tipo", "!=", str(aziende_enum.CERIFICATORE.value))
        else:
            query_builder.where("Tipo", "=", str(tipo.value))

        if nome:
            query_builder.where("Nome", "=", nome)

        if id_azienda:
            query_builder.where("Id_azienda", "=", id_azienda)

        query, values = query_builder.get_query()

        try:
            results = self.db.fetch_results(query, values)
            return [CompanyModel(*row) for row in results]
        except Exception as exc:
            logger.error(f"Error retrieving company list: {exc}")
            return []

    def get_azienda(self, n: int) -> Optional[CompanyModel]:
        """
        Retrieve the company at index `n` from the list of companies.

        Args:
            n (int): Index of the company to retrieve.

        Returns:
            Optional[CompanyModel]: The company if found, else None.
        """
        companies = self.get_lista_aziende()
        try:
            return companies[n]
        except IndexError:
            logger.warning(f"Index {n} out of range when retrieving company.")
            return None
