from off_chain.database_domenico.db_operations import Database


class ControllerGuest:
    def __init__(self):
        self.database = Database()

    def lista_rivenditori(self):
        rivenditori = self.database.get_lista_rivenditori()
        return rivenditori

    # Restituisce la lista di tutte le aziende
    def lista_aziende(self):
        lista_aziende = self.database.get_lista_aziende()
        return lista_aziende

    # Restituisce la lista di tutte le aziende filtrate per tipo
    def lista_aziende_filtro_tipo(self, tipo):
        lista_aziende = self.database.get_lista_aziende_filtrata_tipo(tipo)
        return lista_aziende

    # Restituisce la lista di tutte le aziende filtrate per nome (unica azienda)
    def azienda_by_nome(self, nome):
        azienda = self.database.get_azienda_by_nome(nome)
        return azienda

    # Restituisce la lista di tutte le aziende ordinata per saldo co2
    def lista_aziende_ordinata_co2(self):
        lista_ordinata = self.database.get_lista_aziende_ordinata()
        return lista_ordinata

    # Restituisce la lista di tutti i prodotti finali
    def lista_prodotti(self):
        lista_prodotti = self.database.get_lista_prodotti()
        return lista_prodotti

    def is_certificato(self, id_prodotto):
        return self.database.is_certificato(id_prodotto)

    # Restituisce la lista dei prodotti certificati
    def lista_prodotti_certificati(self):
        lista_prodotti_certificati = self.database.get_prodotti_certificati()
        return lista_prodotti_certificati

    def prodotti_by_nome(self, nome):
        prodotto = self.database.get_prodotti_by_nome(nome)
        return prodotto

    # Restituisce la lista dei prodotti di un certo rivenditore r
    def lista_prodotti_rivenditore(self, r):
        lista_prodotti_by_rivenditore = self.database.get_lista_prodotti_by_rivenditore(r)
        return lista_prodotti_by_rivenditore

    # Restituisce la lista dei prodotti ordinati secondo la co2 consumata
    def lista_prodotti_ordinati_co2(self):
        lista_ordinata = self.database.get_prodotti_ordinati_co2()
        return lista_ordinata

    def lista_prodotti_certificati_rivenditore(self, r):
        lista = self.database.get_prodotti_certificati_by_rivenditore(r)
        return lista

    def lista_prodotti_certificati_ordinata(self):
        lista = self.database.get_prodotti_certificati_ordinati_co2()
        return lista

    def lista_prodotti_certificati_by_nome(self, nome):
        lista = self.database.get_prodotti_certificati_by_nome(nome)
        return lista

    # Restituisce la lista delle operazioni per la produzione del prodotto selezionato
    def lista_operazioni_prodotto(self, id_prodotto):
        lista_operazioni = self.database.get_storico_prodotto(id_prodotto)
        return lista_operazioni

    def certificazione_by_prodotto(self, id_prodotto):
        certificazione = self.database.get_certificazione_by_prodotto(id_prodotto)
        return certificazione

    # Restituisce il dettaglio del prodotto selezionato dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_prodotto(self, lista, n):
        # return lista[n]
        pass

    # Restituisce lo scarto dalla soglia di riferimento
    def scarto_soglia(self, co2, operazione, prodotto):
        soglia = self.database.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)
