from off_chain.configuration.log_load_setting import logger
from off_chain.persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from off_chain.persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from off_chain.persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from off_chain.persistence.repository_impl.certification_repository_impl import CertificationRepositoryImpl


class ControllerGuest:
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
        logger.info(
            "BackEnd: Successful initialization of 'class instances' for repository implements")

    def lista_rivenditori(self):
        # repo1 = CompanyRepositoryImpl()
        rivenditori = self.company.get_lista_rivenditori()
        return rivenditori

    # Restituisce la lista di tutte le aziende
    def lista_aziende(self):
        # repo2 = CompanyRepositoryImpl()
        lista_aziende = self.company.get_lista_aziende()
        return lista_aziende

    # Restituisce la lista di tutte le aziende filtrate per tipo
    def lista_aziende_filtro_tipo(self, tipo):
        # repo3 = CompanyRepositoryImpl()
        lista_aziende = self.company.get_lista_aziende_filtrata_tipo(tipo)
        return lista_aziende

    # Restituisce la lista di tutte le aziende filtrate per nome (unica azienda)
    def azienda_by_nome(self, nome):
        # repo4 = CompanyRepositoryImpl()
        azienda = self.company.get_azienda_by_nome(nome)
        return azienda

    # Restituisce la lista di tutte le aziende ordinata per saldo co2
    def lista_aziende_ordinata_co2(self):
        # repo5 = CompanyRepositoryImpl()
        lista_ordinata = self.company.get_lista_aziende_ordinata()
        return lista_ordinata

    # Restituisce la lista di tutti i prodotti finali
    def lista_prodotti(self):
        # repo6 = ProductRepositoryImpl()
        lista_prodotti = self.product.get_lista_prodotti()
        return lista_prodotti

    def is_certificato(self, id_prodotto):

        # return self.certification.is_certificato(id_prodotto)
        try:
            certificazione = self.certification.is_certificato(id_prodotto)
            return certificazione
        except Exception as e:
            logger.error(f"Errore durante il recupero della certificazione per il prodotto {id_prodotto}: {str(e)}")
            return None  # O gestire l'errore in un altro modo, come ritornare un messaggio d'errore

    # Restituisce la lista dei prodotti certificati
    def lista_prodotti_certificati(self):
        # repo8 = ProductRepositoryImpl()
        lista_prodotti_certificati = self.product.get_prodotti_certificati()
        return lista_prodotti_certificati

    def prodotti_by_nome(self, nome):
        # repo9 = ProductRepositoryImpl()
        prodotto = self.product.get_prodotti_by_nome(nome)
        return prodotto

    # Restituisce la lista dei prodotti di un certo rivenditore r

    def lista_prodotti_rivenditore(self, r):
        # repo10 = ProductRepositoryImpl()
        lista_prodotti_by_rivenditore = self.product.get_lista_prodotti_by_rivenditore(r)
        return lista_prodotti_by_rivenditore

    # Restituisce la lista dei prodotti ordinati secondo la co2 consumata
    def lista_prodotti_ordinati_co2(self):
        # repo11 = ProductRepositoryImpl()
        lista_ordinata = self.product.get_prodotti_ordinati_co2()
        return lista_ordinata

    def lista_prodotti_certificati_rivenditore(self, r):
        # repo12 = ProductRepositoryImpl()
        lista = self.product.get_prodotti_certificati_by_rivenditore(r)
        return lista

    def lista_prodotti_certificati_ordinata(self):
        # repo13 = ProductRepositoryImpl()
        lista = self.product.get_prodotti_certificati_ordinati_co2()
        return lista

    def lista_prodotti_certificati_by_nome(self, nome):
        # repo14 = ProductRepositoryImpl()
        lista = self.product.get_prodotti_certificati_by_nome(nome)
        return lista

    # Restituisce la lista delle operazioni per la produzione del prodotto selezionato

    def lista_operazioni_prodotto(self, id_prodotto):
        # repo15 = ProductRepositoryImpl()
        lista_operazioni = self.product.get_storico_prodotto(id_prodotto)
        return lista_operazioni

    def certificazione_by_prodotto(self, id_prodotto):
        # repo16 = CertificationRepositoryImpl()
        try:
            certificazione = self.certification.get_certificazione_by_prodotto(id_prodotto)
            return certificazione
        except Exception as e:
            logger.error(f"Errore durante il recupero della certificazione per il prodotto {id_prodotto}: {str(e)}")
            return None  # O gestire l'errore in un altro modo, come ritornare un messaggio d'errore

    # Restituisce il dettaglio del prodotto selezionato dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_prodotto(self, lista, n):
        # return lista[n]
        pass

    # Restituisce lo scarto dalla soglia di riferimento

    def scarto_soglia(self, co2, operazione, prodotto):
        # repo17 = ThresholdRepositoryImpl()
        soglia = self.threshold.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)
