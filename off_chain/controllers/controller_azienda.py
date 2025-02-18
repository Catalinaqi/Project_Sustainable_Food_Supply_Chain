from off_chain.database_domenico.db_operations import Database


class ControllerAzienda:
    def __init__(self):
        self.database = Database()

    # Restituisce tutte le soglie
    def lista_soglie(self):
        lista_soglie = self.database.get_lista_soglie()
        return lista_soglie

    # Restituisce il dettaglio della soglia selezionata dato l'indice n
    def get_dettaglio_soglia(self, n):
        pass

    # Restituisce il dettaglio della co2/il numero di certificati della sua azienda
    def get_dettaglio_azienda(self, id_azienda):
        return self.database.get_azienda_by_id(id_azienda)

    # Modifica i dati dell sua azienda
    def modifica_dati_azienda(self, azienda):
        pass

    # Restituisce la lista di tutte le azioni compensative della sua azienda
    def lista_azioni_compensative(self, azienda):
        lista_azioni_compensative = self.database.get_lista_azioni(azienda)
        return lista_azioni_compensative

    # Restituisce la lista delle sue azioni compensative filtrate per data
    def lista_azioni_per_data(self, azienda, d1, d2):
        lista_azioni_per_data = self.database.get_lista_azioni_per_data(azienda, d1, d2)
        return lista_azioni_per_data

    # Restituisce la lista di tutte le azioni compensative della sua azienda
    def lista_azioni_compensative_ordinata(self, azienda):
        lista_azioni_compensative = self.database.get_lista_azioni_ordinata(azienda)
        return lista_azioni_compensative

    # Restituisce il dettaglio dell'azione compensativa selezionata
    # dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_azione(self, n, lista):
        pass

    # Aggiunge un'azione compensativa
    def aggiungi_azione(self, data, azienda, co2_compensata, nome_azione):
        self.database.inserisci_azione(data, azienda, co2_compensata, nome_azione)

    # Restituisce la lista di tutte le operazioni della sua azienda
    def lista_operazioni(self, azienda):
        lista_operazioni = self.database.get_operazioni_by_azienda(azienda)
        return lista_operazioni

    # Restituisce la lista delle sue operazioni filtrate per data
    def lista_operazioni_per_data(self, azienda, d1, d2):
        lista_operazioni = self.database.get_operazioni_by_data(azienda, d1, d2)
        return lista_operazioni

    def lista_operazioni_ordinata_co2(self, azienda):
        lista_operazioni = self.database.get_operazioni_ordinate_co2(azienda)
        return lista_operazioni

    # Restituisce il dettaglio dell'operazione selezionata dato l'indice n e la lista (filtrata o meno)
    def get_dettaglio_operazione(self, n, lista):
        pass

    # Restituisce gli elementi da visualizzare nella combo box
    def elementi_combo_box(self, azienda, operazione, destinatario=''):
        if azienda == "Agricola":
            return self.database.get_prodotti_to_azienda_agricola()
        elif azienda == "Trasportatore":
            return self.database.get_prodotti_to_azienda_trasporto(destinatario)
        elif azienda == "Trasformatore":
            return self.database.get_prodotti_to_azienda_trasformazione(operazione)
        elif azienda == "Rivenditore":
            return self.database.get_prodotti_to_rivenditore()

    # Aggiunge un'operazione
    def aggiungi_operazione(
            self, tipo_azienda, azienda, prodotto, data, co2, evento,
            quantita='', nuovo_stato=00, materie_prime=None
    ):
        if tipo_azienda == "Agricola":
            self.database.inserisci_operazione_azienda_agricola(
                prodotto, quantita, azienda, data, co2, evento
            )
        elif tipo_azienda == "Trasportatore":
            self.database.inserisci_operazione_azienda_trasporto(
                azienda, prodotto, data, co2, evento, nuovo_stato
            )
        elif tipo_azienda == "Trasformatore":
            self.database.inserisci_operazione_azienda_trasformazione(
                azienda, prodotto, data, co2, evento, quantita, materie_prime
            )
        elif tipo_azienda == "Rivenditore":
            self.database.inserisci_operazione_azienda_rivenditore(
                azienda, prodotto, data, co2, evento
            )

    # Restituisce le opzioni per la combo box del dialog per la composizione
    def get_prodotti_to_composizione(self, id_azienda):
        lista = self.database.get_prodotti_to_composizione(id_azienda)
        return lista

    # Restituisce lo scarto dalla soglia di riferimento
    def scarto_soglia(self, co2, operazione, prodotto):
        soglia = self.database.get_soglia_by_operazione_and_prodotto(operazione, prodotto)
        return soglia - float(co2)
