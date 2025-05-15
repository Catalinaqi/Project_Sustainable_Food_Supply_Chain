# pylint: disable=import-error
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
    Controller per accesso ai dati di aziende, prodotti, certificazioni e soglie.
    Inizializza le istanze delle classi di repository per l'accesso ai dati.
    """

    def __init__(self) -> None:
        self.certification = CertificationRepositoryImpl()
        self.product = ProductRepositoryImpl()
        self.threshold = ThresholdRepositoryImpl()
        self.company = CompanyRepositoryImpl()
        logger.info(
            "BackEnd: Successful initialization of repository implementations"
        )

    def lista_rivenditori(self) -> List[CompanyModel]:
        """Restituisce la lista delle aziende di tipo rivenditore."""
        return self.company.get_lista_aziende(tipo=aziende_enum.RIVENDIORE)

    def lista_aziende(self) -> List[CompanyModel]:
        """Restituisce la lista di tutte le aziende."""
        return self.company.get_lista_aziende()

    def lista_aziende_filtro_tipo(self, tipo_azienda: aziende_enum) -> List[CompanyModel]:
        """Restituisce la lista di aziende filtrate per tipo."""
        return self.company.get_lista_aziende(tipo=tipo_azienda)

    def azienda_by_nome(self, nome_azienda: str) -> Optional[CompanyModel]:
        """Restituisce l'azienda corrispondente al nome."""
        aziende = self.company.get_lista_aziende(nome=nome_azienda)
        if aziende:
            return aziende[0]
        logger.warning(f"Azienda con nome '{nome_azienda}' non trovata.")
        return None

    def lista_prodotti(self) -> List[ProductModel]:
        """Restituisce la lista di tutti i prodotti finali."""
        return self.product.get_lista_prodotti()

    def is_certificato(self, id_prodotto: int) -> Optional[bool]:
        """Verifica se un prodotto è certificato."""
        try:
            return self.certification.is_certificato(id_prodotto)
        except Exception as e:
            logger.error(
                f"Errore durante il recupero della certificazione per il prodotto {id_prodotto}: {e}"
            )
            return None

    def certificazione_by_prodotto(self, id_prodotto: int) -> Optional[CertificationModel]:
        """Restituisce la certificazione associata a un prodotto."""
        try:
            return self.certification.get_certificazione_by_prodotto(id_prodotto)
        except Exception as e:
            logger.error(
                f"Errore durante il recupero della certificazione per il prodotto {id_prodotto}: {e}"
            )
            return None

    def scarto_soglia(self, co2: float, operazione: str, prodotto: ProductModel) -> Optional[float]:
        """Calcola lo scarto rispetto alla soglia di riferimento per CO2."""
        try:
            soglia = self.threshold.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
            return soglia - co2
        except Exception as e:
            logger.error(f"Errore nel calcolo dello scarto soglia: {e}")
            return None

    def carica_prodotto_con_storia(self, prodotto_id: int) -> Optional[ProductModel]:
        """
        Carica un prodotto con la sua storia a partire dal suo ID.
        Nota: implementazione simulata.
        """
        try:
            prodotto = self.get_fake_prodotto(prodotto_id)  # Metodo da implementare o mock
            return prodotto
        except Exception as e:
            logger.error(f"Errore durante il caricamento del prodotto con ID {prodotto_id}: {e}")
            return None

    # Funzioni Mock

    def get_prodotti(self) -> List[ProdottoFinito]:
        """Recupera la lista di prodotti finiti."""
        try:
            return self.product.get_lista_prodotti()
        except Exception as e:
            logger.error(f"Errore durante il recupero dei prodotti: {e}")
            return []

    def get_certificazioni_by_lotto(self, lotto_id: int) -> List[CertificationModel]:
        """Recupera la lista di certificazioni associate a un lotto."""
        try:
            return self.certification.get_certificati_catena(lotto_id) or []
        except Exception as e:
            logger.error(f"Errore nel recuperare i certificati per lotto {lotto_id}: {e}")
            return []
