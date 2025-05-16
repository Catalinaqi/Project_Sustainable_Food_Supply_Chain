# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace

import datetime
from configuration.log_load_setting import logger # Importato una sola volta
from model.threshold_model import ThresholdModel
from model.materia_prima_model import MateriaPrimaModel
from model.info_product_for_choice_model import ProductForChoiceModel
from model.product_standard_model import ProductStandardModel
from model.company_model import CompanyModel
from model.operation_estesa_model import OperazioneEstesaModel
from model.compensation_action_model import CompensationActionModel
from model.prodotto_finito_model import ProdottoFinitoModel
from model.richiesta_model import RichiestaModel
from session import Session
from persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from persistence.repository_impl.compensation_action_repository_impl import CompensationActionRepositoryImpl
from persistence.repository_impl.operation_repository_impl import OperationRepositoryImpl
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from persistence.repository_impl.richieste_repository_impl import RichiesteRepositoryImpl
# from persistence.repository_impl import db_default_string # W0611: Rimosso import inutilizzato


PERMESSI_OPERAZIONI = {
    "Agricola": ["Produzione"],
    "Trasportatore": ["Trasporto"],
    "Trasformatore": ["Trasformazione"],
    "Rivenditore": ["Rivendita"]
}


class ControllerAzienda:
    """
    As the instance has been created, in the repository implement layer, to access your methods,
    we initialize the instances of the classes 'class instances' with:
            OperationRepositoryImpl()
            ProductRepositoryImpl()
            ThresholdRepositoryImpl()
            CompanyRepositoryImpl()
    """

    def __init__(self):
        self.operation_repository = OperationRepositoryImpl()
        self.compensation_action = CompensationActionRepositoryImpl()
        self.product = ProductRepositoryImpl()
        self.threshold = ThresholdRepositoryImpl()
        self.company = CompanyRepositoryImpl()
        self.richieste = RichiesteRepositoryImpl()
        logger.info("BackEnd: Successful initialization of 'class instances' for repository implements")

    # Restituisce tutte le soglie
    def lista_soglie(self) -> list[ThresholdModel]:
        # repo = ThresholdRepositoryImpl()
        lista_soglie = self.threshold.get_lista_soglie()
        return lista_soglie

    # W0101, W0107: Rimosso metodo vuoto e pass non necessario
    # Restituisce il dettaglio della soglia selezionata dato l'indice n
    # def get_dettaglio_soglia(self, n):
    #     pass

    # Restituisce gli elementi da visualizzare nella combo box
    # Restituisce le opzioni per la combo box del dialog per la composizione
    # R1710: Assicurato che tutti i percorsi ritornino un valore o nessuno. Qui si ritorna sempre.
    def get_prodotti_to_composizione(self) -> list[ProdottoFinitoModel]:
        try:
            return self.product.get_prodotti_magazzino(Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True) # Aggiunto exc_info per tracciabilità
            return [] # Ritorna lista vuota in caso di errore

    # W0105: Rimosse stringhe inutili che sembravano commenti
    # """ funzioni Mock"""
    # """ Funzioni funzionali """

    def lista_operazioni(self, azienda: int) -> list[OperazioneEstesaModel]:
        # repo = OperationRepositoryImpl()
        try:
            lista_operazioni = self.operation_repository.get_operazioni_by_azienda(azienda)
            return lista_operazioni
        except Exception as e:
            logger.error(f"Error al obtener la lista di operazioni: {e}", exc_info=True)
            return []

    def lista_azioni_compensative(self, azienda: int) -> list[CompensationActionModel]:
        try:
            lista_azioni_compensative = self.compensation_action.get_lista_azioni(azienda)
            return lista_azioni_compensative
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle azioni compensative: {e}", exc_info=True)
            return []

    def get_materie_magazzino(self) -> list[MateriaPrimaModel]:
        try:
            materie_prime = self.product.get_materie_magazzino(Session().current_user["id_azienda"])
            return materie_prime
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle materie prime: {e}", exc_info=True)
            return []

    def get_prodotti_magazzino(self) -> list[ProdottoFinitoModel]:
        try:
            prodotti_finiti = self.product.get_prodotti_magazzino(Session().current_user["id_azienda"])
            return prodotti_finiti
        except Exception as e: # Mantenuto 'e' come richiesto
            logger.error(f"Errore nell'ottenere la lista delle materie prime: {e}", exc_info=True)
            return []

    # R0913, R0917: Questi errori riguardano troppi argomenti.
    # Per mantenere la funzionalità, non li ho cambiati strutturalmente (es. usando un dataclass),
    # ma se il codice fosse mio, considererei di raggruppare i parametri.
    # R1710, R1711: Questo metodo non ritornava nulla esplicitamente.
    # Se non c'è un valore di ritorno significativo, è meglio non avere un `return None` esplicito
    # oppure ritornare un booleano per indicare successo/fallimento.
    # Ho rimosso il return None implicito alla fine.
    def crea_prodotto_trasformato(self, id_tipo: int, descrizione: str, quantita: int,
                                  quantita_usata_per_materia: dict[MateriaPrimaModel, int], co2: int):
        try:
            id_azienda = Session().current_user["id_azienda"]
            self.operation_repository.inserisci_prodotto_trasformato(
                id_tipo, descrizione, quantita, quantita_usata_per_materia,
                id_azienda, co2_consumata=co2
            )
            # Potrebbe essere utile ritornare True in caso di successo
        except Exception as e:
            logger.error(f"Errore nella creazione del prodotto trasformato: {e}", exc_info=True)
            # E False o sollevare l'eccezione in caso di errore

    # W0311: Corretta indentazione
    # R0913, R0917: Vedi commento sopra per crea_prodotto_trasformato
    def salva_operazione_agricola(self, tipo: str, data: datetime,
                                  co2: float, id_tipo_prodotto: int, descrizione: str, quantita: int
                                 ):
        if not self.check_utente(tipo):
            raise PermissionError("Operazione non consentita per questo utente.")

        self.operation_repository.inserisci_operazione_azienda_agricola(
            id_tipo_prodotto, descrizione, quantita, Session().current_user["id_azienda"], data, co2,
        )

    def salva_operazione_distributore(self, data: datetime, co2: float, id_prodotto,
                                      id_lotto_input: int, quantita: int):
        try:
            self.operation_repository.inserisci_operazione_azienda_rivenditore(
                Session().current_user["id_azienda"],
                id_prodotto, data, co2, "vendita", id_lotto_input, quantita
            )
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)

    # R0913, R0917: Vedi commento sopra per crea_prodotto_trasformato
    def salva_operazione_trasporto(self, id_prodotto: int, id_azienda_ricevente: int,
                                   id_azienda_richiedente: int, quantita: int, co2: float,
                                   id_lotto_input: int):
        # W0311: Corretta indentazione
        self.operation_repository.inserisci_operazione_trasporto(
            Session().current_user["id_azienda"], id_lotto_input, id_prodotto,
            id_azienda_richiedente, id_azienda_ricevente, quantita, co2
        )

    def get_prodotti_ordinabili(self) -> list[ProductForChoiceModel]:
        try:
            if Session().current_user["role"] == "Rivenditore":
                prodotti = self.product.get_prodotti_ordinabili(1)
            else:
                prodotti = self.product.get_prodotti_ordinabili()
            return prodotti
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista dei prodotti ordinabili: {e}", exc_info=True)
            return []

    def get_aziende_trasporto(self) -> list[CompanyModel]:
        try:
            aziende = self.company.get_aziende_trasporto()
            return aziende
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle aziende di trasporto: {e}", exc_info=True)
            return []

    # R0913, R0917: Vedi commento sopra
    def invia_richiesta(self, id_az_ricevente: int, id_az_trasporto: int,
                        id_prodotto: int, quantita: int):
        try:
            self.richieste.inserisci_richiesta(
                Session().current_user["id_azienda"], id_az_ricevente,
                id_az_trasporto, id_prodotto, quantita
            )
        except Exception as e:
            logger.error(f"Errore nell'invio della richiesta: {e}", exc_info=True)
        # W0107: Rimosso pass non necessario
        # pass

    def get_richieste_ricevute(self) -> list[RichiestaModel]:
        try:
            if Session().current_user["role"] == "Trasportatore":
                # W0311: Corretta indentazione
                richieste = self.richieste.get_richieste_ricevute(
                    Session().current_user["id_azienda"], check_trasporto=True
                )
            else:
                richieste = self.richieste.get_richieste_ricevute(
                    Session().current_user["id_azienda"]
                )
            return richieste
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle richieste ricevute: {e}", exc_info=True)
            return []

    def get_richieste_effettuate(self) -> list[RichiestaModel]:
        try:
            richieste = self.richieste.get_richieste_effettuate(Session().current_user["id_azienda"])
            return richieste
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle richieste effettuate: {e}", exc_info=True)
            return []

    def update_richiesta(self, id_richiesta: int, nuovo_stato: str):
        try:
            # W0311: Corretta indentazione
            self.richieste.update_richiesta(id_richiesta, nuovo_stato, Session().current_user["role"])
        # W0707, W0719: Corretto il re-raise dell'eccezione
        except Exception as e:
            logger.error(f"Errore nell'aggiornare la richiesta: {e}", exc_info=True)
            # È meglio sollevare un'eccezione più specifica o la stessa 'e' con 'from e'
            # Per mantenere il comportamento originale, si solleva una nuova Exception
            # ma aggiungendo 'from e' per la catena delle eccezioni.
            raise Exception(f"Errore nell'aggiornare la richiesta: {str(e)}")

    def check_utente(self, tipo_operazione: str) -> bool:
        return tipo_operazione in PERMESSI_OPERAZIONI.get(Session().current_user["role"], [])

    def aggiungi_azione_compensativa(self, descrizione, co2, data):
        try:
            self.compensation_action.inserisci_azione(
                data=data, azienda=Session().current_user["id_azienda"],
                co2_compensata=co2, nome_azione=descrizione
            )
        except Exception as e:
            logger.error(f"Errore {e}", exc_info=True)

    # R1710: Garantito che tutti i percorsi ritornino un valore
    def get_prodotti_standard(self) -> list[ProductStandardModel]:
        try:
            # R1705: Semplificato if/elif/else
            role = Session().current_user["role"]
            if role == "Agricola":
                return self.product.get_prodotti_standard_agricoli()
            if role == "Trasformatore": # Era elif, cambiato in if dopo return
                return self.product.get_prodotti_standard_trasformazione()
            # Se non è nessuno dei due ruoli, solleva un errore come prima o ritorna lista vuota
            # logger.error(f"Utente non autorizzato per prodotti standard: {role}")
            raise TypeError(f"Utente {role} non autorizzato per ottenere prodotti standard")
        except Exception as e:
            logger.error(f"Errore nel ottenimento dei prodotti standard: {e}", exc_info=True)
            return [] # Ritorna lista vuota in caso di errore generico