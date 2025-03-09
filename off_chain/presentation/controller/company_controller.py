from off_chain.persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from off_chain.persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from off_chain.persistence.repository_impl.compensation_action_repository_impl import CompensationActionRepositoryImpl
from off_chain.persistence.repository_impl.operation_repository_impl import OperationRepositoryImpl
from off_chain.persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from off_chain.persistence.repository_impl.composition_repository_impl import CompositionRepositoryImpl
from off_chain.model.company_model import CompanyModel


class ControllerAzienda:

    # Restituisce tutte le soglie
    @staticmethod
    def lista_soglie():
        repo=ThresholdRepositoryImpl()
        lista_soglie = repo.get_lista_soglie()
        return lista_soglie

    # Restituisce il dettaglio della soglia selezionata dato l'indice n
    def get_dettaglio_soglia(self, n):
        pass

    # Restituisce il dettaglio della co2/il numero di certificati della sua azienda
    @staticmethod
    def get_dettaglio_azienda(id_azienda):
        repo=CompanyRepositoryImpl()
        return repo.get_azienda_by_id(id_azienda)

    # Modifica i dati dell sua azienda
    def modifica_dati_azienda(self, azienda):
        pass

    # Restituisce la lista di tutte le azioni compensative della sua azienda
    @staticmethod
    def lista_azioni_compensative(azienda):
        repo=CompensationActionRepositoryImpl()
        lista_azioni_compensative = repo.get_lista_azioni(azienda)
        return lista_azioni_compensative

    # Restituisce la lista delle sue azioni compensative filtrate per data
    @staticmethod
    def lista_azioni_per_data(azienda, d1, d2):
        repo=CompensationActionRepositoryImpl()
        lista_azioni_per_data = repo.get_lista_azioni_per_data(azienda, d1, d2)
        return lista_azioni_per_data

    # Restituisce la lista di tutte le azioni compensative della sua azienda
    @staticmethod
    def lista_azioni_compensative_ordinata(azienda):
        repo=CompensationActionRepositoryImpl()
        lista_azioni_compensative = repo.get_lista_azioni_ordinata(azienda)
        return lista_azioni_compensative

    # Restituisce il dettaglio dell'azione compensativa selezionata
    # dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_azione(self, n, lista):
        pass

    # Aggiunge un'azione compensativa
    @staticmethod
    def aggiungi_azione(data, azienda, co2_compensata, nome_azione):
        repo=CompensationActionRepositoryImpl()
        repo.inserisci_azione(data, azienda, co2_compensata, nome_azione)

    # Restituisce la lista di tutte le operazioni della sua azienda
    @staticmethod
    def lista_operazioni(azienda):
        repo=OperationRepositoryImpl()
        lista_operazioni = repo.get_operazioni_by_azienda(azienda)
        return lista_operazioni

    # Restituisce la lista delle sue operazioni filtrate per data
    @staticmethod
    def lista_operazioni_per_data(azienda, d1, d2):
        repo=OperationRepositoryImpl()
        lista_operazioni = repo.get_operazioni_by_data(azienda, d1, d2)
        return lista_operazioni

    @staticmethod
    def lista_operazioni_ordinata_co2(azienda):
        repo=OperationRepositoryImpl()
        lista_operazioni = repo.get_operazioni_ordinate_co2(azienda)
        return lista_operazioni

    # Restituisce il dettaglio dell'operazione selezionata dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_operazione(self, n, lista):
        pass

    # Restituisce gli elementi da visualizzare nella combo box
    @staticmethod
    def elementi_combo_box(azienda, operazione, destinatario=''):
        repo = ThresholdRepositoryImpl()
        repop = ProductRepositoryImpl()
        if azienda == "Agricola":
            return repo.get_prodotti_to_azienda_agricola()
        elif azienda == "Trasportatore":
            return repo.get_prodotti_to_azienda_trasporto(destinatario)
        elif azienda == "Trasformatore":
            return repo.get_prodotti_to_azienda_trasformazione(operazione)
        elif azienda == "Rivenditore":
            return repop.get_prodotti_to_rivenditore()

    # Aggiunge un'operazione
    @staticmethod
    def aggiungi_operazione(
            tipo_azienda, azienda, prodotto, data, co2, evento,
            quantita='', nuovo_stato=00, materie_prime=None
    ):
        repo = OperationRepositoryImpl()
        if tipo_azienda == "Agricola":
            repo.inserisci_operazione_azienda_agricola(
                prodotto, quantita, azienda, data, co2, evento
            )
        elif tipo_azienda == "Trasportatore":
            repo.inserisci_operazione_azienda_trasporto(
                azienda, prodotto, data, co2, evento, nuovo_stato
            )
        elif tipo_azienda == "Trasformatore":
            repo.inserisci_operazione_azienda_trasformazione(
                azienda, prodotto, data, co2, evento, quantita, materie_prime
            )
        elif tipo_azienda == "Rivenditore":
            repo.inserisci_operazione_azienda_rivenditore(
                azienda, prodotto, data, co2, evento
            )

    # Restituisce le opzioni per la combo box del dialog per la composizione
    @staticmethod
    def get_prodotti_to_composizione(id_azienda):
        repo = CompositionRepositoryImpl()
        lista = repo.get_prodotti_to_composizione(id_azienda)
        return lista

    # Restituisce lo scarto dalla soglia di riferimento
    @staticmethod
    def scarto_soglia(co2, operazione, prodotto):
        repo = ThresholdRepositoryImpl()
        soglia = repo.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)

    def get_emissions(self, company_id: int):
        return CompanyModel.get_company_emission(company_id)

    @staticmethod
    def newCompany(name, address, emissions):
        company = CompanyModel(1, name, address, emissions)
        company.save()
