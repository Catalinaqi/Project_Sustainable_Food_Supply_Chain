from configuration.log_load_setting import logger
from persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from persistence.repository_impl.certification_repository_impl import CertificationRepositoryImpl


class ControllerCertificatore:
    """
    As the instance has been created, in the repository implement layer, to access your methods,
    we initialize the instances of the classes 'class instances' with:
            CertificationRepositoryImpl()
            ProductRepositoryImpl()
            ThresholdRepositoryImpl()
            CompanyRepositoryImpl()
    """

    def __init__(self):
        self.certification = CertificationRepositoryImpl()
        self.product = ProductRepositoryImpl()
        self.threshold = ThresholdRepositoryImpl()
        self.company = CompanyRepositoryImpl()
        logger.info("BackEnd: Successful initialization of 'class instances' for repository implements")

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
    def get_dettaglio_azienda(self, id_azienda):
        # repo = CertificationRepositoryImpl()
        return self.certification.get_numero_certificazioni(id_azienda)

    # Restituisce tutte le soglie
    def lista_soglie(self):
        pass

    # Restituisce il dettaglio della soglia selezionata dato l'indice n
    def get_dettaglio_soglia(self, n):
        pass

    def lista_rivenditori(self):
        # repo = CompanyRepositoryImpl()
        rivenditori = self.company.get_lista_rivenditori()
        return rivenditori

    def certificazione_by_prodotto(self, id_prodotto):
        # repo = CertificationRepositoryImpl()
        certificazione = self.certification.get_certificazione_by_prodotto(id_prodotto)
        return certificazione

    def inserisci_certificato(self, id_prodotto, descrizione, id_azienda_certificatore, data):
        # repo = CertificationRepositoryImpl()
        self.certification.inserisci_certificato(id_prodotto, descrizione, id_azienda_certificatore, data)

    # Restituisce la lista di tutti i prodotti finali
    def lista_prodotti(self):
        # repo = ProductRepositoryImpl()
        lista_prodotti = self.product.get_lista_prodotti()
        return lista_prodotti

    def prodotti_by_nome(self, nome):
        # repo = ProductRepositoryImpl()
        prodotto = self.product.get_prodotti_by_nome(nome)
        return prodotto

    # Restituisce la lista dei prodotti di un certo rivenditore r
    def lista_prodotti_rivenditore(self, r):
        # repo = ProductRepositoryImpl()
        lista_prodotti_by_rivenditore = self.product.get_lista_prodotti_by_rivenditore(r)
        return lista_prodotti_by_rivenditore

    # Restituisce la lista dei prodotti ordinati secondo la co2 consumata
    def lista_prodotti_ordinati_co2(self):
        # repo = ProductRepositoryImpl()
        lista_ordinata = self.product.get_prodotti_ordinati_co2()
        return lista_ordinata

    # Restituisce la lista dei prodotti certificati
    def lista_prodotti_certificati(self):
        # repo = ProductRepositoryImpl()
        lista_prodotti_certificati = self.product.get_prodotti_certificati()
        return lista_prodotti_certificati

    def lista_prodotti_certificati_rivenditore(self, r):
        # repo = ProductRepositoryImpl()
        lista = self.product.get_prodotti_certificati_by_rivenditore(r)
        return lista

    def lista_prodotti_certificati_ordinata(self):
        # repo = ProductRepositoryImpl()
        lista = self.product.get_prodotti_certificati_ordinati_co2()
        return lista

    def lista_prodotti_certificati_by_nome(self, nome):
        # repo = ProductRepositoryImpl()
        lista = self.product.get_prodotti_certificati_by_nome(nome)
        return lista

    def is_certificato(self, id_prodotto):
        # repo = CertificationRepositoryImpl()
        return " certificato" """self.product.is_certificato(id_prodotto)"""

    # Restituisce la lista delle operazioni per la produzione del prodotto selezionato
    def lista_operazioni_prodotto(self, id_prodotto):
        # repo = ProductRepositoryImpl()
        lista_operazioni = self.product.get_storico_prodotto(id_prodotto)
        return lista_operazioni

    # Restituisce lo scarto dalla soglia di riferimento
    def scarto_soglia(self, co2, operazione, prodotto):
        # repo = ThresholdRepositoryImpl()
        soglia = self.product.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)
