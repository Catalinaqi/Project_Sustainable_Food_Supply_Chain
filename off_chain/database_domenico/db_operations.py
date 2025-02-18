import os
import sqlite3


class Database:
    def __init__(self, db_path='database.db'):
        # Percorso assoluto del database nella cartella del progetto
        if db_path is None:
            BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Risale di una cartella
            self.db_path = os.path.join(BASE_DIR, 'database.db')
        else:
            self.db_path = db_path

        # Controlla che il database esista prima di connettersi
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database non trovato: {self.db_path}")

        # Connessione al database esistente
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

    def fetch_query(self, query, params=()):
        """Esegue una SELECT e restituisce i risultati"""
        try:
            self.cur.execute(query, params)
            return self.cur.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Errore SQLite durante la SELECT: {e}")

    def execute_query(self, query, params=()):
        """Esegue una query di modifica (INSERT, UPDATE, DELETE) sul database"""
        try:
            self.cur.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Errore SQLite durante l'esecuzione della query: {e}")

    def co2_consumata_prodotti(self, prodotti):
        lista_con_co2 = []
        for prodotto in prodotti:
            storico = self.get_storico_prodotto(prodotto[0])
            totale_co2 = sum(t[4] for t in storico)
            lista_con_co2.append((prodotto, totale_co2))
        return lista_con_co2

    # Restituisce la lista di prodotti sugli scaffali per il guest
    def get_lista_prodotti(self):
        query = """
        SELECT
            Prodotto.Id_prodotto,
            Prodotto.Nome,
            Prodotto.Quantita,
            Prodotto.Stato,
            Azienda.Nome
        FROM Operazione
        JOIN Azienda ON Operazione.Id_azienda = Azienda.Id_azienda
        JOIN Prodotto ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Operazione = "Messo sugli scaffali";
        """
        return self.co2_consumata_prodotti(self.fetch_query(query))

    # Restituisce tutti i prodotti sugli scaffali ordinati per co2 consumata
    def get_prodotti_ordinati_co2(self):
        return sorted(self.get_lista_prodotti(), key=lambda x: x[1])

    # Restituisce tutti i prodotti sugli scaffali con un certo nome
    def get_prodotti_by_nome(self, nome):
        query = """
                SELECT
                    Prodotto.Id_prodotto,
                    Prodotto.Nome,
                    Prodotto.Quantita,
                    Prodotto.Stato,
                    Azienda.Nome
                FROM Operazione
                JOIN Azienda ON Operazione.Id_azienda = Azienda.Id_azienda
                JOIN Prodotto ON Operazione.Id_prodotto = Prodotto.Id_prodotto
                WHERE Operazione.Operazione = "Messo sugli scaffali"
                AND Prodotto.Nome = ?;
                """
        return self.co2_consumata_prodotti(self.fetch_query(query, (nome, )))

    # Restituisce una lista di prodotti sullo scaffale filtrati per rivenditore
    def get_lista_prodotti_by_rivenditore(self, rivenditore):
        query = """
        SELECT
            Prodotto.Id_prodotto,
            Prodotto.Nome,
            Prodotto.Quantita,
            Prodotto.Stato,
            Azienda.Nome
        FROM Operazione
        JOIN Azienda ON Operazione.Id_azienda = Azienda.Id_azienda
        JOIN Prodotto ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Operazione = "Messo sugli scaffali"
        AND Operazione.Id_azienda = ?;
        """
        return self.co2_consumata_prodotti(self.fetch_query(query, (rivenditore,)))

    # Restituisce la lista di tutti i prodotti sullo scaffale certificati
    def get_prodotti_certificati(self):
        query = """
        SELECT
            Prodotto.Id_prodotto,
            Prodotto.Nome,
            Prodotto.Quantita,
            Prodotto.Stato,
            Azienda.Nome
        FROM Operazione
        JOIN Azienda ON Operazione.Id_azienda = Azienda.Id_azienda
        JOIN Prodotto ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Operazione = "Messo sugli scaffali"
        AND Operazione.Id_prodotto IN (
            SELECT Id_prodotto FROM Certificato
        );
        """
        return self.co2_consumata_prodotti(self.fetch_query(query))

    # Restituisce i prodotti certificati sullo scaffale filtrati per rivenditore
    def get_prodotti_certificati_by_rivenditore(self, id_rivenditore):
        query = """
        SELECT
            Prodotto.Id_prodotto,
            Prodotto.Nome,
            Prodotto.Quantita,
            Prodotto.Stato,
            Azienda.Nome
        FROM Operazione
        JOIN Azienda ON Operazione.Id_azienda = Azienda.Id_azienda
        JOIN Prodotto ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Operazione = "Messo sugli scaffali"
        AND Operazione.Id_prodotto IN (
            SELECT Id_prodotto FROM Certificato
        )
        AND Operazione.Id_azienda = ?;
        """
        return self.co2_consumata_prodotti(self.fetch_query(query, (id_rivenditore, )))

    # Restituisce i prodotti certificati sullo scaffale ordinati per co2 consumata
    def get_prodotti_certificati_ordinati_co2(self):
        return sorted(self.get_prodotti_certificati(), key=lambda x: x[1])

    # Restituisce i prodotti certificati sullo scaffale filtrati per nome
    def get_prodotti_certificati_by_nome(self, nome):
        query = """
        SELECT
            Prodotto.Id_prodotto,
            Prodotto.Nome,
            Prodotto.Quantita,
            Prodotto.Stato,
            Azienda.Nome
        FROM Operazione
        JOIN Azienda ON Operazione.Id_azienda = Azienda.Id_azienda
        JOIN Prodotto ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Operazione = "Messo sugli scaffali"
        AND Operazione.Id_prodotto IN (
            SELECT Id_prodotto FROM Certificato
        )
        AND Prodotto.Nome = ?;
        """
        return self.co2_consumata_prodotti(self.fetch_query(query, (nome, )))

    # Restituisce lo storico del prodotto selezionato
    def get_storico_prodotto(self, prodotto):
        query = """
        SELECT
            Operazione.Id_operazione,
            Azienda.Nome,
            Prodotto.Nome,
            Operazione.Data_operazione,
            Operazione.Consumo_CO2,
            Operazione.Operazione
        FROM Operazione
        JOIN Azienda ON Operazione.Id_azienda = Azienda.Id_azienda
        JOIN Prodotto ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Id_prodotto IN (
            SELECT Materia_prima
            FROM Composizione
            WHERE Prodotto = ?
        );
        """
        return self.fetch_query(query, (prodotto,))

    # Restituisce la certificazione del prodotto selezionato
    def get_certificazione_by_prodotto(self, prodotto):
        query = """
        SELECT 
            Certificato.Id_certificato,
            Prodotto.Nome,
            Certificato.Descrizione,
            Azienda.Nome,
            Certificato.Data
        FROM Certificato
        JOIN Azienda ON Certificato.Id_azienda_certificatore = Azienda.Id_azienda
        JOIN Prodotto ON Certificato.Id_prodotto = Prodotto.Id_prodotto
        WHERE Certificato.Id_prodotto = ?;
        """
        return self.fetch_query(query, (prodotto,))

    # Restituisce la lista dei rivenditori
    def get_lista_rivenditori(self):
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome FROM Azienda WHERE Tipo = "Rivenditore"
        """
        return self.fetch_query(query)

    # Restituisce la lista di tutte le aziende con i rispettivi valori di CO2 consumata e compensata
    def get_lista_aziende(self):
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome FROM Azienda WHERE Tipo != "Certificatore"
        """
        aziende = self.fetch_query(query)
        lista_con_co2 = []
        for azienda in aziende:
            query_co2_consumata = """
            SELECT SUM(Consumo_CO2) FROM Operazione WHERE Id_azienda = ?;
            """
            query_co2_compensata = """
            SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
            """
            if not self.fetch_query(query_co2_consumata, (azienda[0],))[0][0]:
                co2_consumata = 0
            else:
                co2_consumata = self.fetch_query(query_co2_consumata, (azienda[0],))[0][0]
            if not self.fetch_query(query_co2_compensata, (azienda[0],))[0][0]:
                co2_compensata = 0
            else:
                co2_compensata = self.fetch_query(query_co2_compensata, (azienda[0],))[0][0]
            lista_con_co2.append((azienda, co2_consumata, co2_compensata))
        return lista_con_co2

    # Restituisce la lista ordinata per saldo CO2 di tutte le aziende
    def get_lista_aziende_ordinata(self):
        lista_ordinata = sorted(self.get_lista_aziende(), key=lambda x: (x[2] or 0) - (x[1] or 0), reverse=True)
        return lista_ordinata

    # Restituisce la lista di tutte le aziende con i rispettivi valori di CO2 consumata e compensata
    # filtrata per tipo
    def get_lista_aziende_filtrata_tipo(self, tipo):
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome FROM Azienda WHERE Tipo != "Certificatore"
        AND Tipo = ?
        """
        aziende = self.fetch_query(query, (tipo,))
        lista_con_co2 = []
        for azienda in aziende:
            query_co2_consumata = """
            SELECT SUM(Consumo_CO2) FROM Operazione WHERE Id_azienda = ?;
            """
            query_co2_compensata = """
            SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
            """
            if not self.fetch_query(query_co2_consumata, (azienda[0],))[0][0]:
                co2_consumata = 0
            else:
                co2_consumata = self.fetch_query(query_co2_consumata, (azienda[0],))[0][0]
            if not self.fetch_query(query_co2_compensata, (azienda[0],))[0][0]:
                co2_compensata = 0
            else:
                co2_compensata = self.fetch_query(query_co2_compensata, (azienda[0],))[0][0]
            lista_con_co2.append((azienda, co2_consumata, co2_compensata))
        return lista_con_co2

    # Restituisce la lista di tutte le aziende con i rispettivi valori di CO2 consumata e compensata
    # filtrata per nome
    def get_azienda_by_nome(self, nome):
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome FROM Azienda WHERE Tipo != "Certificatore"
        AND Nome = ?
        """
        aziende = self.fetch_query(query, (nome,))
        lista_con_co2 = []
        for azienda in aziende:
            query_co2_consumata = """
            SELECT SUM(Consumo_CO2) FROM Operazione WHERE Id_azienda = ?;
            """
            query_co2_compensata = """
            SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
            """
            if not self.fetch_query(query_co2_consumata, (azienda[0],))[0][0]:
                co2_consumata = 0
            else:
                co2_consumata = self.fetch_query(query_co2_consumata, (azienda[0],))[0][0]
            if not self.fetch_query(query_co2_compensata, (azienda[0],))[0][0]:
                co2_compensata = 0
            else:
                co2_compensata = self.fetch_query(query_co2_compensata, (azienda[0],))[0][0]
            lista_con_co2.append((azienda, co2_consumata, co2_compensata))
        return lista_con_co2

    def get_azienda_by_id(self, id_):
        query = """
        SELECT Id_azienda, Tipo, Indirizzo, Nome FROM Azienda WHERE Id_azienda = ?;
        """
        aziende = self.fetch_query(query, (id_,))
        lista_con_co2 = []
        for azienda in aziende:
            query_co2_consumata = """
            SELECT SUM(Consumo_CO2) FROM Operazione WHERE Id_azienda = ?;
            """
            query_co2_compensata = """
            SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
            """
            if not self.fetch_query(query_co2_consumata, (azienda[0],))[0][0]:
                co2_consumata = 0
            else:
                co2_consumata = self.fetch_query(query_co2_consumata, (azienda[0],))[0][0]
            if not self.fetch_query(query_co2_compensata, (azienda[0],))[0][0]:
                co2_compensata = 0
            else:
                co2_compensata = self.fetch_query(query_co2_compensata, (azienda[0],))[0][0]
            lista_con_co2.append((azienda, co2_consumata, co2_compensata))
        return lista_con_co2

    def get_azienda(self, n):
        return self.get_lista_aziende()[n]

    # Restituisce il numero di certificazioni di un'azienda
    def get_numero_certificazioni(self, id_azienda):
        query = """
        SELECT COUNT(*) FROM Certificato WHERE Id_azienda_certificatore = ?;
        """
        return self.fetch_query(query, (id_azienda,))[0]

    # Restituisce true se il prodotto è certificato, false altrimenti
    def is_certificato(self, id_prodotto):
        query = """
        SELECT * FROM Certificato WHERE Id_prodotto = ?;
        """
        if not self.fetch_query(query, (id_prodotto,)):
            return False
        return True

    # Inserisce un nuovo certificato
    def inserisci_certificato(self, prodotto, tipo, azienda, data):
        query = """
        INSERT INTO Certificato (Id_prodotto, Descrizione, Id_azienda_certificatore, Data)
        VALUES (?, ?, ?, ?);
        """
        self.execute_query(query, (prodotto, tipo, azienda, data))

    # Restituisce la lista delle azioni compensative per azienda
    def get_lista_azioni(self, id_azienda):
        query = """
        SELECT * FROM Azioni_compensative WHERE Id_azienda = ?;
        """
        return self.fetch_query(query, (id_azienda,))

    # Restituisce la lista di azioni compensative filtrate per data
    def get_lista_azioni_per_data(self, id_azienda, d1, d2):
        query = """
        SELECT * FROM Azioni_compensative
        WHERE Id_azienda = ? AND Data BETWEEN ? AND ?;
        """
        return self.fetch_query(query, (id_azienda, d1, d2))

    # Restituisce la lista di azioni compensative ordinata per co2 risparmiata
    def get_lista_azioni_ordinata(self, id_azienda):
        query = """
        SELECT * FROM Azioni_compensative
        WHERE Id_azienda = ?
        ORDER BY Co2_compensata DESC;
        """
        return self.fetch_query(query, (id_azienda,))

    # Restituisce il valore della co2 compensata per azienda
    def get_co2_compensata(self, id_azienda):
        query = """
        SELECT SUM(Co2_compensata) FROM Azioni_compensative WHERE Id_azienda = ?;
        """
        return self.fetch_query(query, (id_azienda,))[0][0]

    # Inserisce una nuova azione compensativa
    def inserisci_azione(self, data, azienda, co2_compensata, nome_azione):
        query = """
        INSERT INTO Azioni_compensative (Data, Id_azienda, Co2_compensata, Nome_azione)
        VALUES (?, ?, ?, ?);
        """
        self.execute_query(query, (data, azienda, co2_compensata, nome_azione))

    # Restituisce la lista di tutte le soglie
    def get_lista_soglie(self):
        query = """
        SELECT * FROM Soglie;
        """
        return self.fetch_query(query)

    # Le seguenti quattro funzioni restituiscono gli elementi che verranno visualizzati nelle
    # rispettive combo box, a seconda del tipo di azienda che sta effettuando l'operazione
    def get_prodotti_to_azienda_agricola(self):
        query = """
        SELECT DISTINCT Prodotto FROM Soglie WHERE Tipo = "materia prima";
        """
        lista_finale = []
        for i in self.fetch_query(query):
            lista_finale.append(i[0])
        return lista_finale

    def get_prodotti_to_azienda_trasporto(self, destinatario):
        query_to_trasformazione = """
        SELECT Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita
        FROM Prodotto
        WHERE Prodotto.Stato = 00 OR Prodotto.Stato = 10
        AND Prodotto.Nome IN (
            SELECT Tipo
            FROM Soglie
            WHERE Tipo = "materia prima"
        );
        """
        query_to_rivenditore = """
        SELECT Id_prodotto, Nome, Quantita 
        FROM Prodotto
        WHERE Prodotto.Stato = 00 OR Prodotto.Stato = 10;
        """
        if destinatario == "Azienda di trasformazione":
            return self.fetch_query(query_to_trasformazione)
        return self.fetch_query(query_to_rivenditore)

    def get_prodotti_to_azienda_trasformazione(self, operazione):
        if operazione == "Trasformazione":
            query = """
            SELECT Id_prodotto, Nome, Quantita FROM Prodotto WHERE Stato = 01;
            """
        else:
            query = """
            SELECT DISTINCT Prodotto FROM Soglie WHERE Tipo = "prodotto finale"
            """
            lista_finale = []
            for i in self.fetch_query(query):
                lista_finale.append(i[0])
            return lista_finale
        return self.fetch_query(query)

    def get_prodotti_to_rivenditore(self):
        query = """
        SELECT Id_prodotto, Nome, Quantita FROM Prodotto WHERE Stato = 11;
        """
        return self.fetch_query(query)

    # Questa funzione restituisce i prodotti che l'azienda di trasformazione
    # può inserire nella tabella "composizione" come valori dell'attributo "materia prima"
    def get_materie_prime(self, azienda):
        query = """
        SELECT Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita
        FROM Prodotto
        JOIN Operazione
        ON Prodotto.Id_prodotto = Operazione.Id_prodotto
        WHERE Operazione.Operazione = "Trasformazione"
        AND Operazione.Id_azienda = ?
        ORDER BY Operazione.Data_operazione DESC;
        """
        return self.fetch_query(query, (azienda,))

    # Le seguenti quattro funzioni permettono l'inserimento di un'operazione
    # a seconda del tipo di azienda che la sta effettuando
    def inserisci_operazione_azienda_agricola(self, nome, quantita, azienda, data, co2, evento):
        try:
            self.cur.execute("BEGIN TRANSACTION;")  # Inizio transazione

            # Inserisci il prodotto
            query_prodotto = """
            INSERT INTO Prodotto (Nome, Quantita, Stato) VALUES (?, ?, ?);
            """
            self.cur.execute(query_prodotto, (nome, quantita, 0))

            prodotto_id = self.cur.lastrowid  # Ottieni l'ID del prodotto inserito

            # Inserisci l'operazione
            query_operazione = """
            INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione) VALUES (?, ?, ?, ?, ?);
            """
            self.cur.execute(query_operazione, (azienda, prodotto_id, data, co2, evento))

            self.conn.commit()  # Conferma la transazione

        except sqlite3.Error as e:
            self.conn.rollback()  # Annulla tutto se c'è un errore
            raise Exception(f"Errore durante l'inserimento: {str(e)}")  # Lancia un'eccezione

    def inserisci_operazione_azienda_trasporto(self, azienda, prodotto, data, co2, evento, nuovo_stato):
        try:
            self.cur.execute("BEGIN TRANSACTION;")  # Inizio transazione

            # Inserisci l'operazione
            query_operazione = """
            INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
            VALUES (?, ?, ?, ?, ?);
            """
            self.cur.execute(query_operazione, (azienda, prodotto, data, co2, evento))

            # Modifica lo stato del prodotto
            query_prodotto = """
            UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;
            """
            self.cur.execute(query_prodotto, (nuovo_stato, prodotto))

            if nuovo_stato == 11:  # Cioè se il destinatario è il rivenditore
                query_composizione = """
                INSERT OR IGNORE INTO Composizione VALUES(?, ?)
                """
                self.cur.execute(query_composizione, (prodotto, prodotto))

            self.conn.commit()  # Conferma la transazione

        except sqlite3.Error as e:
            self.conn.rollback()  # Annulla tutto se c'è un errore
            raise Exception(f"Errore durante l'inserimento: {str(e)}")  # Lancia un'eccezione

    def inserisci_operazione_azienda_trasformazione(self, azienda, prodotto, data, co2, evento, quantita=0,
                                                    materie_prime=None):
        if materie_prime is None:
            materie_prime = []
        if evento == "Trasformazione":
            # In questo caso, il parametro prodotto è l'id del prodotto che seleziono
            try:
                self.cur.execute("BEGIN TRANSACTION;")  # Inizio transazione

                # Inserisci l'operazione
                query = """
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
                VALUES (?, ?, ?, ?, ?);
                """
                self.cur.execute(query, (azienda, prodotto[0], data, co2, evento))

                # Modifica lo stato del prodotto
                query_prodotto = """
                UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;
                """
                self.cur.execute(query_prodotto, (101, prodotto[0]))

                self.conn.commit()  # Conferma la transazione

            except sqlite3.Error as e:
                self.conn.rollback()  # Annulla tutto se c'è un errore
                raise Exception(f"Errore durante l'inserimento: {str(e)}")  # Lancia un'eccezione

        else:
            # In quest'altro caso, invece, il parametro prodotto è il nome del prodotto che seleziono.
            # Questo perché devo creare una nuova istanza di prodotto e mi serve il nome
            # (l'id nella tabella prodotto è autoincrement).
            try:
                self.cur.execute("BEGIN TRANSACTION;")  # Inizio transazione

                # Inserisci il prodotto
                query_prodotto = """
                INSERT INTO Prodotto (Nome, Quantita, Stato) VALUES (?, ?, ?);
                """
                self.cur.execute(query_prodotto, (prodotto, quantita, 10))

                prodotto_id = self.cur.lastrowid  # Ottieni l'ID del prodotto inserito

                # Inserisci l'operazione
                query_operazione = """
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
                VALUES (?, ?, ?, ?, ?);
                """
                self.cur.execute(query_operazione, (azienda, prodotto_id, data, co2, evento))

                # Inserisci la composizione
                query_composizione = """
                INSERT INTO Composizione VALUES(?, ?)
                """
                # Modifica lo stato del prodotto
                query_stato = """
                UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;
                """
                self.cur.execute(query_composizione, (prodotto_id, prodotto_id))
                for mp in materie_prime:
                    self.cur.execute(query_composizione, (prodotto_id, mp))
                    self.cur.execute(query_stato, (110, mp))

                self.conn.commit()  # Conferma la transazione

            except sqlite3.Error as e:
                self.conn.rollback()  # Annulla tutto se c'è un errore
                raise Exception(f"Errore durante l'inserimento: {str(e)}")  # Lancia un'eccezione

    def inserisci_operazione_azienda_rivenditore(self, azienda, prodotto, data, co2, evento):
        try:
            self.cur.execute("BEGIN TRANSACTION;")  # Inizio transazione

            # Inserisci l'operazione
            query_operazione = """
            INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
            VALUES (?, ?, ?, ?, ?);
            """
            self.cur.execute(query_operazione, (azienda, prodotto, data, co2, evento))

            # Modifica lo stato del prodotto
            query_prodotto = """
            UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;
            """
            self.cur.execute(query_prodotto, (111, prodotto))

            self.conn.commit()  # Conferma la transazione

        except sqlite3.Error as e:
            self.conn.rollback()  # Annulla tutto se c'è un errore
            raise Exception(f"Errore durante l'inserimento: {str(e)}")  # Lancia un'eccezione

    # Questa funzione restituisce la soglia data l'operazione e il prodotto
    def get_soglia_by_operazione_and_prodotto(self, operazione, prodotto):
        query = """
        SELECT Soglia_Massima FROM Soglie WHERE Operazione = ? AND Prodotto = ?;
        """
        if not self.fetch_query(query, (operazione, prodotto)):
            print('non ce')
            return 999
        return self.fetch_query(query, (operazione, prodotto))[0][0]

    # Restituisce la lista di tutte le operazioni effettuate da una certa azienda
    def get_operazioni_by_azienda(self, azienda):
        query = """
        SELECT Operazione.Id_operazione, Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita, 
        Operazione.Data_operazione, Operazione.Consumo_CO2, Operazione.Operazione
        FROM Operazione JOIN Prodotto
        ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Id_azienda = ?;
        """
        return self.fetch_query(query, (azienda,))

    # Restituisce la lista di tutte le operazioni effettuate da una certa azienda filtrate per data
    def get_operazioni_by_data(self, azienda, d1, d2):
        query = """
        SELECT Operazione.Id_operazione, Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita, Operazione.Data_operazione, Operazione.Consumo_CO2, Operazione.Operazione
        FROM Operazione JOIN Prodotto
        ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Id_azienda = ?
        AND Operazione.Data_operazione BETWEEN ? AND ?;
        """
        return self.fetch_query(query, (azienda, d1, d2))

    # Restituisce la lista di tutte le operazioni effettuate da una certa azienda ordinate per co2 consumata
    def get_operazioni_ordinate_co2(self, azienda):
        query = """
        SELECT Operazione.Id_operazione, Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita, Operazione.Data_operazione, Operazione.Consumo_CO2, Operazione.Operazione
        FROM Operazione JOIN Prodotto
        ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Id_azienda = ?
        ORDER BY Operazione.Consumo_CO2 ASC;
        """
        return self.fetch_query(query, (azienda,))

    # Restituisce i prodotti con cui un trasformatore può fare la composizione
    def get_prodotti_to_composizione(self, azienda):
        query = """
        SELECT Id_prodotto, Nome, Quantita
        FROM Prodotto
        WHERE Stato != 110
        AND Id_prodotto IN (
            SELECT Id_prodotto
            FROM Operazione
            WHERE Id_azienda = ? AND Operazione = "Trasformazione"
        )
        """
        return self.fetch_query(query, (azienda,))

    def close(self):
        self.conn.close()
