"""Controller per l'accesso ai dati pubblici: aziende, prodotti e certificazioni."""
# pylint: disable=no-name-in-module
# # pylint: disable=import-error
from typing import List, Optional
from configuration.log_load_setting import logger
from model.company_model import CompanyModel
from model.product_model import ProductModel
from model.prodotto_finito_cliente import ProdottoFinito
from model.certification_model import CertificationModel
from persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from persistence.repository_impl.certification_repository_impl import CertificationRepositoryImpl
from persistence.repository_impl.database_standard import aziende_enum


class ControllerGuest:
    """
    Controller per accesso ai dati pubblici:
    - Aziende
    - Prodotti
    - Certificazioni
    """

    def __init__(self) -> None:
        self.certification = CertificationRepositoryImpl()
        self.product = ProductRepositoryImpl()
        self.threshold = ThresholdRepositoryImpl()
        self.company = CompanyRepositoryImpl()
        logger.info("BackEnd: Successful initialization of repository implementations")

    def lista_rivenditori(self) -> List[CompanyModel]:
        """Restituisce la lista delle aziende di tipo rivenditore."""
        return self.company.get_lista_aziende(tipo=aziende_enum.RIVENDIORE)

    def lista_aziende(self) -> List[CompanyModel]:
        """Restituisce la lista di tutte le aziende disponibili nel sistema."""
        return self.company.get_lista_aziende()

    def lista_aziende_filtro_tipo(self, tipo_azienda: aziende_enum) -> List[CompanyModel]:
        """Restituisce la lista di aziende filtrate per tipo."""
        return self.company.get_lista_aziende(tipo=tipo_azienda)

    def azienda_by_nome(self, nome_azienda: str) -> Optional[CompanyModel]:
        """Restituisce l'azienda corrispondente al nome specificato."""
        aziende = self.company.get_lista_aziende(nome=nome_azienda)
        if aziende:
            return aziende[0]
        logger.warning("Azienda con nome '%s' non trovata.", nome_azienda)
        return None

    def lista_prodotti(self) -> List[ProductModel]:
        """Restituisce la lista di tutti i prodotti finali registrati."""
        return self.product.get_lista_prodotti()

    def is_certificato(self, id_prodotto: int) -> Optional[bool]:
        """Verifica se un prodotto è certificato."""
        try:
            return self.certification.is_certificato(id_prodotto)
        except Exception as error:  # pylint: disable=broad-except
            logger.error(
                "Errore durante il recupero della certificazione per il prodotto %d: %s",
                id_prodotto,
                error
            )
            return None

    def certificazione_by_prodotto(self, id_prodotto: int) -> Optional[CertificationModel]:
        """Restituisce la certificazione associata a un prodotto."""
        try:
            return self.certification.get_certificazione_by_prodotto(id_prodotto)
        except Exception as error:  # pylint: disable=broad-except
            logger.error(
                "Errore durante il recupero della certificazione per il prodotto %d: %s",
                id_prodotto,
                error
            )
            return None

    def get_prodotti(self) -> List[ProdottoFinito]:
        """Recupera la lista di prodotti finiti con eventuali dettagli aggiuntivi."""
        try:
            return self.product.get_lista_prodotti()
        except Exception as error:  # pylint: disable=broad-except
            logger.error("Errore durante il recupero dei prodotti: %s", error)
            return []

    def get_certificazioni_by_lotto(self, lotto_id: int) -> List[CertificationModel]:
        """Recupera la lista di certificazioni associate a un lotto specifico."""
        try:
            certificati = self.certification.get_certificati_catena(lotto_id)
            return certificati if certificati is not None else []
        except Exception as error:  # pylint: disable=broad-except
            logger.error("Errore nel recuperare i certificati per lotto %d: %s", lotto_id, error)
            return []
