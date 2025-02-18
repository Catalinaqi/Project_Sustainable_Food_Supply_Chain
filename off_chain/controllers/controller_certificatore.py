from off_chain.database_domenico.db_operations import Database


class ControllerCertificatore:
    def __init__(self):
        self.database = Database()

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
        return self.database.get_numero_certificazioni(id_azienda)

    # Restituisce tutte le soglie
    def lista_soglie(self):
        pass

    # Restituisce il dettaglio della soglia selezionata dato l'indice n
    def get_dettaglio_soglia(self, n):
        pass

    def lista_rivenditori(self):
        rivenditori = self.database.get_lista_rivenditori()
        return rivenditori

    def certificazione_by_prodotto(self, id_prodotto):
        certificazione = self.database.get_certificazione_by_prodotto(id_prodotto)
        return certificazione

    def inserisci_certificato(self, id_prodotto, descrizione, id_azienda_certificatore, data):
        self.database.inserisci_certificato(id_prodotto, descrizione, id_azienda_certificatore, data)

    # Restituisce la lista di tutti i prodotti finali
    def lista_prodotti(self):
        lista_prodotti = self.database.get_lista_prodotti()
        return lista_prodotti

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

    # Restituisce la lista dei prodotti certificati
    def lista_prodotti_certificati(self):
        lista_prodotti_certificati = self.database.get_prodotti_certificati()
        return lista_prodotti_certificati

    def lista_prodotti_certificati_rivenditore(self, r):
        lista = self.database.get_prodotti_certificati_by_rivenditore(r)
        return lista

    def lista_prodotti_certificati_ordinata(self):
        lista = self.database.get_prodotti_certificati_ordinati_co2()
        return lista

    def lista_prodotti_certificati_by_nome(self, nome):
        lista = self.database.get_prodotti_certificati_by_nome(nome)
        return lista

    def is_certificato(self, id_prodotto):
        return self.database.is_certificato(id_prodotto)

    # Restituisce la lista delle operazioni per la produzione del prodotto selezionato
    def lista_operazioni_prodotto(self, id_prodotto):
        lista_operazioni = self.database.get_storico_prodotto(id_prodotto)
        return lista_operazioni

    # Restituisce lo scarto dalla soglia di riferimento
    def scarto_soglia(self, co2, operazione, prodotto):
        soglia = self.database.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)
