from configuration.log_load_setting import logger
from configuration.database import Database
from configuration.db_manager_setting import DatabaseManagerSetting


class DatabaseMigrations:



    # Variable of the class to track if the migrations were executed
    _migrations_executed = False

    
    @staticmethod
    def run_migrations():

        TABLE_DELETION_QUERIES = [
            'DROP TABLE IF EXISTS Richiesta',
            'DROP TABLE IF EXISTS Magazzino',
            'DROP TABLE IF EXISTS Azioni_compensative',
            'DROP TABLE IF EXISTS Certificato',
            'DROP TABLE IF EXISTS Operazione',
            'DROP TABLE IF EXISTS Prodotto',
            'DROP TABLE IF EXISTS Azienda',
            'DROP TABLE IF EXISTS Soglie',
            'DROP TABLE IF EXISTS Credenziali',
            'DROP TABLE IF EXISTS ComposizioneLotto',
        ]
        
        TABLE_CREATION_QUERIES = [
            '''
            CREATE TABLE  Credenziali (
                Id_credenziali INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL,
                topt_secret TEXT NOT NULL
            )
            ''',
            '''
            CREATE TABLE  Soglie (
                Operazione TEXT NOT NULL,
                Prodotto TEXT NOT NULL,
                Soglia_Massima REAL NOT NULL,
                Tipo TEXT NOT NULL,
                PRIMARY KEY (Operazione, Prodotto)
            )
            ''',
            '''
            CREATE TABLE  Azienda (
                Id_azienda INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_credenziali INTEGER NOT NULL,
                Tipo TEXT CHECK(Tipo IN ('Agricola', 'Trasportatore', 'Trasformatore', 'Rivenditore', 'Certificatore')),
                Nome TEXT NOT NULL,
                Indirizzo TEXT NOT NULL,
                Co2_emessa REAL NOT NULL,
                Co2_compensata REAL NOT NULL,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_credenziali) REFERENCES Credenziali(Id_credenziali) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE  Prodotto (
                Id_prodotto INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome TEXT NOT NULL,
                Stato INTEGER,
                Data_di_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE  Operazione (
                Id_operazione INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_azienda INTEGER NOT NULL,
                Id_prodotto INTEGER NOT NULL,
                Id_lotto INTEGER UNIQUE NOT NULL,
                Data_operazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Consumo_CO2 REAL NOT NULL,
                quantita REAL NOT NULL CHECK(quantita > 0),
                Tipo TEXT CHECK(tipo IN ('produzione', 'trasporto', 'trasformazione', 'vendita')) NOT NULL,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
                FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE ComposizioneLotto (
                id_lotto_output TEXT NOT NULL,
                id_lotto_input TEXT NOT NULL,
                quantità_utilizzata REAL NOT NULL CHECK(quantità_utilizzata > 0),
                PRIMARY KEY (id_lotto_output, id_lotto_input),
                FOREIGN KEY (id_lotto_output) REFERENCES Operazione(Id_lotto),
                FOREIGN KEY (id_lotto_input) REFERENCES Operazione(Id_lotto)
            )
            ''',
            '''
            CREATE TABLE  Certificato (
                Id_certificato INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_prodotto INTEGER NOT NULL,
                Descrizione TEXT,
                Id_azienda_certificatore INTEGER NOT NULL,
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_azienda_certificatore) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
                FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE  Azioni_compensative (
                Id_azione INTEGER PRIMARY KEY AUTOINCREMENT,
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Id_azienda INTEGER NOT NULL,
                Co2_compensata REAL NOT NULL,
                Nome_azione TEXT NOT NULL,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE Magazzino (
                id_azienda TEXT NOT NULL,
                id_lotto TEXT NOT NULL,
                quantita REAL NOT NULL CHECK(quantita >= 0),
                PRIMARY KEY (id_azienda, id_lotto),
                FOREIGN KEY (id_azienda) REFERENCES Azienda(Id_azienda),
                FOREIGN KEY (id_lotto) REFERENCES Operazione(Id_lotto)
)
            ''',
            '''
            CREATE TABLE  Richiesta (
                Id_richiesta INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_azienda INTEGER NOT NULL,
                Id_richiedente INTEGER NOT NULL,
                Id_ricevente INTEGER NOT NULL,
                Id_trasportatore INTEGER NOT NULL,
                Id_prodotto INTEGER NOT NULL,
                Quantita REAL NOT NULL,
                Stato_ricevente TEXT CHECK(Stato_ricevente IN ('In attesa', 'Accettata', 'Rifiutata')),
                Stato_trasportatore TEXT CHECK(Stato_trasportatore IN ('In attesa', 'Accettata', 'Rifiutata')),
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            )
            '''
        ]

        # Check if the migrations were already
        if DatabaseMigrations._migrations_executed:
            logger.info("Migrations already executed. Skipping...")
            return

        try:
            db = Database()
            queries_with_params = [(query, ()) for query in TABLE_DELETION_QUERIES + TABLE_CREATION_QUERIES]
            db.execute_transaction(queries_with_params)

            # Check if the migrations were executed
            DatabaseMigrations._migrations_executed = True
            logger.info("BackEnd: run_migrations: Migrations completed successfully.")

        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            raise Exception(f"Migration error: {e}")
        

        # Esegui le query di seed solo se le migrazioni sono appena state eseguite
        try:
            # Seed delle credenziali
            SEED_CREDENZIALI = [
                ("aaa", "12345Aa@", "secret1"),
                ("ttt", "12345Aa@", "secret2"),
                ("trasf", "12345Aa@", "secret3"),
            ]

            for username, password, topt in SEED_CREDENZIALI:
                db.execute_query("""
                    INSERT OR IGNORE INTO Credenziali (Username, Password, topt_secret)
                    VALUES (?, ?, ?)
                """, (username, password, topt))

            # Ottieni gli ID delle credenziali inserite
            credenziali = db.fetch_results("SELECT Id_credenziali, Username FROM Credenziali")

            # Seed aziende di esempio collegate agli ID credenziali
            SEED_AZIENDE = [
                ("aaa", "Azienda Agricola Verde", "Via Roma 1", "Agricola", 10.5, 2.0),
                ("ttt", "Trasporti EcoExpress", "Via Milano 2", "Trasportatore", 30.0, 5.0),
                ("trasf", "Certificazioni BioCheck", "Via Torino 3", "Trasformatore", 5.0, 1.5),
            ]

            for username, nome, indirizzo, tipo, co2_emessa, co2_compensata in SEED_AZIENDE:
                # Trova l'ID credenziale corrispondente
                id_cred = next((idc for idc, user in credenziali if user == username), None)
                if id_cred:
                    logger.info("trovato id credenziale")
                    db.execute_query("""
                        INSERT OR IGNORE INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo, Co2_emessa, Co2_compensata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (id_cred, tipo, nome, indirizzo, co2_emessa, co2_compensata))
                        # Seed prodotti per l'azienda con id_azienda = 1
            SEED_PRODOTTI = [
                ("Mele Bio", 0),
                ("Succo di mela", 0)
            ]

            for nome, stato in SEED_PRODOTTI:
                db.execute_query("""
                    INSERT INTO Prodotto (Nome, Stato)
                    VALUES (?, ?)
                """, (nome, stato))

            # Ottieni gli ID dei prodotti inseriti
            prodotti = db.fetch_results("SELECT Id_prodotto, Nome FROM Prodotto")
            id_azienda = 1  # come richiesto

            # Operazioni di produzione per ciascun prodotto (lotti univoci)
            SEED_OPERAZIONI = [
                {
                    "prodotto": "Mele Bio",
                    "lotto": 1001,
                    "co2": 5.0,
                    "quantita": 100.0
                },
                {
                    "prodotto": "Succo di mela",
                    "lotto": 1002,
                    "co2": 3.2,
                    "quantita": 80.0
                }
            ]

            for op in SEED_OPERAZIONI:
                id_prodotto = next((idp for idp, nome in prodotti if nome == op["prodotto"]), None)
                if id_prodotto:
                    db.execute_query("""
                        INSERT INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
                        VALUES (?, ?, ?, ?, ?, 'produzione')
                    """, (id_azienda, id_prodotto, op["lotto"], op["co2"], op["quantita"]))

            # Inserimento nel Magazzino per i lotti prodotti
            for op in SEED_OPERAZIONI:
                db.execute_query("""
                    INSERT INTO Magazzino (id_azienda, id_lotto, quantita)
                    VALUES (?, ?, ?)
                """, (id_azienda, op["lotto"], op["quantita"]))

            logger.info("BackEnd: run_migrations: Seed prodotti, operazioni e magazzino completato.")

            
            

            logger.info("BackEnd: run_migrations: Seed dei dati iniziali completato.")
        except Exception as e:
            logger.error(f"Errore durante l'inserimento dei dati di seed: {e}")


        
