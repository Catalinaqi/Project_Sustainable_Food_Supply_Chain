from off_chain.persistence.repository_impl.company_repository_impl import CompanyRepositoryImpl
from off_chain.persistence.repository_impl.threshold_repository_impl import ThresholdRepositoryImpl
from off_chain.persistence.repository_impl.product_repository_impl import ProductRepositoryImpl
from off_chain.persistence.repository_impl.certification_repository_impl import CertificationRepositoryImpl


class ControllerGuest:

    @staticmethod
    def lista_rivenditori():
        repo1=CompanyRepositoryImpl()
        rivenditori = repo1.get_lista_rivenditori()
        return rivenditori

    # Restituisce la lista di tutte le aziende
    @staticmethod
    def lista_aziende():
        repo2=CompanyRepositoryImpl()
        lista_aziende = repo2.get_lista_aziende()
        return lista_aziende

    # Restituisce la lista di tutte le aziende filtrate per tipo
    @staticmethod
    def lista_aziende_filtro_tipo(tipo):
        repo3=CompanyRepositoryImpl()
        lista_aziende = repo3.get_lista_aziende_filtrata_tipo(tipo)
        return lista_aziende

    # Restituisce la lista di tutte le aziende filtrate per nome (unica azienda)
    @staticmethod
    def azienda_by_nome(nome):
        repo4=CompanyRepositoryImpl()
        azienda = repo4.get_azienda_by_nome(nome)
        return azienda

    # Restituisce la lista di tutte le aziende ordinata per saldo co2
    @staticmethod
    def lista_aziende_ordinata_co2():
        repo5=CompanyRepositoryImpl()
        lista_ordinata = repo5.get_lista_aziende_ordinata()
        return lista_ordinata

    # Restituisce la lista di tutti i prodotti finali
    @staticmethod
    def lista_prodotti():
        repo6=ProductRepositoryImpl()
        lista_prodotti = repo6.get_lista_prodotti()
        return lista_prodotti

    @staticmethod
    def is_certificato(id_prodotto):
        repo7=CertificationRepositoryImpl()
        return repo7.is_certificato(id_prodotto)

    # Restituisce la lista dei prodotti certificati
    @staticmethod
    def lista_prodotti_certificati():
        repo8=ProductRepositoryImpl()
        lista_prodotti_certificati = repo8.get_prodotti_certificati()
        return lista_prodotti_certificati

    @staticmethod
    def prodotti_by_nome(nome):
        repo9=ProductRepositoryImpl()
        prodotto = repo9.get_prodotti_by_nome(nome)
        return prodotto

    # Restituisce la lista dei prodotti di un certo rivenditore r
    @staticmethod
    def lista_prodotti_rivenditore(r):
        repo10=ProductRepositoryImpl()
        lista_prodotti_by_rivenditore = repo10.get_lista_prodotti_by_rivenditore(r)
        return lista_prodotti_by_rivenditore

    # Restituisce la lista dei prodotti ordinati secondo la co2 consumata
    @staticmethod
    def lista_prodotti_ordinati_co2():
        repo11=ProductRepositoryImpl()
        lista_ordinata = repo11.get_prodotti_ordinati_co2()
        return lista_ordinata

    @staticmethod
    def lista_prodotti_certificati_rivenditore(r):
        repo12=ProductRepositoryImpl()
        lista = repo12.get_prodotti_certificati_by_rivenditore(r)
        return lista

    @staticmethod
    def lista_prodotti_certificati_ordinata():
        repo13=ProductRepositoryImpl()
        lista = repo13.get_prodotti_certificati_ordinati_co2()
        return lista

    @staticmethod
    def lista_prodotti_certificati_by_nome(nome):
        repo14=ProductRepositoryImpl()
        lista = repo14.get_prodotti_certificati_by_nome(nome)
        return lista

    # Restituisce la lista delle operazioni per la produzione del prodotto selezionato
    @staticmethod
    def lista_operazioni_prodotto(id_prodotto):
        repo15=ProductRepositoryImpl()
        lista_operazioni = repo15.get_storico_prodotto(id_prodotto)
        return lista_operazioni

    @staticmethod
    def certificazione_by_prodotto(id_prodotto):
        repo16=CertificationRepositoryImpl()
        certificazione = repo16.get_certificazione_by_prodotto(id_prodotto)
        return certificazione

    # Restituisce il dettaglio del prodotto selezionato dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_prodotto(self, lista, n):
        # return lista[n]
        pass

    # Restituisce lo scarto dalla soglia di riferimento
    @staticmethod
    def scarto_soglia(co2, operazione, prodotto):
        repo17=ThresholdRepositoryImpl()
        soglia = repo17.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)
