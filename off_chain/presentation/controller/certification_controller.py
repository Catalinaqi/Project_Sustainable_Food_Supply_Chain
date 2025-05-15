# pylint: disable=import-error
"""
Controller per la gestione delle certificazioni da parte del certificatore.
Inizializza i repository per certificazioni, prodotti, soglie e aziende.
"""
from configuration.log_load_setting import logger
from model.lotto_for_cetification_model import LottoForCertificaion
from model.certification_for_lotto import CertificationForLotto
from session import Session
from persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from persistence.repository_impl.certification_repository_impl import CertificationRepositoryImpl


class ControllerCertificatore:
    """
    Controller per il certificatore. Fornisce metodi per gestire e recuperare informazioni
    su certificazioni, prodotti, aziende e soglie.
    """

    def __init__(self):
        self.certification = CertificationRepositoryImpl()
        self.product = ProductRepositoryImpl()
        self.threshold = ThresholdRepositoryImpl()
        self.company = CompanyRepositoryImpl()
        logger.info("BackEnd: Inizializzazione completata dei repository per certificatore")

    def get_dettaglio_azienda(self, id_azienda: int):
        """
        Restituisce il numero di certificazioni per una determinata azienda.
        """
        try:
            return self.certification.get_numero_certificazioni(id_azienda)
        except Exception as exc:
            logger.error("Errore nel recupero dei dettagli azienda: %s", exc, exc_info=True)
            return None

    def certificazione_by_prodotto(self, id_prodotto: int):
        """
        Restituisce la certificazione associata a un prodotto.
        """
        try:
            return self.certification.get_certificazione_by_prodotto(id_prodotto)
        except Exception as exc:
            logger.error("Errore nel recupero della certificazione del prodotto: %s", exc, exc_info=True)
            return None

    def lista_prodotti(self):
        """
        Restituisce la lista di tutti i prodotti registrati.
        """
        try:
            return self.product.get_lista_prodotti()
        except Exception as exc:
            logger.error("Errore nel recupero della lista prodotti: %s", exc, exc_info=True)
            return []

    def is_certificato(self, id_prodotto: int) -> str:
        """
        Metodo placeholder per determinare se un prodotto è certificato.
        TODO: implementare verifica reale.
        """
        # FIXME: Implementare logica di verifica reale
        return "certificato"

    def get_lotti_certificabili(self) -> list[LottoForCertificaion]:
        """
        Restituisce la lista dei lotti certificabili.
        """
        try:
            return self.certification.get_lotti_certificabili()
        except Exception as exc:
            logger.error("Errore nel recupero dei lotti certificabili: %s", exc, exc_info=True)
            return []

    def get_certificati_lotto(self, id_lotto: int) -> list[CertificationForLotto]:
        """
        Restituisce la lista di certificazioni associate a un lotto.
        """
        try:
            return self.certification.get_certificati_lotto(id_lotto)
        except Exception as exc:
            logger.error("Errore nel recupero dei certificati del lotto: %s", exc, exc_info=True)
            return []

    def aggiungi_certificazione(self, id_lotto: int, descrizione: str):
        """
        Aggiunge una nuova certificazione a un lotto.
        """
        try:
            id_azienda = Session().current_user["id_azienda"]
            self.certification.aggiungi_certificazione(id_lotto, descrizione, id_azienda)
        except Exception as exc:
            logger.error("Errore nell'aggiunta della certificazione: %s", exc, exc_info=True)
