import datetime
from configuration.log_load_setting import logger
from model.operation_model import OperationModel
from model.threshold_model import ThresholdModel
from model.product_model import ProductModel
from model.materia_prima_model import MateriaPrimaModel
from model.info_product_for_choice_model import ProductForChoiceModel
from session import Session
from persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from persistence.repository_impl.compensation_action_repository_impl import CompensationActionRepositoryImpl
from persistence.repository_impl.operation_repository_impl import OperationRepositoryImpl
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from configuration.log_load_setting import logger
from persistence.repository_impl.composition_repository_impl import CompositionRepositoryImpl
from model.company_model import CompanyModel
from model.operation_estesa_model import OperazioneEstesaModel
from model.compensation_action_model import CompensationActionModel
from persistence.repository_impl.richieste_repository_impl import RichiesteRepositoryImpl
from model.richiesta_model import RichiestaModel


PERMESSI_OPERAZIONI = {
    "Agricola": ["Produzione" ],
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

    def lista_soglie(self, tipo_azienda: str) -> list[ThresholdModel]:
        # repo = ThresholdRepositoryImpl()
        lista_soglie = self.threshold.get_lista_soglie(tipo_azienda=tipo_azienda)
        return lista_soglie

        # Restituisce il dettaglio della soglia selezionata dato l'indice n    def get_dettaglio_soglia(self, n):
        pass

    # Restituisce il dettaglio della co2/il numero di certificati della sua azienda
    def get_dettaglio_azienda(self, id_azienda):
        # repo = CompanyRepositoryImpl()
        return self.company.get_azienda_by_id(id_azienda)

    # Modifica i dati dell sua azienda
    def modifica_dati_azienda(self, azienda):
        pass


    # Restituisce la lista delle sue azioni compensative filtrate per data
    def lista_azioni_per_data(self, azienda, d1, d2):
        # repo = CompensationActionRepositoryImpl()
        lista_azioni_per_data = self.company.get_lista_azioni_per_data(azienda, d1, d2)
        return lista_azioni_per_data

    # Restituisce la lista di tutte le azioni compensative della sua azienda
    def lista_azioni_compensative_ordinata(self, azienda):
        # repo = CompensationActionRepositoryImpl()
        lista_azioni_compensative = self.company.get_lista_azioni_ordinata(azienda)
        return lista_azioni_compensative

    # Restituisce il dettaglio dell'azione compensativa selezionata
    # dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_azione(self, n, lista):
        pass

    # Aggiunge un'azione compensativa
    def aggiungi_azione(self, data, azienda, co2_compensata, nome_azione):


        # repo = CompensationActionRepositoryImpl()
        self.company.inserisci_azione(data, azienda, co2_compensata, nome_azione)


    # Restituisce la lista delle sue operazioni filtrate per data
    def lista_operazioni_per_data(self, azienda, d1, d2):
        # repo = OperationRepositoryImpl()
        lista_operazioni = self.company.get_operazioni_by_data(azienda, d1, d2)
        return lista_operazioni

    def lista_operazioni_ordinata_co2(self, azienda):
        # repo = OperationRepositoryImpl()
        lista_operazioni = self.company.get_operazioni_ordinate_co2(azienda)
        return lista_operazioni

    # Restituisce il dettaglio dell'operazione selezionata dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_operazione(self, n, lista):
        pass

    # Restituisce gli elementi da visualizzare nella combo box

    def elementi_combo_box(self, azienda, operazione, destinatario=''):
        if azienda == "Agricola":
            return self.threshold.get_prodotti_to_azienda_agricola()
        elif azienda == "Trasportatore":
            return self.product.get_prodotti_to_azienda_trasporto(destinatario)
        elif azienda == "Trasformatore":
            return self.product.get_prodotti_to_azienda_trasformazione(operazione)
        elif azienda == "Rivenditore":
            return self.product.get_prodotti_to_rivenditore()

    # Restituisce le opzioni per la combo box del dialog per la composizione
    def get_prodotti_to_composizione(self, id_azienda):
        # repo = CompositionRepositoryImpl()
        #TODO: AGGIUSTARE QUERY
        #lista = self.product.get_prodotti_to_composizione(id_azienda)
        return  [
            ProductModel(1, "Prodotto A", []),
            ProductModel(2, "Prodotto B", []),
            ProductModel(3, "Prodotto C", [])
        ]

    # Restituisce lo scarto dalla soglia di riferimento
    def scarto_soglia(self, co2, operazione, prodotto):
        # repo = ThresholdRepositoryImpl()
        soglia = self.threshold.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)

    def get_emissions(self, company_id: int):
        return self.company.get_company_emission(company_id)

    def newCompany(self, name, address, emissions):
        company = CompanyModel(1, name, address, emissions)
        company.save()



    """ funzioni Mock"""

    
   


    """ Funzioni funzionali """

    def lista_operazioni(self, azienda : int) -> list[OperazioneEstesaModel]:
        # repo = OperationRepositoryImpl()
        try:
            lista_operazioni = self.operation_repository.get_operazioni_by_azienda(azienda)
            return lista_operazioni
        except Exception as e:
            logger.error(f"Error al obtener la lista di operazioni: {e}", exc_info=True)
            return []


    def lista_azioni_compensative(self, azienda : int) -> list[CompensationActionModel]:
        try:
            lista_azioni_compensative = self.compensation_action.get_lista_azioni(azienda)
            return lista_azioni_compensative
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle azioni compensative: {e}", exc_info=True)
            return []
        
    def get_materie_prime_magazzino_azienda(self) -> list[MateriaPrimaModel]:
        try:
            materie_prime = self.product.get_materie_prime_magazzino_azienda(Session().current_user["id_azienda"])
            return materie_prime
        except Exception as e:
            logger.error(f"Errore nell'ottenere la lista delle materie prime: {e}", exc_info=True)
            return  []
        
    def crea_prodotto_trasformato(self,nome : str, quantita :int,quantita_usata_per_materia : dict[MateriaPrimaModel, int]):
        try:
            self.product.inserisci_prodotto_trasformato(nome, quantita, quantita_usata_per_materia, id_azienda=Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore nella creazione del prodotto trasformato: {e}", exc_info=True)
            return None
        

    def salva_operazione_agricola(self, tipo : str, data : datetime,
                                  co2 : float,nome_prodotto : str, quantita : int
                ):
            if not self.check_utente(tipo):
                raise PermissionError("Operazione non consentita per questo utente.")
            
            self.operation_repository.inserisci_operazione_azienda_agricola(
                nome_prodotto, quantita, Session().current_user["id_azienda"], data, co2,
            )

    def salva_operazione_trasporto(self, id_prodotto : int, id_azienda_ricevente: int, id_azienda_richiedente: int,\
                                    quantita : int, co2 : float , id_lotto_input : int,
                ):
            
            self.operation_repository.inserisci_operazione_trasporto(
                Session().current_user["id_azienda"],id_lotto_input, id_prodotto,id_azienda_richiedente, id_azienda_ricevente, quantita, co2
            )

    def get_prodotti_ordinabili(self) -> list[ProductForChoiceModel]:
        try:
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
        
    def invia_richiesta(self,id_az_ricevente: int, id_az_trasporto : int, id_prodotto : int, quantita : int):
        try:
            self.richieste.inserisci_richiesta(Session().current_user["id_azienda"],id_az_ricevente, id_az_trasporto, id_prodotto, quantita)
        except Exception as e:
            logger.error(f"Errore nell'invio della richiesta: {e}", exc_info=True)
        pass
    
    def get_richieste_ricevute(self) -> list[RichiestaModel]:
        try:
            if Session().current_user["role"] == "Trasportatore":
                richieste = self.richieste.get_richieste_ricevute(Session().current_user["id_azienda"], check_trasporto=True)
            else:
                richieste = self.richieste.get_richieste_ricevute(Session().current_user["id_azienda"])
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
        
    def update_richiesta(self, id_richiesta : int, nuovo_stato : str):
        try:
                self.richieste.update_richiesta(id_richiesta, nuovo_stato, Session().current_user["role"])
        except Exception as e:
            logger.error(f"Errore nell'aggiornare la richiesta: {e}", exc_info=True)
            raise Exception(f"Errore nell'aggiornare la richiesta: {e}")
            


    
        
    def check_utente(self, tipo_operazione : str) -> bool:
        return tipo_operazione in PERMESSI_OPERAZIONI.get(Session().current_user["role"], [])
        
