import datetime
from abc import ABC
import sqlite3
from configuration.database import Database
from configuration.log_load_setting import logger
from domain.repository.operation_repository import OperationRepository
from model.operation_model import OperationModel
from model.operation_estesa_model import OperazioneEstesaModel
from model.materia_prima_model import MateriaPrimaModel
from persistence.query_builder import QueryBuilder
from persistence.repository_impl.integrity_utils import firma_dati, verifica_firma


class OperationRepositoryImpl(ABC):
    # Class variable that stores the single instance
    

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()
        logger.info("BackEnd: Successfully initializing the instance for OperationRepositoryImpl.")
        

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


    """ Funzionanti"""

    def inserisci_operazione_azienda_agricola(self, id_tipo_prodotto: int, descrizione : str, quantita: int, azienda: int, data: datetime, co2: float):
        """
        Inserts a new agricultural product and logs the operation.
        """
        try:

            tipo_evento = "produzione"
            id_lotto = self.get_next_id_lotto_output
            query, value = (
                self.query_builder.table("Operazione")
                .insert(Id_azienda=azienda, Id_prodotto=id_tipo_prodotto, Data_operazione=data, Consumo_CO2=co2,
                        Tipo=tipo_evento, Id_lotto= id_lotto, quantita=quantita)
                .get_query()
            )
            self.db.execute_query(query, value)

            query, value = (
                self.query_builder.table("Magazzino")
                .insert(Id_azienda=azienda, id_lotto=id_lotto, quantita=quantita)
                .get_query()
            )

            self.db.execute_query(query, value)

            logger.info(f"Operazione registrata con successo.")
            #print(f"la soglia del prod farina è {str(self.recupera_soglia(tipo_evento,id_tipo_prodotto))}")
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


    def inserisci_prodotto_trasformato(self,id_tipo_prodotto: int, descrizione : str, quantita_prodotta: int, materie_prime_usate: dict , id_azienda: int, co2_consumata : int):
        """
        Salva un prodotto trasformato nel database con le materie prime utilizzate.
        
        :param nome_prodotto: Nome del prodotto trasformato
        :param quantita_prodotta: Quantità del prodotto trasformato
        :param materie_prime_usate: dict con chiave qualsiasi e valore (MateriaPrimaModel, quantita_usata)
        """

        try:
            queries = []
            composizioni = []
            tipo_evento = "trasformazione"

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

            # Aggiungo nuovo lotto al magazzino
            query_magazzino = " INSERT OR IGNORE INTO Magazzino (id_azienda, id_lotto, quantita) VALUES (?, ?,?)"
            value = (id_azienda,value_output_lotto,quantita_prodotta)
            queries.append((query_magazzino, value))

            # 3. Esegui la transazione iniziale (prodotti + materie prime)
            self.db.execute_transaction(queries)
            

            # 6. Inserisci operazione di trasformazione
            query_operazione, value = (
                self.query_builder.
                table("Operazione")
                .insert(id_prodotto=id_tipo_prodotto,
                        id_azienda = id_azienda,
                        Tipo =tipo_evento,
                        Id_lotto = value_output_lotto,
                        Consumo_CO2 = co2_consumata,
                        quantita = quantita_prodotta)
                .get_query()
            )
    
                
            self.db.execute_query(query_operazione, value)

            #return self.recupera_soglia(tipo_evento ,id_tipo_prodotto)

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
         

    

    def salva_soglia(self,tipo_operazione: str, id_prodotto: int, soglia_massima: int):
        payload = {
            "tipo_operazione": tipo_operazione,
            "id_prodotto": id_prodotto,
            "soglia_massima": soglia_massima,
            
        }

        firma = firma_dati(payload)

        # Salva su DB insieme alla firma
        self.db.execute_query("""
            INSERT INTO Soglie (Operazione,Prodotto, Soglia_Massima, firma) VALUES (?, ?, ?, ?)
        """, (tipo_operazione, id_prodotto, soglia_massima, firma))




    def recupera_soglia(self, tipo_operazione: str, id_prodotto: int):
        result = self.db.fetch_results("""
            SELECT Operazione, Prodotto, Soglia_Massima, firma FROM Soglie WHERE Operazione = ? AND Prodotto = ?
        """, (tipo_operazione, id_prodotto))

        if not result:
            raise ValueError("Soglia non trovata.")

        tipo_operazione, id_prodotto, soglia_massima, firma = result[0]
        
        # Assicurati che i tipi siano coerenti con quelli usati nella firma originale
        payload = {
            "tipo_operazione": tipo_operazione,
            "id_prodotto": id_prodotto,
            "soglia_massima": soglia_massima,
        }

        if not verifica_firma(payload, signature=firma):
            raise ValueError("Dati soglia corrotti o manomessi!")

        return soglia_massima

    
            


         