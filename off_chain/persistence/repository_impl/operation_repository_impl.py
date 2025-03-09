import datetime
from abc import ABC
from off_chain.configuration.db_manager_setting import DatabaseManagerSetting
from off_chain.configuration.log_load_setting import logger
from off_chain.domain.repository.operation_repository import OperationRepository
from off_chain.model.operation_model import OperationModel


class OperationRepositoryImpl(OperationRepository, ABC):
    # Class variable that stores the single instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OperationRepositoryImpl, cls).__new__(cls)
            cls._instance.db_manager_setting = DatabaseManagerSetting()
            logger.info("BackEnd: Successfully initializing the instance for CertificationRepositoryImpl.")
        return cls._instance

    def get_operazioni_ordinate_co2(self, azienda: int) -> list:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda ordinate per co2 consumata """
        query = """
        SELECT Operazione.Id_operazione, Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita, Operazione.Data_operazione, Operazione.Consumo_CO2, Operazione.Operazione
        FROM Operazione JOIN Prodotto
        ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Id_azienda = ?
        ORDER BY Operazione.Consumo_CO2 ASC;
        """
        return self.db_manager_setting.fetch_query(query, (azienda,))

    def get_operazioni_by_data(self, azienda: int, d1: datetime, d2: datetime) -> list:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda filtrate per data """
        query = """
        SELECT Operazione.Id_operazione, Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita, Operazione.Data_operazione, Operazione.Consumo_CO2, Operazione.Operazione
        FROM Operazione JOIN Prodotto
        ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Id_azienda = ?
        AND Operazione.Data_operazione BETWEEN ? AND ?;
        """
        return self.db_manager_setting.fetch_query(query, (azienda, d1, d2))

    def get_operazioni_by_azienda(self, azienda: int) -> list:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda """
        query = """
        SELECT Operazione.Id_operazione, Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita, 
        Operazione.Data_operazione, Operazione.Consumo_CO2, Operazione.Operazione
        FROM Operazione JOIN Prodotto
        ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Id_azienda = ?;
        """
        return self.db_manager_setting.fetch_one(query, (azienda,))

    def inserisci_operazione_azienda_rivenditore(self, azienda: int, prodotto: int, data: datetime, co2: float,
                                                 evento: str):
        """
       Inserts a new operation for a retailer and updates the product status in a single transaction.
       """
        queries = [
            ("""
            INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
            VALUES (?, ?, ?, ?, ?);
                """, (azienda, prodotto, data, co2, evento)),

            ("""
                UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;
                """, (111, prodotto))
        ]

        try:
            self.db_manager_setting.execute_transaction(queries)
        except Exception as e:
            raise Exception(f"Error inserting retailer operation: {str(e)}")

    def inserisci_operazione_azienda_trasformazione(self, azienda: int, prodotto: int, data: datetime, co2: float,
                                                    evento: str, quantita: int = 0,
                                                    materie_prime: str = None):
        """
        Inserts a transformation operation. If the product is a new transformation, it creates a new product record.
        Updates product status and registers composition.
        """
        if materie_prime is None:
            raw_materials = []

        queries = []

        if evento == "Trasformazione":
            # In questo caso, il parametro prodotto è l'id del prodotto che seleziono
            # Inserisci l'operazione
            queries.append((
                """
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
                VALUES (?, ?, ?, ?, ?);
                """,
                (azienda, prodotto[0], data, co2, evento)
            ))
            # Modifica lo stato del prodotto
            queries.append((
                """
                UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;
                """,
                (101, prodotto[0])  # Stato 101: Prodotto trasformato
            ))

        else:
            # In quest'altro caso, invece, il parametro prodotto è il nome del prodotto che seleziono.
            # Questo perché devo creare una nuova istanza di prodotto e mi serve il nome
            # (l'id nella tabella prodotto è autoincrement).
            queries.append((
                """
                INSERT INTO SFS_PRODUCT (name_product, quantity_product, status_product)
                VALUES (?, ?, ?);
                """,
                (prodotto, quantita, 10)  # Stato 10: Prodotto grezzo
            ))

            # Ottieni l'ID del prodotto inserito
            queries.append((
                """
                SELECT last_insert_rowid();
                """,
                ()
            ))

            # Inserisci l'operazione
            queries.append((
                """
                INSERT INTO SFS_OPERATION (id_company, id_product, created_date, 
                co2_footprint, operation_description)
                VALUES (?, last_insert_rowid(), ?, ?, ?);
                """,
                (azienda, data, co2, evento)
            ))

            # Inserisci la composizione
            queries.append((
                """
                INSERT INTO SFS_COMPOSITION (cod_product, cod_raw_material)
                VALUES (last_insert_rowid(), last_insert_rowid());
                """,
                ()
            ))

            for raw_material in raw_materials:
                queries.append((
                    """
                    INSERT INTO SFS_COMPOSITION (cod_product, cod_raw_material)
                    VALUES (last_insert_rowid(), ?);
                    """,
                    (raw_material,)
                ))

                # Modifica lo stato del prodotto
                queries.append((
                    """
                    UPDATE SFS_PRODUCT SET status_product = ? WHERE id_product = ?;
                    """,
                    (110, raw_material)  # Stato 110: Prodotto trasformato
                ))

        try:
            self.db_manager_setting.execute_transaction(queries)
        except Exception as e:
            raise Exception(f"Error inserting transformation operation: {str(e)}")

    def inserisci_operazione_azienda_trasporto(self, azienda: int, prodotto: int, data: datetime, co2: float,
                                               evento: str, nuovo_stato: int):
        """
           Inserts a transport operation and updates the product status.
           If the new status is 11 (Retailer), inserts a record in SFS_COMPOSITION.
           """
        queries = [
            # Insert operation into SFS_OPERATION
            ("""
                    INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
                    VALUES (?, ?, ?, ?, ?);
                    """, (azienda, prodotto, data, co2, evento)),

            # Update product status in SFS_PRODUCT
            ("""
                    UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;
                    """, (nuovo_stato, prodotto))
        ]

        if nuovo_stato == 11:  # If the destination is a retailer
            queries.append((
                """
                INSERT OR IGNORE INTO Composizione VALUES(?, ?)                    
                """, (prodotto, prodotto)
            ))

        try:
            self.db_manager_setting.execute_transaction(queries)
        except Exception as e:
            raise Exception(f"Error inserting transport operation: {str(e)}")

    def inserisci_operazione_azienda_agricola(self, nome: str, quantita: int, azienda: int, data: datetime, co2: float,
                                              evento: str):
        """
        Inserts a new agricultural product and logs the operation.
        """
        queries = [
            # Insert product into SFS_PRODUCT
            ("""
            INSERT INTO Prodotto (Nome, Quantita, Stato) VALUES (?, ?, ?);
            """, (nome, quantita, 0)),  # Status 0: Newly created product

            # Retrieve the last inserted product ID
            ("""
            SELECT last_insert_rowid();
            """, ())
        ]

        # Insert operation into SFS_OPERATION
        queries.append((
            """
            INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione) VALUES (?, ?, ?, ?, ?);
            """,
            (azienda, nome, data, co2, evento)
        ))

        try:
            self.db_manager_setting.execute_transaction(queries)
        except Exception as e:
            raise Exception(f"Error inserting agricultural operation: {str(e)}")
