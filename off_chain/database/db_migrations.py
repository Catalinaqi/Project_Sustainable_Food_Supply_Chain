from off_chain.configuration.log_load_setting import logger
from off_chain.configuration.db_manager_setting import DatabaseManagerSetting


class DatabaseMigrations:



    # Variable of the class to track if the migrations were executed
    _migrations_executed = False

    @staticmethod
    def run_migrations():
        TABLE_CREATION_QUERIES = [
            '''
            CREATE TABLE IF NOT EXISTS Credenziali (
                Id_credenziali INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL,
                topt_secret TEXT NOT NULL
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Soglie (
                Operazione TEXT NOT NULL,
                Prodotto TEXT NOT NULL,
                Soglia_Massima REAL NOT NULL,
                Tipo TEXT NOT NULL,
                PRIMARY KEY (Operazione, Prodotto)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Azienda (
                Id_azienda INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_credenziali INTEGER NOT NULL,
                Tipo TEXT CHECK(Tipo IN ('Agricola', 'Trasportatore', 'Trasformatore', 'Rivenditore', 'Certificatore')),
                Nome TEXT NOT NULL,
                Indirizzo TEXT NOT NULL,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_credenziali) REFERENCES Credenziali(Id_credenziali) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Prodotto (
                Id_prodotto INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome TEXT NOT NULL,
                Quantita REAL NOT NULL,
                Stato INTEGER,
                Data_di_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Operazione (
                Id_operazione INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_azienda INTEGER NOT NULL,
                Id_prodotto INTEGER NOT NULL,
                Data_operazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Consumo_CO2 REAL NOT NULL,
                Operazione TEXT,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
                FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Certificato (
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
            CREATE TABLE IF NOT EXISTS Composizione (
                Prodotto INTEGER NOT NULL,
                Materia_prima INTEGER NOT NULL,
                PRIMARY KEY (Prodotto, Materia_prima)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS Azioni_compensative (
                Id_azione INTEGER PRIMARY KEY AUTOINCREMENT,
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Id_azienda INTEGER NOT NULL,
                Co2_compensata REAL NOT NULL,
                Nome_azione TEXT NOT NULL,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            )
            '''
        ]

        # Check if the migrations were already
        if DatabaseMigrations._migrations_executed:
            logger.info("Migrations already executed. Skipping...")
            return

        try:
            queries_with_params = [(query, ()) for query in TABLE_CREATION_QUERIES]

            xx = DatabaseManagerSetting()

            # Execute migrations
            xx.execute_bd_migrations(queries_with_params)

            # Check if the migrations were executed
            DatabaseMigrations._migrations_executed = True
            logger.info("BackEnd: run_migrations: Migrations completed successfully.")

        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            raise Exception(f"Migration error: {e}")


# Execute migrations when the module is imported
#DatabaseMigrations.run_migrations()
#logger.info("Step 3, backend: Executed migrations of tables...")
