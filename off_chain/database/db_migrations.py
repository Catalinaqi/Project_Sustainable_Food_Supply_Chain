# pylint: disable=too-many-lines
# Justification: This file contains extensive DDL and DML for migrations and seeding,
# which naturally leads to a higher line count. Breaking it down further might reduce
# readability of the overall migration flow.
"""
Manages database schema migrations and initial data seeding.

This module provides functionality to:
1. Drop existing tables (if necessary, for a clean slate).
2. Create new tables according to the defined schema.
3. Insert initial seed data into the newly created tables.

It ensures migrations are run only once per application execution.
"""
from typing import List, Tuple, Any, Dict, Optional # For type hinting

# Assuming these imports are correct and Pylint can find them.
from configuration.log_load_setting import logger
from configuration.database import Database # Assuming Database class is Pylint-compliant

# --- Constants for Table Names (Good for preventing typos) ---
# (This is optional but can be helpful in larger schemas)
# TBL_CREDENZIALI = "Credenziali"
# TBL_AZIENDA = "Azienda"
# ... and so on for all tables

# --- DDL Statements ---

# Note: Order is crucial for dropping tables due to foreign key constraints.
# Tables with dependencies must be dropped before the tables they depend on.
_TABLE_DELETION_QUERIES: List[str] = [
    'DROP TABLE IF EXISTS Richiesta',
    'DROP TABLE IF EXISTS Magazzino',
    'DROP TABLE IF EXISTS ComposizioneLotto',
    'DROP TABLE IF EXISTS Azioni_compensative',
    'DROP TABLE IF EXISTS Certificato',
    'DROP TABLE IF EXISTS Operazione',
    'DROP TABLE IF EXISTS Prodotto',
    'DROP TABLE IF EXISTS Soglie',
    'DROP TABLE IF EXISTS Azienda',
    'DROP TABLE IF EXISTS Credenziali',
]

# Note: Order is crucial for creating tables due to foreign key constraints.
# Tables must be created before other tables can reference them.
_TABLE_CREATION_QUERIES: List[str] = [
    """
    CREATE TABLE IF NOT EXISTS Credenziali (
        Id_credenziali INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE NOT NULL,
        Password TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Soglie (
        Operazione TEXT NOT NULL,
        Prodotto INTEGER NOT NULL,
        Soglia_Massima INTEGER NOT NULL,
        firma TEXT NOT NULL,
        PRIMARY KEY (Operazione, Prodotto)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Azienda (
        Id_azienda INTEGER PRIMARY KEY AUTOINCREMENT,
        Id_credenziali INTEGER NOT NULL,
        Tipo TEXT CHECK(Tipo IN ('Agricola', 'Trasportatore', 'Trasformatore', 'Rivenditore', 'Certificatore')) NOT NULL,
        Nome TEXT NOT NULL,
        Indirizzo TEXT NOT NULL,
        Co2_emessa REAL NOT NULL DEFAULT 0,
        Co2_compensata REAL NOT NULL DEFAULT 0,
        Token INTEGER NOT NULL DEFAULT 100,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (Id_credenziali) REFERENCES Credenziali(Id_credenziali) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Prodotto (
        Id_prodotto INTEGER PRIMARY KEY AUTOINCREMENT,
        Nome TEXT NOT NULL,
        Stato INTEGER, -- Consider using TEXT CHECK for clarity if Stato has defined meanings
        Data_di_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Operazione (
        Id_operazione INTEGER PRIMARY KEY AUTOINCREMENT,
        Id_azienda INTEGER NOT NULL,
        Id_prodotto INTEGER NOT NULL,
        Id_lotto INTEGER UNIQUE NOT NULL, -- SQLite usually creates an index for UNIQUE
        Data_operazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        Consumo_CO2 REAL NOT NULL,
        quantita REAL NOT NULL CHECK(quantita > 0),
        Tipo TEXT CHECK(tipo IN ('produzione', 'trasporto', 'trasformazione', 'vendita')) NOT NULL,
        FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
        FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ComposizioneLotto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_lotto_output INTEGER NOT NULL, -- This should likely reference Operazione(Id_lotto)
        id_lotto_input INTEGER NOT NULL,
        quantità_utilizzata REAL NOT NULL CHECK(quantità_utilizzata > 0),
        FOREIGN KEY (id_lotto_output) REFERENCES Operazione(Id_lotto) ON DELETE CASCADE, -- Added
        FOREIGN KEY (id_lotto_input) REFERENCES Operazione(Id_lotto) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Certificato (
        Id_certificato INTEGER PRIMARY KEY AUTOINCREMENT,
        Id_lotto INTEGER NOT NULL, -- This should reference Operazione(Id_lotto)
        Descrizione TEXT,
        Id_azienda_certificatore INTEGER NOT NULL,
        Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (Id_lotto) REFERENCES Operazione(Id_lotto) ON DELETE CASCADE, -- Added
        FOREIGN KEY (Id_azienda_certificatore) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Azioni_compensative (
        Id_azione INTEGER PRIMARY KEY AUTOINCREMENT,
        Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        Id_azienda INTEGER NOT NULL,
        Co2_compensata REAL NOT NULL,
        Nome_azione TEXT NOT NULL,
        FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Magazzino (
        id_azienda INTEGER NOT NULL, -- Changed to INTEGER to match Azienda.Id_azienda
        id_lotto INTEGER NOT NULL,   -- Changed to INTEGER to match Operazione.Id_lotto
        quantita REAL NOT NULL CHECK(quantita >= 0),
        PRIMARY KEY (id_azienda, id_lotto),
        FOREIGN KEY (id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
        FOREIGN KEY (id_lotto) REFERENCES Operazione(Id_lotto) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Richiesta (
        Id_richiesta INTEGER PRIMARY KEY AUTOINCREMENT,
        Id_richiedente INTEGER NOT NULL,
        Id_ricevente INTEGER NOT NULL,
        Id_trasportatore INTEGER NOT NULL,
        Id_prodotto INTEGER NOT NULL, -- Should this reference Prodotto(Id_prodotto)?
        Quantita REAL NOT NULL,
        Stato_ricevente TEXT CHECK(Stato_ricevente IN ('In attesa', 'Accettata', 'Rifiutata')),
        Stato_trasportatore TEXT CHECK(Stato_trasportatore IN ('In attesa', 'Accettata', 'Rifiutata')),
        Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (Id_richiedente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
        FOREIGN KEY (Id_ricevente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
        FOREIGN KEY (Id_trasportatore) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
        FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE -- Added based on assumption
    )
    """
]

# --- Seed Data Definitions ---
# pylint: disable=invalid-name
# Justification: SEED_XXX are module-level constants representing data.
_SEED_CREDENZIALI: List[Tuple[str, str]] = [
    ("aaa", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
    ("ttt", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
    ("trasf", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
    ("riv", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
    ("cert", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
]

_SEED_AZIENDE: List[Tuple[str, str, str, str, float, float]] = [
    ("aaa", "Azienda Agricola Verde", "Via Roma 1", "Agricola", 10.5, 2.0),
    ("ttt", "Trasporti EcoExpress", "Via Milano 2", "Trasportatore", 30.0, 5.0),
    ("trasf", "Industria Alimentare Pro", "Via Genova 7", "Trasformatore", 15.0, 3.0), # Name changed for clarity
    ("riv", "Supermercato Fresco Facile", "Via Napoli 4", "Rivenditore", 5.0, 1.0), # Name changed
    ("cert", "Certificazioni BioCheck", "Via Torino 3", "Certificatore", 2.0, 0.5), # Name changed
]

_SEED_PRODOTTI: List[Tuple[str, int]] = [
    ("grano", 0), ("mais", 0), ("soia", 0), ("riso", 0), ("pomodoro", 0),
    ("latte", 0), ("uova", 0), ("patate", 0), ("mele", 0), ("olive", 0),
    ("pane", 1), ("farina di grano", 1), ("olio di oliva", 1),
    ("passata di pomodoro", 1), ("formaggio", 1), ("yogurt", 1),
    ("conserve di frutta", 1), ("patatine fritte", 1), ("pasta", 1),
    ("salsa di soia", 1),
]

_SEED_OPERAZIONI: List[Tuple[int, int, int, float, float, str]] = [
    (1, 1, 1001, 50.0, 100.0, 'produzione'), # Azienda 1 (Agricola), Prodotto 1 (grano), Lotto 1001
    (1, 9, 1002, 25.0, 50.0, 'produzione'), # Azienda 1 (Agricola), Prodotto 9 (mele), Lotto 1002
    (2, 1, 1010, 10.0, 100.0, 'trasporto'),# Azienda 2 (Trasportatore), Prodotto 1 (grano), Lotto 1010 (nuovo lotto per trasporto)
    (2, 9, 1020, 5.0, 50.0, 'trasporto'),  # Azienda 2 (Trasportatore), Prodotto 9 (mele), Lotto 1020
    (3, 12, 1100, 30.0, 90.0, 'trasformazione'),# Azienda 3 (Trasformatore), Prodotto 12 (farina), Lotto 1100
    (2, 12, 1011, 8.0, 90.0, 'trasporto'), # Azienda 2 (Trasportatore), Prodotto 12 (farina), Lotto 1011
    (4, 12, 2000, 2.0, 10.0, 'vendita'),  # Azienda 4 (Rivenditore), Prodotto 12 (farina), Lotto 2000
]

_SEED_MAGAZZINO: List[Tuple[int, int, float]] = [
    (1, 1001, 100.0), # Azienda Agricola ha grano
    (1, 1002, 50.0),  # Azienda Agricola ha mele
    (3, 1010, 100.0), # Trasformatore riceve grano (lotto 1010)
    (3, 1020, 50.0),  # Trasformatore riceve mele (lotto 1020)
    # (3, 1100, 90.0)  # Dopo trasformazione, il Trasformatore ha farina (lotto 1100) -> Questo si deduce
    # (4, 1011, 90.0)  # Rivenditore riceve farina (lotto 1011) -> Questo si deduce
]

_SEED_COMPOSIZIONE_LOTTO: List[Tuple[int, int, float]] = [
    (1100, 1010, 100.0), # Lotto farina (1100) usa tutto il grano trasportato (1010)
    # Aggiungere altre composizioni se necessario, es. pane da farina
]

_SEED_CERTIFICATI: List[Tuple[int, str, int]] = [
    (1001, "Certificato BIO per grano lotto 1001", 5), # Certificatore (Azienda 5)
    (1100, "Certificato qualità farina lotto 1100", 5),
    (2000, "Certificato vendita farina lotto 2000", 5),
]

_SEED_RICHIESTA: Tuple[int, int, int, int, float, str, str] = (
    4,  # Id_richiedente (Rivenditore, Azienda 4) chiede farina
    3,  # Id_ricevente (Trasformatore, Azienda 3) che ha la farina
    2,  # Id_trasportatore (Trasportatore, Azienda 2)
    12, # Id_prodotto (Farina di grano)
    10.0,
    'In attesa',
    'In attesa',
)

_SEED_SOGLIE: List[Tuple[str, int, int, str]] = [
    ("produzione", 1, 52, "b990173ff0b8d24e9d41dbaa64a39cda476c54cf50b465811c788ee36a211369"),
    ("produzione", 2, 54, "2a747f613ae99ad4444a0160f4aa98c3f8e47416889b32ad30dd919c51e3f305"),
    # ... (mantenere il resto delle soglie come erano, ma assicurarsi che Prodotto ID sia intero)
    ("trasporto", 1, 52, "39de91dc8df31c6d647431e1038d30a188b3cb271cb32e2376162cc2aa0a1809"),
    ("trasporto", 12, 74, "764ef09dd6c7feafd9b944f6cb5ab738b33226774e1cd97f424cd58601249b15"),
    ("trasformazione", 12, 74, "7bc5b3288dc49521fbb2c21e5d49dd7e60b73338a8a6334a88770ba8066af323"),
    ("vendita", 12, 74, "7c5cb17ba405a4b3d6975dbd82981275f5990bc5e3fc5cf2fe26a17a9d58dad3"),
]
# pylint: enable=invalid-name

class DatabaseMigrations:
<<<<<<< Updated upstream
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

=======
    """
    Handles database schema creation and initial data seeding.
    Ensures that migrations are run only once per application session.
    """
    _migrations_executed: bool = False # Class variable to track execution status

    @staticmethod
    def run_migrations() -> None:
        """
        Executes the full database migration process:
        1. Drops all known tables (for a clean environment).
        2. Creates all tables according to the defined schema.
        3. Inserts initial seed data if migrations were just performed.

        This method ensures it only runs once per application execution.

        Raises:
            RuntimeError: If there's a critical error during migrations.
        """
>>>>>>> Stashed changes
        if DatabaseMigrations._migrations_executed:
            logger.info("Database migrations already executed this session. Skipping.")
            return

        logger.info("Starting database migration process...")
        db: Optional[Database] = None # Initialize to allow use in finally block if needed
        try:
<<<<<<< Updated upstream
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
=======
            db = Database() # Get the singleton database instance

            # Combine DDL queries into a single transaction
            # Using "CREATE TABLE IF NOT EXISTS" makes dropping optional for idempotent runs,
            # but for a true "clean slate" migration, dropping is good.
            ddl_queries: List[Tuple[str, Tuple[Any, ...]]] = [
                (query, ()) for query in _TABLE_DELETION_QUERIES + _TABLE_CREATION_QUERIES
            ]
            logger.info("Executing DDL queries (drop and create tables)...")
            db.execute_transaction(ddl_queries)
            logger.info("Table schema migration (DDL) completed successfully.")

            # Set flag immediately after successful DDL
            DatabaseMigrations._migrations_executed = True

            # Proceed to seeding only if DDL was successful
            logger.info("Starting data seeding process...")
            DatabaseMigrations._seed_all_data(db)
            logger.info("Initial data seeding completed successfully.")

            logger.info("Full database migration and seeding process finished.")

        except Exception as e: # Catching broad exception from Database class or other issues
            logger.critical("Critical error during database migration: %s", e, exc_info=True)
            # Depending on severity, you might want to exit or handle differently
            raise RuntimeError(f"Database migration failed: {e}") from e
        # 'finally' block is not strictly needed here if db.close() is handled by Database.__del__
        # or a context manager.

    @staticmethod
    def _seed_all_data(db: Database) -> None:
        """
        Helper method to insert all defined seed data into the database.
        This is called after the table schema has been successfully created/updated.

        Args:
            db: The active Database instance.
        """
        try:
            logger.info("Seeding 'Credenziali' table...")
            for username, password_hash in _SEED_CREDENZIALI:
                db.execute_query(
                    "INSERT OR IGNORE INTO Credenziali (Username, Password) VALUES (?, ?)",
                    (username, password_hash)
                )

            # Fetch inserted credenziali to get their IDs for linking
            # Type hinting for rows fetched from database
            credenziali_rows: List[Tuple[int, str]] = db.fetch_all(
                "SELECT Id_credenziali, Username FROM Credenziali"
            )
            credenziali_map: Dict[str, int] = {
                username: id_cred for id_cred, username in credenziali_rows
            }
            logger.debug("Fetched credenziali map: %s", credenziali_map)


            logger.info("Seeding 'Azienda' table...")
            for username, nome, indirizzo, tipo, co2_em, co2_comp in _SEED_AZIENDE:
                id_credenziale = credenziali_map.get(username)
                if id_credenziale:
                    db.execute_query(
                        """INSERT OR IGNORE INTO Azienda
                           (Id_credenziali, Tipo, Nome, Indirizzo, Co2_emessa, Co2_compensata)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (id_credenziale, tipo, nome, indirizzo, co2_em, co2_comp)
                    )
                else:
                    logger.warning("Could not find Id_credenziali for username '%s' while seeding Azienda.", username)
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
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
=======
            logger.info("Seeding 'Prodotto' table...")
            for nome, stato in _SEED_PRODOTTI:
                db.execute_query(
                    "INSERT OR IGNORE INTO Prodotto (Nome, Stato) VALUES (?, ?)",
                    (nome, stato)
                )

            logger.info("Seeding 'Operazione' table...")
            for id_az, id_prod, id_lotto, co2, quant, tipo_op in _SEED_OPERAZIONI:
                db.execute_query(
                    """INSERT OR IGNORE INTO Operazione
                       (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (id_az, id_prod, id_lotto, co2, quant, tipo_op)
                )

            logger.info("Seeding 'Magazzino' table...")
            for id_az, id_lotto, qt in _SEED_MAGAZZINO:
                db.execute_query(
                    "INSERT OR IGNORE INTO Magazzino (id_azienda, id_lotto, quantita) VALUES (?, ?, ?)",
                    (id_az, id_lotto, qt)
                )

            logger.info("Seeding 'ComposizioneLotto' table...")
            for out_l, in_l, qty_used in _SEED_COMPOSIZIONE_LOTTO:
                db.execute_query(
                    """INSERT OR IGNORE INTO ComposizioneLotto
                       (id_lotto_output, id_lotto_input, quantità_utilizzata)
                       VALUES (?, ?, ?)""",
                    (out_l, in_l, qty_used)
                )

            logger.info("Seeding 'Certificato' table...")
            for id_lotto, desc, id_az_cert in _SEED_CERTIFICATI:
                db.execute_query(
                    """INSERT OR IGNORE INTO Certificato
                       (Id_lotto, Descrizione, Id_azienda_certificatore)
                       VALUES (?, ?, ?)""",
                    (id_lotto, desc, id_az_cert)
                )

            logger.info("Seeding 'Richiesta' table...")
            db.execute_query(
                """INSERT OR IGNORE INTO Richiesta
                   (Id_richiedente, Id_ricevente, Id_trasportatore, Id_prodotto,
                    Quantita, Stato_ricevente, Stato_trasportatore)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                _SEED_RICHIESTA
            )

            logger.info("Seeding 'Soglie' table...")
            for op_type, prod_id_str, soglia_max_str, firma_str in _SEED_SOGLIE:
                try:
                    prod_id = int(prod_id_str)
                    soglia_max = int(soglia_max_str)
                    db.execute_query(
                        "INSERT OR IGNORE INTO Soglie (Operazione, Prodotto, Soglia_Massima, firma) VALUES (?, ?, ?, ?)",
                        (op_type, prod_id, soglia_max, firma_str)
                    )
                except ValueError:
                    logger.error(
                        "Invalid integer value for Prodotto ('%s') or Soglia_Massima ('%s') in _SEED_SOGLIE for operation '%s'. Skipping this entry.",
                        prod_id_str, soglia_max_str, op_type
                    )

            logger.info("All seed data insertion attempts completed.")

        except Exception as e: # Catching broad exception from Database class or other issues
            logger.error("Error during data seeding: %s", e, exc_info=True)
            # Decide if this error should halt the application or just be logged
            # For seeding, it might be acceptable to log and continue if some seeds fail,
            # but DDL failures are usually critical.
            # Re-raising here will propagate to run_migrations's handler.
            raise RuntimeError(f"Data seeding failed: {e}") from e


if __name__ == "__main__":
    # This block allows testing the migrations independently.
    # It assumes your 'configuration.database.Database' and 'configuration.log_load_setting.logger'
    # are set up correctly or can be mocked/initialized here.

    # For standalone testing, you might need to set up a basic logger if not already done
    import logging as pylogging # Alias to avoid conflict with module 'logger'
    if not logger.hasHandlers():
        pylogging.basicConfig(level=pylogging.DEBUG, format='%(levelname)s: %(message)s')
        # Assuming 'logger' is the one from 'configuration.log_load_setting'
        # This setup below might be redundant if your global logger is already well-configured.
        # logger.addHandler(pylogging.StreamHandler())
        # logger.setLevel(pylogging.DEBUG)


    logger.info("--- Running Database Migrations Self-Test ---")
    try:
        # To ensure a clean test, you might want to delete the database file first
        # from configuration.db_load_setting import DATABASE_PATH # Assuming this exists
        # test_db_file = Path(DATABASE_PATH)
        # if test_db_file.exists():
        #     logger.info(f"Deleting existing test database file: {test_db_file}")
        #     test_db_file.unlink()

        DatabaseMigrations.run_migrations()
        logger.info("Self-test: Migrations completed successfully via run_migrations().")

        # Attempt to run again to test the _migrations_executed flag
        logger.info("Self-test: Attempting to run migrations again (should be skipped)...")
        DatabaseMigrations.run_migrations()

        # Optionally, query some data to verify seeding
        db_instance = Database()
        num_aziende = db_instance.fetch_scalar("SELECT COUNT(*) FROM Azienda")
        logger.info("Self-test: Number of aziende seeded: %s", num_aziende)
        assert num_aziende is not None and num_aziende > 0

        num_soglie = db_instance.fetch_scalar("SELECT COUNT(*) FROM Soglie")
        logger.info("Self-test: Number of soglie seeded: %s", num_soglie)
        assert num_soglie is not None and num_soglie > 0


    except RuntimeError as e:
        logger.error("Self-test: Database migration self-test failed: %s", e, exc_info=True)
    except Exception as e: # pylint: disable=broad-except
        logger.error("Self-test: An unexpected error occurred during self-test: %s", e, exc_info=True)
    finally:
        # Clean up database instance if necessary, though singleton might handle it
        # db_instance.close() # If your Database class has an explicit close
        logger.info("--- Database Migrations Self-Test Finished ---")
>>>>>>> Stashed changes
