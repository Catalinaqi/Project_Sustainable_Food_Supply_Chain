from configuration.log_load_setting import logger
from configuration.database import Database


class DatabaseMigrations:
    """Class to handle database migrations and initial seed data insertion."""

    _migrations_executed = False

    @staticmethod
    def run_migrations():
        """Run the full set of migrations and seed data if not already executed."""
        # Tables must be dropped in reverse order of dependencies to avoid FK constraint errors
        table_deletion_queries = [
            'DROP TABLE IF EXISTS Richiesta;',
            'DROP TABLE IF EXISTS Magazzino;',
            'DROP TABLE IF EXISTS ComposizioneLotto;',
            'DROP TABLE IF EXISTS Azioni_compensative;',
            'DROP TABLE IF EXISTS Certificato;',
            'DROP TABLE IF EXISTS Operazione;',
            'DROP TABLE IF EXISTS Prodotto;',
            'DROP TABLE IF EXISTS Soglie;',
            'DROP TABLE IF EXISTS Azienda;',
            'DROP TABLE IF EXISTS Credenziali;'
        ]

        table_creation_queries = [
            '''
            CREATE TABLE Credenziali (
                Id_credenziali INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL
            );
            ''',
            '''
            CREATE TABLE Soglie (
                Operazione TEXT NOT NULL,
                Prodotto INTEGER NOT NULL,
                Soglia_Massima INTEGER NOT NULL,
                firma TEXT NOT NULL,
                PRIMARY KEY (Operazione, Prodotto)
            );
            ''',
            '''
            CREATE TABLE Azienda (
                Id_azienda INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_credenziali INTEGER NOT NULL,
                Tipo TEXT CHECK(Tipo IN ('Agricola', 'Trasportatore', 'Trasformatore', 'Rivenditore', 'Certificatore')),
                Nome TEXT NOT NULL,
                Indirizzo TEXT NOT NULL,
                Co2_emessa REAL NOT NULL DEFAULT 0,
                Co2_compensata REAL NOT NULL DEFAULT 0,
                Token INTEGER NOT NULL DEFAULT 100,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_credenziali) REFERENCES Credenziali(Id_credenziali) ON DELETE CASCADE
            );
            ''',
            '''
            CREATE TABLE Prodotto (
                Id_prodotto INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome TEXT NOT NULL,
                Stato INTEGER,
                Data_di_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            ''',
            '''
            CREATE TABLE Operazione (
                Id_operazione INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_azienda INTEGER NOT NULL,
                Id_prodotto INTEGER NOT NULL,
                Id_lotto INTEGER UNIQUE NOT NULL,
                Data_operazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Consumo_CO2 REAL NOT NULL,
                quantita REAL NOT NULL CHECK(quantita > 0),
                Tipo TEXT CHECK(Tipo IN ('produzione', 'trasporto', 'trasformazione', 'vendita')) NOT NULL,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
                FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE
            );
            ''',
            '''
            CREATE TABLE ComposizioneLotto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_lotto_output INTEGER NOT NULL,
                id_lotto_input INTEGER NOT NULL,
                quantita_utilizzata REAL NOT NULL CHECK(quantita_utilizzata > 0),
                FOREIGN KEY (id_lotto_input) REFERENCES Operazione(Id_lotto)
            );
            ''',
            '''
            CREATE TABLE Certificato (
                Id_certificato INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_lotto INTEGER NOT NULL,
                Descrizione TEXT,
                Id_azienda_certificatore INTEGER NOT NULL,
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_azienda_certificatore) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            );
            ''',
            '''
            CREATE TABLE Azioni_compensative (
                Id_azione INTEGER PRIMARY KEY AUTOINCREMENT,
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Id_azienda INTEGER NOT NULL,
                Co2_compensata REAL NOT NULL,
                Nome_azione TEXT NOT NULL,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            );
            ''',
            '''
            CREATE TABLE Magazzino (
                id_azienda INTEGER NOT NULL,
                id_lotto INTEGER NOT NULL,
                quantita REAL NOT NULL CHECK(quantita >= 0),
                PRIMARY KEY (id_azienda, id_lotto),
                FOREIGN KEY (id_azienda) REFERENCES Azienda(Id_azienda),
                FOREIGN KEY (id_lotto) REFERENCES Operazione(Id_lotto)
            );
            ''',
            '''
            CREATE TABLE Richiesta (
                Id_richiesta INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_richiedente INTEGER NOT NULL,
                Id_ricevente INTEGER NOT NULL,
                Id_trasportatore INTEGER NOT NULL,
                Id_prodotto INTEGER NOT NULL,
                Quantita REAL NOT NULL,
                Stato_ricevente TEXT CHECK(Stato_ricevente IN ('In attesa', 'Accettata', 'Rifiutata')),
                Stato_trasportatore TEXT CHECK(Stato_trasportatore IN ('In attesa', 'Accettata', 'Rifiutata')),
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_richiedente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
                FOREIGN KEY (Id_ricevente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
                FOREIGN KEY (Id_trasportatore) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            );
            '''
        ]

        if DatabaseMigrations._migrations_executed:
            logger.info("Migrations already executed. Skipping...")
            return

        try:
            db = Database()
            queries_with_params = [(query, ()) for query in table_deletion_queries + table_creation_queries]
            db.execute_transaction(queries_with_params)
            DatabaseMigrations._migrations_executed = True
            logger.info("BackEnd: run_migrations: Migrations completed successfully.")
        except Exception as err:
            logger.error(f"Error during database migration: {err}")
            raise Exception(f"Migration error: {err}")

        try:
            DatabaseMigrations.insert_seed_data(db)
            logger.info("BackEnd: run_migrations: Seed data insertion completed.")
        except Exception as err:
            logger.error(f"Error during seed data insertion: {err}")

    @staticmethod
    def insert_seed_data(db):
        """Insert initial seed data into the database."""
        # Seed credentials
        seed_credenziali = [
            ("aaa", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
            ("ttt", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
            ("trasf", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
            ("riv", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
            ("cert", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45")
        ]

        for username, password in seed_credenziali:
            db.execute_query(
                """
                INSERT OR IGNORE INTO Credenziali (Username, Password)
                VALUES (?, ?)
                """,
                (username, password),
            )

        credenziali = db.fetch_results("SELECT Id_credenziali, Username FROM Credenziali")

        # Seed aziende linked to credentials
        seed_aziende = [
            ("aaa", "Azienda Agricola Verde", "Via Roma 1", "Agricola", 10.5, 2.0),
            ("ttt", "Trasporti EcoExpress", "Via Milano 2", "Trasportatore", 30.0, 5.0),
            ("trasf", "Certificazioni BioCheck", "Via Torino 3", "Trasformatore", 5.0, 1.5),
            ("riv", "riv BioCheck", "Via Torino 3", "Rivenditore", 5.0, 1.5),
            ("cert", "cert BioCheck", "Via Torino 3", "Certificatore", 5.0, 1.5),
        ]

        for username, nome, indirizzo, tipo, co2_emessa, co2_compensata in seed_aziende:
            id_cred = next((idc for idc, user in credenziali if user == username), None)
            if id_cred is not None:
                db.execute_query(
                    """
                    INSERT OR IGNORE INTO Azienda (
                        Id_credenziali, Tipo, Nome, Indirizzo, Co2_emessa, Co2_compensata
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (id_cred, tipo, nome, indirizzo, co2_emessa, co2_compensata),
                )

        # Seed prodotti
        seed_prodotti = ["patate", "carote", "mele", "fragole", "albicocche"]
        for prodotto in seed_prodotti:
            db.execute_query(
                "INSERT OR IGNORE INTO Prodotto (Nome, Stato) VALUES (?, ?)",
                (prodotto, 0),
            )

        # Seed soglie (example)
        soglie = [
            ("produzione", 1, 20, "firma1"),
            ("trasporto", 1, 50, "firma2"),
            ("trasformazione", 1, 30, "firma3"),
            ("vendita", 1, 15, "firma4")
        ]
        for operazione, prodotto, soglia, firma in soglie:
            db.execute_query(
                """
                INSERT OR IGNORE INTO Soglie (Operazione, Prodotto, Soglia_Massima, firma)
                VALUES (?, ?, ?, ?)
                """,
                (operazione, prodotto, soglia, firma),
            )

        # Seed azioni compensative
        azioni_compensative = [
            (1, 5, "piantumazione alberi"),
            (2, 10, "pannelli solari"),
            (3, 3, "riforestazione")
        ]
        for id_azienda, co2_compensata, nome_azione in azioni_compensative:
            db.execute_query(
                """
                INSERT INTO Azioni_compensative (Id_azienda, Co2_compensata, Nome_azione)
                VALUES (?, ?, ?)
                """,
                (id_azienda, co2_compensata, nome_azione),
            )
