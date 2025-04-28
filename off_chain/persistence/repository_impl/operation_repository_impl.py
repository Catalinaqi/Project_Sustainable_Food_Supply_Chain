import datetime
from abc import ABC
from configuration.database import Database
from configuration.log_load_setting import logger
from domain.repository.operation_repository import OperationRepository
from model.operation_model import OperationModel
from model.operation_estesa_model import OperazioneEstesaModel
from persistence.query_builder import QueryBuilder


class OperationRepositoryImpl(OperationRepository, ABC):
    # Class variable that stores the single instance
    

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()
        logger.info("BackEnd: Successfully initializing the instance for OperationRepositoryImpl.")
        

    def get_operazioni_ordinate_co2(self, azienda: int) -> list:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda ordinate per co2 consumata """
        query = """
        SELECT Operazione.Id_operazione, Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita, Operazione.Data_operazione, Operazione.Consumo_CO2, Operazione.Operazione
        FROM Operazione JOIN Prodotto
        ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Id_azienda = ?
        ORDER BY Operazione.Consumo_CO2 ASC;
        """
        return self.db_manager_setting.fetch_results(query, (azienda,))

    def get_operazioni_by_data(self, azienda: int, d1: datetime, d2: datetime) -> list:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda filtrate per data """
        query = """
        SELECT Operazione.Id_operazione, Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita, Operazione.Data_operazione, Operazione.Consumo_CO2, Operazione.Operazione
        FROM Operazione JOIN Prodotto
        ON Operazione.Id_prodotto = Prodotto.Id_prodotto
        WHERE Operazione.Id_azienda = ?
        AND Operazione.Data_operazione BETWEEN ? AND ?;
        """
        return self.db_manager_setting.fetch_results(query, (azienda, d1, d2))

    def get_operazioni_by_azienda(self, azienda: int) -> list[OperazioneEstesaModel]:
        """Restituisce la lista di tutte le operazioni effettuate da una certa azienda """

        query, value = (
            self.query_builder
                .select(
                    "Operazione.Id_operazione",
                    "Prodotto.Id_prodotto",
                    "Prodotto.Nome",
                    "Operazione.Data_operazione",
                    "Operazione.Consumo_CO2",
                    "Operazione.Tipo",
                    "Operazione.quantita",
                )
                .table("Operazione")
                .join("Prodotto", "Operazione.Id_prodotto", "Prodotto.Id_prodotto")
                .where("Operazione.Id_azienda", "=", azienda)
                .get_query()
        )


        try:
            results = self.db.fetch_results(query, value)
            operazioni_estese = [
                    OperazioneEstesaModel(
                        Id_operazione=row[0],
                        Id_prodotto=row[1],
                        Nome_prodotto=row[2],
                        Data_operazione=row[3],
                        Consumo_CO2=row[4],
                        Nome_operazione=row[5],
                        Quantita_prodotto=row[6],                 
            )
            for row in results
            ]

            return operazioni_estese   
        except Exception as e:
            logger.error(f"Error fetching operations by company qui: {e}", exc_info=True)
            return[]
    



    def inserisci_operazione_azienda_rivenditore(self, azienda: int, prodotto: int, data: datetime, co2: float,
                                                 evento: str):
        """
        Inserts a new operation for a retailer and updates the product status in a single transaction.
        """
        query1 = """
            INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
            VALUES (?, ?, ?, ?, ?);
        """
        params1 = (azienda, prodotto, data, co2, evento)

        query2 = """
            UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;
        """
        params2 = (111, prodotto)

        try:
            # Ejecutar ambas consultas dentro de la misma transacción
            self.db_manager_setting.execute_query(query1, params1)
            self.db_manager_setting.execute_query(query2, params2)
        except Exception as e:
            raise Exception(f"BackEnd: inserisci_operazione_azienda_rivenditore: Error inserting retailer operation: {str(e)}")

    def inserisci_operazione_azienda_trasformazione(self, azienda: int, prodotto: [int], data: datetime, co2: float,
                                                    evento: str, quantita: int = 0,
                                                    materie_prime: str = None):
        if materie_prime is None:
            materie_prime = []

        if evento == "Trasformazione":
            # In questo caso, il parametro prodotto è l'id del prodotto che seleziono
            queries = [
                ("""
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
                VALUES (?, ?, ?, ?, ?);
                """, (azienda, prodotto[0], data, co2, evento)),

                ("""
                UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;
                """, (101, prodotto[0]))
            ]

            try:
                self.db_manager_setting.execute_query(queries, multiple=True)
            except Exception as e:
                raise Exception(f"Errore durante l'inserimento: {str(e)}")

        else:
            # In questo caso, il parametro prodotto è il nome del prodotto che seleziono.
            queries = [
                ("""
                INSERT INTO Prodotto (Nome, Quantita, Stato) VALUES (?, ?, ?);
                """, (prodotto, quantita, 10))
            ]

            try:
                self.db_manager_setting.execute_query(queries[0][0], queries[0][1])
                prodotto_id = self.db_manager_setting.cursor.lastrowid  # Ottieni l'ID del prodotto inserito

                queries.extend([
                    ("""
                    INSERT INTO Operazione (Id_azienda, Id_prodotto, Data_operazione, Consumo_CO2, Operazione)
                    VALUES (?, ?, ?, ?, ?);
                    """, (azienda, prodotto_id, data, co2, evento)),

                    ("""
                    INSERT INTO Composizione VALUES(?, ?);
                    """, (prodotto_id, prodotto_id))
                ])

                for mp in materie_prime:
                    queries.append((
                        "INSERT INTO Composizione VALUES(?, ?);", (prodotto_id, mp)
                    ))
                    queries.append((
                        "UPDATE Prodotto SET Stato = ? WHERE Id_prodotto = ?;", (110, mp)
                    ))

                self.db_manager_setting.execute_query(queries, multiple=True)

            except Exception as e:
                raise Exception(f"Errore durante l'inserimento: {str(e)}")

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

        # Esegui tutte le query in un'unica transazione
        self.db_manager_setting.execute_query(queries, multiple=True)
        logger.info(f"Operazione inserita e stato aggiornato con successo per il prodotto {prodotto}.")





    """ Funzionanti"""

    def inserisci_operazione_azienda_agricola(self, nome: str, quantita: int, azienda: int, data: datetime, co2: float):
        """
        Inserts a new agricultural product and logs the operation.
        """
        try:

            query = "INSERT INTO Prodotto (Nome, Stato) VALUES (?, ?)"
            params = (nome, 0)  # Stato 0 indica che il prodotto è in magazzino

            self.db.cur.execute(query, params)
            self.db.conn.commit()
            new_prodotto_id = self.db.cur.lastrowid  # Restituisce l'ID del nuovo prodotto            


            evento = "produzione"
            id_lotto = "PROD" + str(new_prodotto_id)  # Genera un ID lotto unico}
            query, value = (
                self.query_builder.table("Operazione")
                .insert(Id_azienda=azienda, Id_prodotto=new_prodotto_id, Data_operazione=data, Consumo_CO2=co2,
                        Tipo=evento, Id_lotto= id_lotto, quantita=quantita)
                .get_query()
            )
            self.db.execute_query(query, value)

            query, value = (
                self.query_builder.table("Magazzino")
                .insert(Id_azienda=azienda, id_lotto=id_lotto, quantita=quantita)
                .get_query()
            )

            self.db.execute_query(query, value)


            logger.info(f"Prodotto inserito con ID {new_prodotto_id} e operazione registrata con successo.")
        except Exception as e:
            logger.error(f"Errore durante l'inserimento del prodotto: {str(e)}")


    def inserisci_operazione_trasporto(self, id_azienda_trasporto: int,id_lotto_input: int, id_prodotto: int, id_azienda_richiedente: int, id_azienda_ricevente: int, quantita: int, co2_emessa: float):
        """
        Inserts a new transport operation and updates the product status.
        """
        try:
            query = "SELECT IFNULL(MAX(id_lotto_output), 0) + 1 FROM ComposizioneLotto;"
            self.db.execute_query(query)
            result = self.db.fetchone()
            value_output_lotto = result[0] if result else 1
            query = "INSERT INTO ComposizioneLotto (id_lotto_output,id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)"
            params = (value_output_lotto, id_lotto_input, quantita)  # Stato 0 indica che il prodotto è in magazzino

            self.db.cur.execute(query, params)
            self.db.conn.commit()
            lotto_output = self.db.cur.lastrowid



            query = "INSERT INTO Operazione (Id_azienda,Id_prodotto,Id_lotto, Quantita, Consumo_CO2, tipo) VALUES (?, ?, ?, ?, ?, ?)"
            params = (id_azienda_trasporto,id_prodotto, lotto_output, quantita, co2_emessa,"trasporto")

            self.db.cur.execute(query, params)
            self.db.conn.commit()
            logger.info(f"Operazione di trasporto inserita con successo.")


            #TODO Aggionare magazzino


        except Exception as e:
            logger.error(f"Errore durante l'inserimento dell'operazione di trasporto: {str(e)}")


    
