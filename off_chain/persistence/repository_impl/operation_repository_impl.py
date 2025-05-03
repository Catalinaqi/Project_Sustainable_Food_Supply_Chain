import datetime
from abc import ABC
import sqlite3
from configuration.database import Database
from configuration.log_load_setting import logger
from domain.repository.operation_repository import OperationRepository
from model.operation_model import OperationModel
from model.operation_estesa_model import OperazioneEstesaModel
from off_chain.model.materia_prima_model import MateriaPrimaModel
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
                                                 evento: str, id_lotto_input: int, quantita : int):
        """
        Inserts a new operation for a retailer and updates the product status in a single transaction.
        """
        try:
        

            
            value_output_lotto = self.get_next_id_lotto_output()
            query = "INSERT INTO ComposizioneLotto (id_lotto_output,id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)"
            params = (value_output_lotto,id_lotto_input,quantita)

            self.db.execute_query(query,params)
            
            query = """
                INSERT INTO Operazione (Id_azienda, Id_prodotto,Id_lotto, Data_operazione, Consumo_CO2, Tipo,quantita)
                VALUES (?, ?, ?, ?, ?,?,?);
            """
            params = (azienda, prodotto,value_output_lotto, data, co2, evento,quantita)

            self.db.execute_query(query,params)

            

            # Aggiornare Magazzino
            query = "UPDATE Magazzino SET quantita = quantita - ? WHERE Id_azienda = ? AND Id_lotto = ?"
            params = (quantita,azienda,id_lotto_input)

            self.db.execute_query(query,params)

        
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
            
            value_output_lotto = self.get_next_id_lotto_output()
            
            query = "INSERT INTO ComposizioneLotto (id_lotto_output,id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)"
            params = (value_output_lotto, id_lotto_input, quantita)  

        


            self.db.execute_query(query, params)
            

        except Exception as e:
                    logger.error(f"composizione {e}")
        
        try:

            query = "INSERT INTO Operazione (Id_azienda,Id_prodotto,Id_lotto, Quantita, Consumo_CO2, tipo) VALUES (?, ?, ?, ?, ?, ?)"
            params = (id_azienda_trasporto,id_prodotto, value_output_lotto, quantita, co2_emessa,"trasporto")

            self.db.execute_query(query, params)
            #self.db.conn.commit()
            logger.info(f"Operazione di trasporto inserita con successo.")

        except Exception as e:
                    logger.error(f"composizione {e}")
        
        try:

            query = "INSERT INTO Magazzino(id_azienda,id_lotto,quantita) VALUES(?,?,?)"
            params = (id_azienda_richiedente,value_output_lotto,quantita)

            self.db.execute_query(query, params)
            #self.db.conn.commit()

        except Exception as e:
                    logger.error(f"composizione {e}")
        
        try:


            

    # Verifica quantità disponibile
            quantita_disponibile = self.db.fetch_one("SELECT quantita FROM Magazzino WHERE id_lotto = ?", (id_lotto_input,))
             

            if quantita_disponibile is None:
                raise Exception(f"{id_lotto_input} non trovato")

           

            if quantita_disponibile < quantita:
                raise Exception( f"Quantità insufficiente: disponibile {quantita_disponibile}, richiesta {quantita}.")

    # Aggiornamento
            self.db.execute_query("""
                UPDATE Magazzino
                SET quantita = quantita - ?
                WHERE id_lotto = ?;
            """, (quantita, id_lotto_input))

            #self.db.conn.commit()
            logger.info( f"Aggiornamento riuscito: {quantita} sottratti dal lotto {id_lotto_input}.")



        except Exception as e:
            logger.error(f"Errore durante l'inserimento dell'operazione di trasporto: {str(e)}")


    def inserisci_prodotto_trasformato(self,nome_prodotto: str, quantita_prodotta: int, materie_prime_usate: dict , id_azienda: int, co2_consumata : int):
        """
        Salva un prodotto trasformato nel database con le materie prime utilizzate.
        
        :param nome_prodotto: Nome del prodotto trasformato
        :param quantita_prodotta: Quantità del prodotto trasformato
        :param materie_prime_usate: dict con chiave qualsiasi e valore (MateriaPrimaModel, quantita_usata)
        """


        try:
            queries = []
            composizioni = []

            # 1. Inserisci prodotto trasformato
            query, params = (
                self.query_builder.table("Prodotto").insert(
                    nome=nome_prodotto,
                    stato=1
                ).get_query()
            )
            queries.append((query, params))



            # 2. Prepara update quantità e composizione
            for _, (materia, quantita_usata) in materie_prime_usate.items():
                # 2a. Diminuisci la quantità di materia prima

                if isinstance(materia, MateriaPrimaModel):

                    query_update_materia, value = (
                        self.query_builder.
                        table("Magazzino")
                        .update(quantita=("quantita - ?",[quantita_usata]))
                        .where("id_azienda", "=", materia.id_azienda)
                        .where("quantita", ">=", quantita_usata)
                        .get_query()
                    )
                    


                queries.append((query_update_materia, value))
                composizioni.append((materia.id_prodotto, quantita_usata))


            # 3 Creo la composizione del lotto 
            value_output_lotto = self.get_next_id_lotto_output()
            


            for _, (materia, quantita_usata) in materie_prime_usate.items():
                if isinstance(materia, MateriaPrimaModel):
                    query_comp = "INSERT INTO ComposizioneLotto (id_lotto_output,id_lotto_input, quantità_utilizzata) VALUES (?, ?, ?)"
                    params = (value_output_lotto, materia.id_lotto, quantita_usata)

                    queries.append((query_comp, params))



            # 3. Esegui la transazione iniziale (prodotti + materie prime)
            self.db.execute_transaction(queries)




            # 4. Recupera l'ID del prodotto inserito
            prodotto_id = self.db.fetch_one("SELECT MAX(Id_prodotto) FROM Prodotto")



            # 6. Inserisci operazione di trasformazione
            query_operazione, value = (
                self.query_builder.
                table("Operazione")
                .insert(id_prodotto=prodotto_id,
                        id_azienda = id_azienda,
                        Tipo ="trasformazione",
                        Id_lotto = value_output_lotto,
                        Consumo_CO2 = co2_consumata,
                        quantita = quantita_prodotta)
                .get_query()
            )
    
                
            self.db.execute_query(query_operazione, value)

        except sqlite3.IntegrityError as e:
                print("IntegrityError:", e)
                self.db.conn.rollback()

        except Exception as e:
            # Se c'è un errore, rollback dell'intera transazione
            self.db.conn.rollback()
            raise Exception(f"Errore durante la creazione del prodotto trasformato: {e}")


    def get_next_id_lotto_output(self):
         try:
            result = self.db.fetch_one("SELECT IFNULL(MAX(id_lotto_output), 0) + 1 FROM ComposizioneLotto;")
            value_output_lotto = result or 1
            return value_output_lotto
         except Exception as e:
              raise ValueError("Erroe nell'ottenimento del nuovo id lotto")
         