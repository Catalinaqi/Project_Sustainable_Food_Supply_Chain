# pylint: disable=import-error
import datetime
from typing import Dict, List
from configuration.log_load_setting import logger
from model.threshold_model import ThresholdModel
from model.prodotto_finito_model import ProdottoLottoModel
from model.info_product_for_choice_model import ProductForChoiceModel
from model.product_standard_model import ProductStandardModel
from model.company_model import CompanyModel
from model.operation_estesa_model import OperazioneEstesaModel
from model.compensation_action_model import CompensationActionModel
from model.richiesta_model import RichiestaModel
from session import Session
from persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from persistence.repository_impl.compensation_action_repository_impl import CompensationActionRepositoryImpl
from persistence.repository_impl.operation_repository_impl import OperationRepositoryImpl
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from persistence.repository_impl.richieste_repository_impl import RichiesteRepositoryImpl

PERMESSI_OPERAZIONI = {
    "Agricola": ["Produzione"],
    "Trasportatore": ["Trasporto"],
    "Trasformatore": ["Trasformazione"],
    "Rivenditore": ["Rivendita"],
}


class ControllerAzienda:
    """Controller per la gestione delle operazioni aziendali e delle richieste."""

    def __init__(self) -> None:
        self._session = Session()
        self.operation_repository = OperationRepositoryImpl()
        self.compensation_action = CompensationActionRepositoryImpl()
        self.product = ProductRepositoryImpl()
        self.threshold = ThresholdRepositoryImpl()
        self.company = CompanyRepositoryImpl()
        self.richieste = RichiesteRepositoryImpl()
        logger.info("BackEnd: Inizializzazione completata dei repository")

    @property
    def id_azienda(self) -> int:
        """Restituisce l'ID dell'azienda dell'utente corrente."""
        return self._session.current_user["id_azienda"]

    @property
    def ruolo_utente(self) -> str:
        """Restituisce il ruolo dell'utente corrente."""
        return self._session.current_user["role"]

    def lista_soglie(self) -> List[ThresholdModel]:
        """Restituisce la lista delle soglie configurate."""
        return self.threshold.get_lista_soglie()

    def get_prodotti_to_composizione(self) -> List[ProdottoLottoModel]:
        """Recupera i prodotti finiti in magazzino dell'azienda corrente per composizione."""
        try:
            return self.product.get_prodotti_finiti_magazzino_azienda(self.id_azienda)
        except Exception as exc:
            logger.error(f"Errore nel recupero prodotti per composizione: {exc}")
            return []

    def lista_operazioni(self, azienda_id: int) -> List[OperazioneEstesaModel]:
        """Recupera la lista delle operazioni associate a una data azienda."""
        try:
            return self.operation_repository.get_operazioni_by_azienda(azienda_id)
        except Exception as exc:
            logger.error(f"Errore nel recupero operazioni: {exc}", exc_info=True)
            return []

    def lista_azioni_compensative(self, azienda_id: int) -> List[CompensationActionModel]:
        """Recupera la lista delle azioni compensative di un'azienda."""
        try:
            return self.compensation_action.get_lista_azioni(azienda_id)
        except Exception as exc:
            logger.error(f"Errore nel recupero azioni compensative: {exc}", exc_info=True)
            return []

    def get_materie_prime_magazzino_azienda(self) -> List[ProdottoLottoModel]:
        """Recupera le materie prime in magazzino dell'azienda corrente."""
        try:
            return self.product.get_materie_prime_magazzino_azienda(self.id_azienda)
        except Exception as exc:
            logger.error(f"Errore nel recupero materie prime: {exc}", exc_info=True)
            return []

    def get_prodotti_finiti_magazzino_azienda(self) -> List[ProdottoLottoModel]:
        """Recupera i prodotti finiti in magazzino dell'azienda corrente."""
        try:
            return self.product.get_prodotti_finiti_magazzino_azienda(self.id_azienda)
        except Exception as exc:
            logger.error(f"Errore nel recupero prodotti finiti: {exc}", exc_info=True)
            return []

    def crea_prodotto_trasformato(
        self,
        id_tipo: int,
        descrizione: str,
        quantita: int,
        quantita_per_materia: Dict[ProdottoLottoModel, int],
        co2: int,
    ) -> None:
        """
        Crea un nuovo prodotto trasformato basato su materie prime.

        Args:
            id_tipo: ID del tipo di prodotto.
            descrizione: Descrizione del prodotto trasformato.
            quantita: Quantità prodotta.
            quantita_per_materia: Dizionario di materie prime con quantità utilizzata.
            co2: Emissioni CO2 associate alla trasformazione.
        """
        try:
            self.operation_repository.inserisci_prodotto_trasformato(
                id_tipo, descrizione, quantita, quantita_per_materia,
                self.id_azienda, co2
            )
        except Exception as exc:
            logger.error(f"Errore nella creazione prodotto trasformato: {exc}", exc_info=True)

    def salva_operazione_agricola(
        self,
        tipo: str,
        data: datetime.datetime,
        co2: float,
        id_tipo_prodotto: int,
        descrizione: str,
        quantita: int,
    ) -> None:
        """
        Salva un'operazione agricola se il ruolo utente è autorizzato.

        Raises:
            PermissionError: Se l'utente non ha i permessi per il tipo di operazione.
        """
        if not self.check_utente(tipo):
            raise PermissionError("Operazione non consentita per questo utente.")
        try:
            self.operation_repository.inserisci_operazione_azienda_agricola(
                id_tipo_prodotto, descrizione, quantita, self.id_azienda, data, co2
            )
        except Exception as exc:
            logger.error(f"Errore salvataggio operazione agricola: {exc}", exc_info=True)

    def salva_operazione_distributore(
        self,
        data: datetime.datetime,
        co2: float,
        id_prodotto: int,
        id_lotto_input: int,
        quantita: int,
    ) -> None:
        """Salva un'operazione di rivendita."""
        try:
            self.operation_repository.inserisci_operazione_azienda_rivenditore(
                self.id_azienda, id_prodotto, data, co2,
                "vendita", id_lotto_input, quantita
            )
        except Exception as exc:
            logger.error(f"Errore salvataggio operazione rivendita: {exc}", exc_info=True)

    def salva_operazione_trasporto(
        self,
        id_prodotto: int,
        id_azienda_ricevente: int,
        id_azienda_richiedente: int,
        quantita: int,
        co2: float,
        id_lotto_input: int,
    ) -> None:
        """Salva un'operazione di trasporto."""
        try:
            self.operation_repository.inserisci_operazione_trasporto(
                self.id_azienda, id_lotto_input, id_prodotto,
                id_azienda_richiedente, id_azienda_ricevente, quantita, co2
            )
        except Exception as exc:
            logger.error(f"Errore salvataggio operazione trasporto: {exc}", exc_info=True)

    def get_prodotti_ordinabili(self) -> List[ProductForChoiceModel]:
        """Recupera i prodotti ordinabili in base al ruolo utente."""
        try:
            filtro = 1 if self.ruolo_utente == "Rivenditore" else None
            return self.product.get_prodotti_ordinabili(filtro)
        except Exception as exc:
            logger.error(f"Errore nel recupero prodotti ordinabili: {exc}", exc_info=True)
            return []

    def get_aziende_trasporto(self) -> List[CompanyModel]:
        """Recupera le aziende abilitate al trasporto."""
        try:
            return self.company.get_aziende_trasporto()
        except Exception as exc:
            logger.error(f"Errore nel recupero aziende trasporto: {exc}", exc_info=True)
            return []

    def invia_richiesta(
        self,
        id_az_ricevente: int,
        id_az_trasporto: int,
        id_prodotto: int,
        quantita: int,
    ) -> None:
        """Invia una nuova richiesta di operazione."""
        try:
            self.richieste.inserisci_richiesta(
                self.id_azienda, id_az_ricevente, id_az_trasporto, id_prodotto, quantita
            )
        except Exception as exc:
            logger.error(f"Errore invio richiesta: {exc}", exc_info=True)

    def get_richieste_ricevute(self) -> List[RichiestaModel]:
        """Recupera le richieste ricevute dall'azienda corrente."""
        try:
            is_trasportatore = self.ruolo_utente == "Trasportatore"
            return self.richieste.get_richieste_ricevute(self.id_azienda, check_trasporto=is_trasportatore)
        except Exception as exc:
            logger.error(f"Errore richieste ricevute: {exc}", exc_info=True)
            return []

    def get_richieste_effettuate(self) -> List[RichiestaModel]:
        """Recupera le richieste effettuate dall'azienda corrente."""
        try:
            return self.richieste.get_richieste_effettuate(self.id_azienda)
        except Exception as exc:
            logger.error(f"Errore richieste effettuate: {exc}", exc_info=True)
            return []

    def update_richiesta(self, id_richiesta: int, nuovo_stato: str) -> None:
        """Aggiorna lo stato di una richiesta."""
        try:
            self.richieste.update_richiesta(id_richiesta, nuovo_stato, self.ruolo_utente)
        except Exception as exc:
            logger.error(f"Errore aggiornamento richiesta: {exc}", exc_info=True)
            raise RuntimeError("Errore aggiornamento richiesta") from exc

    def check_utente(self, tipo_operazione: str) -> bool:
        """
        Verifica se l'utente ha i permessi per il tipo di operazione richiesto.

        Args:
            tipo_operazione: Tipo di operazione da verificare.

        Returns:
            bool: True se consentito, False altrimenti.
        """
        return tipo_operazione in PERMESSI_OPERAZIONI.get(self.ruolo_utente, [])

    def aggiungi_azione_compensativa(
        self,
        descrizione: str,
        co2: float,
        data: datetime.datetime,
    ) -> None:
        """Aggiunge una nuova azione compensativa per l'azienda corrente."""
        try:
            self.compensation_action.inserisci_azione(
                data=data,
                azienda=self.id_azienda,
                co2_compensata=co2,
                nome_azione=descrizione,
            )
        except Exception as exc:
            logger.error(f"Errore inserimento azione compensativa: {exc}", exc_info=True)

    def get_prodotti_standard(self) -> List[ProductStandardModel]:
        """Recupera la lista di prodotti standard in base al ruolo utente."""
        try:
            if self.ruolo_utente == "Agricola":
                return self.product.get_prodotti_standard_agricoli()
            if self.ruolo_utente == "Trasformatore":
                return self.product.get_prodotti_standard_trasformazione()
            raise TypeError("Utente non autorizzato")
        except Exception as exc:
            logger.error(f"Errore prodotti standard: {exc}", exc_info=True)
            return []
