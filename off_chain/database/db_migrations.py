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
                Co2_emessa REAL NOT NULL DEFAULT 0,
                Co2_compensata REAL NOT NULL DEFAULT 0,
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_lotto_output INTEGER NOT NULL,
                id_lotto_input INTEGER NOT NULL,
                quantità_utilizzata REAL NOT NULL CHECK(quantità_utilizzata > 0),
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
                Id_richiedente INTEGER NOT NULL,
                Id_ricevente INTEGER NOT NULL,
                Id_trasportatore INTEGER NOT NULL,
                Id_prodotto INTEGER NOT NULL,
                Quantita REAL NOT NULL,
                Stato_ricevente TEXT CHECK(Stato_ricevente IN ('In attesa', 'Accettata', 'Rifiutata')),
                Stato_trasportatore TEXT CHECK(Stato_trasportatore IN ('In attesa', 'Accettata', 'Rifiutata')),
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_richiedente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
                FOREIGN KEY (Id_ricevente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
                FOREIGN KEY (Id_trasportatore) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            )
            '''
        ]
        
        
        
        # Check if the migrations were already executed
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
            # Chiamata alla funzione per inserire i seed
            DatabaseMigrations.insert_seed_data(db)

            logger.info("BackEnd: run_migrations: Seed dei dati iniziali completato.")
        except Exception as e:
            logger.error(f"Errore durante l'inserimento dei dati di seed: {e}")

    @staticmethod
    def insert_seed_data(db):

        try:
            # Seed delle credenziali
            SEED_CREDENZIALI = [
                ("aaa", "12345Aa@", "secret1"),
                ("ttt", "12345Aa@", "secret2"),
                ("trasf", "12345Aa@", "secret3"),
                ("riv","12345Aa@","secret3")
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
                ("riv", "riv BioCheck", "Via Torino 3", "Rivenditore", 5.0, 1.5),
            ]

            for username, nome, indirizzo, tipo, co2_emessa, co2_compensata in SEED_AZIENDE:
                # Trova l'ID credenziale corrispondente
                id_cred = next((idc for idc, user in credenziali if user == username), None)
                if id_cred:
                    db.execute_query("""
                        INSERT OR IGNORE INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo, Co2_emessa, Co2_compensata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (id_cred, tipo, nome, indirizzo, co2_emessa, co2_compensata))

            # Seed dei prodotti
            SEED_PRODOTTI = [
                
                ("farina", 0),
                ("zucchero",0),
                ("impasto",1)
            ]

            for nome, stato in SEED_PRODOTTI:
                db.execute_query("""
                    INSERT OR IGNORE INTO Prodotto (Nome, Stato)
                    VALUES (?, ?)
                """, (nome, stato))

            SEED_MAGAZZINO = [

                
                (1,1001, 100),
                (1,1002,50),
                (3,2001,1)
            ]

            for id_az, id_lot, qt in SEED_MAGAZZINO:
                db.execute_query("""
                    INSERT OR IGNORE INTO Magazzino (id_azienda, id_lotto, quantita)
                    VALUES (?, ?,?)
                """, (id_az, id_lot,qt))


            # Operazioni di produzione delle materie prime
            operazioni = [
    # Produzione mele
                (1, 1, 1001, 50.0, 100.0, 'produzione'),
                # Produzione zucchero
                (1, 2, 1002, 25.0, 50.0, 'produzione'),
                # Trasformazione in succo
                (3, 3, 2001, 10.0, 100.0, 'trasformazione'),

                (3, 3, 2002, 1.0, 10.0, 'vendita'),

                
            ]

            for op in operazioni:
                db.execute_query("""
                    INSERT OR IGNORE INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, op)

            # ComposizioneLotto: il succo di mela in bottiglia è fatto da mele e zucchero
            composizioni = [
                  # usa 40 zucchero
                (2001, 1001, 50.0),
                (2001, 1002, 50.0),
                (2002,2001,10)  # usa 40 di zucchero
            ]

            for output_lotto, input_lotto, quantita_usata in composizioni:
                db.execute_query("""
                    INSERT OR IGNORE INTO ComposizioneLotto (id_lotto_output, id_lotto_input, quantità_utilizzata)
                    VALUES (?, ?, ?)
                """, (output_lotto, input_lotto, quantita_usata))

            # Magazzino: solo il prodotto finito (succo di mela in bottiglia) è nel magazzino del trasformatore
            db.execute_query("""
                INSERT OR IGNORE INTO Magazzino (id_azienda, id_lotto, quantita)
                VALUES (?, ?, ?)
            """, (3, 2002, 130.0))  # solo il prodotto finito

            # Richiesta di prodotto da parte di un rivenditore (vendita)
            db.execute_query("""
                INSERT INTO Richiesta (
                    Id_richiedente, Id_ricevente, Id_trasportatore, 
                    Id_prodotto, Quantita, Stato_ricevente, Stato_trasportatore
                )
                VALUES ( ?, ?, ?, ?, ?, ?, ?)
            """, (  
                1,  # Id_richiedente (azienda che vende il succo di mela in bottiglia)
                2,  # Id_ricevente (azienda di distribuzione)
                3,  # Id_trasportatore (trasportatore)
                2,  # Id prodotto "Succo di mela in bottiglia"
                50.0,  # Quantità richiesta
                'In attesa',  # Stato_ricevente
                'In attesa'   # Stato_trasportatore
            ))

            # Logger
            logger.info("Seed dei dati iniziali completato.")

        except Exception as e:
            logger.error(f"Errore durante l'inserimento dei dati di seed: {e}")


