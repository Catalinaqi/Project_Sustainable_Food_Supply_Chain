# pylint: disable=import-error
import datetime
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
    "Rivenditore": ["Rivendita"]
}


class ControllerAzienda:
    """Controller per la gestione delle operazioni aziendali."""

    def __init__(self):
        self._session = Session()
        self.operation_repository = OperationRepositoryImpl()
        self.compensation_action = CompensationActionRepositoryImpl()
        self.product = ProductRepositoryImpl()
        self.threshold = ThresholdRepositoryImpl()
        self.company = CompanyRepositoryImpl()
        self.richieste = RichiesteRepositoryImpl()
        logger.info("BackEnd: Inizializzazione completata dei repository")

    @property
    def id_azienda(self):
        return self._session.current_user["id_azienda"]

    @property
    def ruolo_utente(self):
        return self._session.current_user["role"]

    def lista_soglie(self) -> list[ThresholdModel]:
        return self.threshold.get_lista_soglie()

    def get_prodotti_to_composizione(self) -> list[ProdottoLottoModel]:
        try:
            return self.product.get_prodotti_finiti_magazzino_azienda(self.id_azienda)
        except Exception as exc:
            logger.error("Errore nel recupero prodotti per composizione: %s", exc)
            return []

    def lista_operazioni(self, azienda_id: int) -> list[OperazioneEstesaModel]:
        try:
            return self.operation_repository.get_operazioni_by_azienda(azienda_id)
        except Exception as exc:
            logger.error("Errore nel recupero operazioni: %s", exc, exc_info=True)
            return []

    def lista_azioni_compensative(self, azienda_id: int) -> list[CompensationActionModel]:
        try:
            return self.compensation_action.get_lista_azioni(azienda_id)
        except Exception as exc:
            logger.error("Errore nel recupero azioni compensative: %s", exc, exc_info=True)
            return []

    def get_materie_prime_magazzino_azienda(self) -> list[ProdottoLottoModel]:
        try:
            return self.product.get_materie_prime_magazzino_azienda(self.id_azienda)
        except Exception as exc:
            logger.error("Errore nel recupero materie prime: %s", exc, exc_info=True)
            return []

    def get_prodotti_finiti_magazzino_azienda(self) -> list[ProdottoLottoModel]:
        try:
            return self.product.get_prodotti_finiti_magazzino_azienda(self.id_azienda)
        except Exception as exc:
            logger.error("Errore nel recupero prodotti finiti: %s", exc, exc_info=True)
            return []

    def crea_prodotto_trasformato(
        self,
        id_tipo: int,
        descrizione: str,
        quantita: int,
        quantita_per_materia: dict[ProdottoLottoModel, int],
        co2: int,
    ):
        try:
            self.operation_repository.inserisci_prodotto_trasformato(
                id_tipo, descrizione, quantita, quantita_per_materia,
                self.id_azienda, co2
            )
        except Exception as exc:
            logger.error("Errore nella creazione prodotto trasformato: %s", exc, exc_info=True)

    def salva_operazione_agricola(
        self,
        tipo: str,
        data: datetime.datetime,
        co2: float,
        id_tipo_prodotto: int,
        descrizione: str,
        quantita: int,
    ):
        if not self.check_utente(tipo):
            raise PermissionError("Operazione non consentita per questo utente.")
        self.operation_repository.inserisci_operazione_azienda_agricola(
            id_tipo_prodotto, descrizione, quantita, self.id_azienda, data, co2
        )

    def salva_operazione_distributore(
        self,
        data: datetime.datetime,
        co2: float,
        id_prodotto: int,
        id_lotto_input: int,
        quantita: int,
    ):
        try:
            self.operation_repository.inserisci_operazione_azienda_rivenditore(
                self.id_azienda, id_prodotto, data, co2,
                "vendita", id_lotto_input, quantita
            )
        except Exception as exc:
            logger.error("Errore salvataggio operazione rivendita: %s", exc)

    def salva_operazione_trasporto(
        self,
        id_prodotto: int,
        id_azienda_ricevente: int,
        id_azienda_richiedente: int,
        quantita: int,
        co2: float,
        id_lotto_input: int
    ):
        self.operation_repository.inserisci_operazione_trasporto(
            self.id_azienda, id_lotto_input, id_prodotto,
            id_azienda_richiedente, id_azienda_ricevente, quantita, co2
        )

    def get_prodotti_ordinabili(self) -> list[ProductForChoiceModel]:
        try:
            filtro = 1 if self.ruolo_utente == "Rivenditore" else None
            return self.product.get_prodotti_ordinabili(filtro)
        except Exception as exc:
            logger.error("Errore nel recupero prodotti ordinabili: %s", exc, exc_info=True)
            return []

    def get_aziende_trasporto(self) -> list[CompanyModel]:
        try:
            return self.company.get_aziende_trasporto()
        except Exception as exc:
            logger.error("Errore nel recupero aziende trasporto: %s", exc, exc_info=True)
            return []

    def invia_richiesta(self, id_az_ricevente: int, id_az_trasporto: int, id_prodotto: int, quantita: int):
        try:
            self.richieste.inserisci_richiesta(
                self.id_azienda, id_az_ricevente, id_az_trasporto, id_prodotto, quantita
            )
        except Exception as exc:
            logger.error("Errore invio richiesta: %s", exc, exc_info=True)

    def get_richieste_ricevute(self) -> list[RichiestaModel]:
        try:
            is_trasportatore = self.ruolo_utente == "Trasportatore"
            return self.richieste.get_richieste_ricevute(self.id_azienda, check_trasporto=is_trasportatore)
        except Exception as exc:
            logger.error("Errore richieste ricevute: %s", exc, exc_info=True)
            return []

    def get_richieste_effettuate(self) -> list[RichiestaModel]:
        try:
            return self.richieste.get_richieste_effettuate(self.id_azienda)
        except Exception as exc:
            logger.error("Errore richieste effettuate: %s", exc, exc_info=True)
            return []

    def update_richiesta(self, id_richiesta: int, nuovo_stato: str):
        try:
            self.richieste.update_richiesta(id_richiesta, nuovo_stato, self.ruolo_utente)
        except Exception as exc:
            logger.error("Errore aggiornamento richiesta: %s", exc, exc_info=True)
            raise RuntimeError("Errore aggiornamento richiesta") from exc

    def check_utente(self, tipo_operazione: str) -> bool:
        return tipo_operazione in PERMESSI_OPERAZIONI.get(self.ruolo_utente, [])

    def aggiungi_azione_compensativa(self, descrizione: str, co2: float, data: datetime.datetime):
        try:
            self.compensation_action.inserisci_azione(
                data=data,
                azienda=self.id_azienda,
                co2_compensata=co2,
                nome_azione=descrizione
            )
        except Exception as exc:
            logger.error("Errore inserimento azione compensativa: %s", exc)

    def get_prodotti_standard(self) -> list[ProductStandardModel]:
        try:
            if self.ruolo_utente == "Agricola":
                return self.product.get_prodotti_standard_agricoli()
            if self.ruolo_utente == "Trasformatore":
                return self.product.get_prodotti_standard_trasformazione()
            raise TypeError("Utente non autorizzato")
        except Exception as exc:
            logger.error("Errore prodotti standard: %s", exc)
            return []
