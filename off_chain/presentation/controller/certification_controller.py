from off_chain.persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from off_chain.persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from off_chain.persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from off_chain.persistence.repository_impl.certification_repository_impl import CertificationRepositoryImpl


class ControllerCertificatore:

    # Restituisce il dettaglio del prodotto selezionato dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_prodotto(self, lista, n):
        pass

    # Assegna un certificato (oppure lo rimuove) al prodotto selezionato di indice n
    def certifica(self, n, azienda, is_certificato=True):
        pass

    # Restituisce la lista di tutte le aziende
    def lista_aziende(self):
        pass

    # Restituisce il dettaglio dell'azienda selezionata dato l'indice n
    #@staticmethod
    def get_dettaglio_azienda(self,id_azienda):
        return CertificationRepositoryImpl.get_numero_certificazioni(id_azienda)

    # Restituisce tutte le soglie
    def lista_soglie(self):
        pass

    # Restituisce il dettaglio della soglia selezionata dato l'indice n
    def get_dettaglio_soglia(self, n):
        pass

    @staticmethod
    def lista_rivenditori():
        rivenditori = CompanyRepositoryImpl.get_lista_rivenditori()
        return rivenditori

    @staticmethod
    def certificazione_by_prodotto(id_prodotto):
        certificazione = CertificationRepositoryImpl.get_certificazione_by_prodotto(id_prodotto)
        return certificazione

    @staticmethod
    def inserisci_certificato(id_prodotto, descrizione, id_azienda_certificatore, data):
        CertificationRepositoryImpl.inserisci_certificato(id_prodotto, descrizione, id_azienda_certificatore, data)

    # Restituisce la lista di tutti i prodotti finali
    @staticmethod
    def lista_prodotti():
        lista_prodotti = ProductRepositoryImpl.get_lista_prodotti()
        return lista_prodotti

    @staticmethod
    def prodotti_by_nome(nome):
        prodotto = ProductRepositoryImpl.get_prodotti_by_nome(nome)
        return prodotto

    # Restituisce la lista dei prodotti di un certo rivenditore r
    @staticmethod
    def lista_prodotti_rivenditore(r):
        repo=ProductRepositoryImpl()
        lista_prodotti_by_rivenditore = repo.get_lista_prodotti_by_rivenditore(r)
        return lista_prodotti_by_rivenditore

    # Restituisce la lista dei prodotti ordinati secondo la co2 consumata
    @staticmethod
    def lista_prodotti_ordinati_co2():
        repo=ProductRepositoryImpl()
        lista_ordinata = repo.get_prodotti_ordinati_co2()
        return lista_ordinata

    # Restituisce la lista dei prodotti certificati
    @staticmethod
    def lista_prodotti_certificati():
        repo=ProductRepositoryImpl()
        lista_prodotti_certificati = repo.get_prodotti_certificati()
        return lista_prodotti_certificati

    @staticmethod
    def lista_prodotti_certificati_rivenditore(r):
        repo=ProductRepositoryImpl()
        lista = repo.get_prodotti_certificati_by_rivenditore(r)
        return lista

    @staticmethod
    def lista_prodotti_certificati_ordinata():
        repo=ProductRepositoryImpl()
        lista = repo.get_prodotti_certificati_ordinati_co2()
        return lista

    @staticmethod
    def lista_prodotti_certificati_by_nome(nome):
        repo=ProductRepositoryImpl()
        lista = repo.get_prodotti_certificati_by_nome(nome)
        return lista

    @staticmethod
    def is_certificato(id_prodotto):
        repo=CertificationRepositoryImpl()
        return repo.is_certificato(id_prodotto)

    # Restituisce la lista delle operazioni per la produzione del prodotto selezionato
    @staticmethod
    def lista_operazioni_prodotto(id_prodotto):
        repo=ProductRepositoryImpl()
        lista_operazioni = repo.get_storico_prodotto(id_prodotto)
        return lista_operazioni

    # Restituisce lo scarto dalla soglia di riferimento
    @staticmethod
    def scarto_soglia(co2, operazione, prodotto):
        repo=ThresholdRepositoryImpl()
        soglia = repo.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)
