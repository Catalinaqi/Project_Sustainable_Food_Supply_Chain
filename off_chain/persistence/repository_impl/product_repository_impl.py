from abc import ABC
from configuration.database import Database
from configuration.log_load_setting import logger
from domain.repository.product_repository import ProductRepository
from model.materia_prima_model import MateriaPrimaModel
from model.info_product_for_choice_model import ProductForChoiceModel
from model.lotto_composizione_model import Composizione, Lotto
from model.prodotto_finito_cliente import ProdottoFinito
from persistence.query_builder import QueryBuilder


class ProductRepositoryImpl(ProductRepository, ABC):
    """
     Implementing the prodotto repository.
     """
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()

    def get_storico_prodotto(self, prodotto: int) -> list:
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
        return self.db_manager_setting.fetch_results(query, (prodotto,))

    def co2_consumata_prodotti(self, prodotti: [int]) -> list:
        lista_con_co2 = []
        for prodotto in prodotti:
            #repo = ProductRepositoryImpl()
            storico = self.get_storico_prodotto(prodotto[0])
            totale_co2 = sum(t[4] for t in storico)
            lista_con_co2.append((prodotto, totale_co2))
        return lista_con_co2

    

    def get_prodotti_ordinati_co2(self):
        return sorted(self.get_lista_prodotti(), key=lambda x: x[1])

    def get_prodotti_by_nome(self, nome: str) -> list:
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
        return self.db_manager_setting.fetch_results(query, (nome,))

    def get_lista_prodotti_by_rivenditore(self, rivenditore: int) -> list:
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
        return self.db_manager_setting.fetch_results(query, (rivenditore,))

    def get_prodotti_certificati(self) -> list:
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
        #prodotti = self.db_manager_setting.fetch_results(query)
        #logger.info(f"get_prodotti_certificati - prodotti: {prodotti}")
        #if not prodotti:
        #    return []
        #return ProductRepositoryImpl.co2_consumata_prodotti(prodotti)

        result = self.db_manager_setting.fetch_results(query)
        if not result:
            logger.warning("The get_lista_credenziali is empty or the query returned no results.")
        else:
            logger.info(f"Obtained in get_lista_credenziali: {result}")

        #return result
        return self.co2_consumata_prodotti(result)

    def get_prodotti_certificati_by_rivenditore(self, id_rivenditore: int) -> list:
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
        return self.co2_consumata_prodotti(
            self.db_manager_setting.fetch_results(query, (id_rivenditore,)))

    def get_prodotti_certificati_ordinati_co2(self):
        return sorted(self.get_prodotti_certificati(), key=lambda x: x[1])

    def get_prodotti_certificati_by_nome(self, nome: str) -> list:
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
        return self.co2_consumata_prodotti(
            self.db_manager_setting.fetch_results(query, (nome,)))

    def get_prodotti_to_rivenditore(self) -> list:
        query = """
        SELECT Id_prodotto, Nome, Quantita FROM Prodotto WHERE Stato = 11;
        """
        return self.db_manager_setting.fetch_results(query)

    def get_materie_prime(self, azienda: int) -> list:
        query = """
        SELECT Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita
        FROM Prodotto
        JOIN Operazione
        ON Prodotto.Id_prodotto = Operazione.Id_prodotto
        WHERE Operazione.Operazione = "Trasformazione"
        AND Operazione.Id_azienda = ?
        ORDER BY Operazione.Data_operazione DESC;
        """
        return self.db_manager_setting.fetch_results(query, (azienda,))
    




    """ Funzioni definitive"""

    def get_materie_prime_magazzino_azienda(self, id_azienda : int) -> list[MateriaPrimaModel]:
        query, value = (
            self.query_builder
            .select("Prodotto.id_prodotto","Magazzino.id_azienda","Magazzino.quantita", "Prodotto.nome")
            .table("Magazzino")
            .join("Operazione", "Magazzino.id_lotto", "Operazione.id_lotto")
            .join("Prodotto", "Operazione.id_prodotto", "Prodotto.id_prodotto")
            .where("Magazzino.id_azienda", "=", id_azienda)
            .where("Prodotto.stato", "=", 0)  # Stato 0 indica che è una materia prima
            .get_query()
        )

        try:
            logger.info(f"Query in get_materie_prime_magazzino_azienda: {query} - Value: {value}")
            result = self.db.fetch_results(query, value)
        except Exception as e:
            logger.error(f"Error in get_materie_prime_magazzino_azienda: {e}")
            return []

        
        if not result:
            logger.warning("The get_materie_prime_magazzino_azienda is empty or the query returned no results.")
        else:
            logger.info(f"Obtained in get_materie_prime_magazzino_azienda: {result}")
        try:
            return [MateriaPrimaModel(*x) for x in result] if result else [] 
        except Exception as e:
            logger.error(f"Error in converting result to MateriaPrimaModel: {e}")
            return []   
     # Assicurati che il path sia corretto


    def get_prodotti_ordinabili(self) -> list[ProductForChoiceModel]:
        query, value = (
            self.query_builder
            .select("Azienda.Nome","Prodotto.nome","Magazzino.quantita","Azienda.Id_azienda","Prodotto.id_prodotto",  "Operazione.Consumo_CO2")
            .table("Magazzino")
            .join("Operazione", "Magazzino.id_lotto", "Operazione.id_lotto")
            .join("Azienda", "Operazione.id_azienda", "Azienda.id_azienda")
            .where("Azienda.Tipo", "=", "Agricola")
            .join("Prodotto", "Operazione.id_prodotto", "Prodotto.id_prodotto")
            .where("Magazzino.quantita", ">", 0)
            .where("Prodotto.stato", "=", 0)  
            .get_query()
        )

        try:
            logger.info(f"Query in get_prodotti_ordinabili: {query} - Value: {value}")
            result = self.db.fetch_results(query, value)
        except Exception as e:
            logger.error(f"Error in get_prodotti_ordinabili: {e}")
            return []

        
        if not result:
            logger.warning("The get_prodotti_ordinabili is empty or the query returned no results.")
        else:
            logger.info(f"Obtained in get_prodotti_ordinabili: {result}")
        try:
            return [ProductForChoiceModel(*x) for x in result] if result else []
        except Exception as e:
            logger.error(f"Error in converting result to ProductForChoiceModel: {e}")
            return []



# Funzione per caricare un lotto e la sua composizione ricorsiva
    def carica_lotto_con_composizione(self, id_lotto) -> Lotto:
    # 1. Recupero dati dell'operazione (lotto)
        query, value = (
            self.query_builder
            .select("Id_lotto", "Tipo", "quantita", "Consumo_CO2")
            .table("Operazione")
            .where("Id_lotto", "=", id_lotto)
            .get_query()
        )

        try:
            logger.info(f"Query operazione: {query} - Value: {value}")
            rows = self.db.fetch_results(query, value)
            logger.info(f"Result operazione: {rows}")
            if not rows:
                logger.warning(f"Nessuna operazione trovata per id_lotto: {id_lotto}")
                return None
            row = rows[0]
            lotto = Lotto(*row)  # Istanza singola
        except Exception as e:
            logger.error(f"Errore nel recupero dell'operazione: {e}")
            return None

        # 2. Recupero composizioni
        query, value = (
            self.query_builder
            .select("id_lotto_input", "quantità_utilizzata")
            .table("ComposizioneLotto")
            .where("id_lotto_output", "=", id_lotto)
            .get_query()
        )

        try:
            logger.info(f"Query composizione: {query} - Value: {value}")
            rows = self.db.fetch_results(query, value)
            logger.info(f"Result composizione: {rows}")
            composizioni_raw: list[Composizione] = [Composizione(*x) for x in rows] if rows else []
        except Exception as e:
            logger.error(f"Errore nel recupero della composizione: {e}")
            return None

        # 3. Ricorsione per ogni composizione
        for comp in composizioni_raw:
            input_lotto = self.carica_lotto_con_composizione(comp.id_lotto_input)
            composizione = Composizione(
                id_lotto_input=comp.id_lotto_input,
                quantita_utilizzata=comp.quantita_utilizzata,
                lotto_input=input_lotto
            )
            lotto.composizione.append(composizione)

        return lotto
    

    def get_lista_prodotti(self):

        query,value = (
            self.query_builder.select(
                "Prodotto.nome",
                "Operazione.Id_lotto",
                "Azienda.nome",
                "Operazione.Id_prodotto",
            )
            .table("Operazione")
            .join("Azienda", "Operazione.Id_azienda", "Azienda.Id_azienda")
            .join("Prodotto", "Operazione.Id_prodotto", "Prodotto.Id_prodotto")
            .where("Operazione.Tipo", "=", "vendita")
            .get_query()
        )
        
        try:
            # Esegui direttamente il raw SQL (non serve builder qui)
            results = self.db.fetch_results(query, value)
            if results:
                prodotti_co2 = [ProdottoFinito(*r) for r in results]
            
                return prodotti_co2
            else:
                logger.warning("Nessun risultato trovato ")
                return []
        except Exception as e:
            logger.error(f"Errore in calcola_co2_totale_per_prodotti_finiti: {e}")
            return []















    def inserisci_prodotto_trasformato(self,nome_prodotto: str, quantita_prodotta: int, materie_prime_usate: dict , id_azienda: int):
        """
        Salva un prodotto trasformato nel database con le materie prime utilizzate.
        
        :param nome_prodotto: Nome del prodotto trasformato
        :param quantita_prodotta: Quantità del prodotto trasformato
        :param materie_prime_usate: dict con chiave qualsiasi e valore (MateriaPrimaModel, quantita_usata)
        """
        db = Database()

        return

        try:
            queries = []
            composizioni = []

            # 1. Inserisci prodotto trasformato
            query, value = self.query_builder.table("Prodotto").insert(
                nome=nome_prodotto,
                quantita=quantita_prodotta,
                stato=0  # Stato 0 indica che è un prodotto trasformato
            ).get_query()

            queries.append((query, value))

            # 2. Prepara update quantità e composizione
            for _, (materia, quantita_usata) in materie_prime_usate.items():
                # 2a. Diminuisci la quantità di materia prima

                if isinstance(materia, MateriaPrimaModel):
                    materia_id = materia.id

                    query_update_materia, value = (
                        self.query_builder.
                        table("Magazzino")
                        .update(quantita=("quantita - ?",[quantita_usata]))
                        .where("id_azienda", "=", materia.id_azienda)
                        .where("id_prodotto", "=", materia_id)
                        .where("quantita", ">=", quantita_usata)
                        .get_query()
                    )
                    


                queries.append((query_update_materia, value))

                # 2b. Inserimento relazione (da fare dopo che otteniamo l'ID del prodotto)
                composizioni.append((materia.id, quantita_usata))

            # 3. Esegui la transazione iniziale (prodotti + materie prime)
            db.execute_transaction(queries)

            # 4. Recupera l'ID del prodotto inserito
            prodotto_id = db.fetch_one("SELECT MAX(id) FROM Prodotti")



            # 5. Inserisci composizione in tabella intermedia
            for materia_id, quantita_usata in composizioni:
                query_composizione, value = (
                    self.query_builder.
                    table("Composizione_prodotto")
                    .insert(prodotto_id=prodotto_id, materia_id=materia_id, quantita_usata=quantita_usata)
                    .get_query(
                        # Assicurati che il nome della tabella e i campi siano corretti
                    )
                )
                db.execute_query(query_composizione, value)

            # 6. Inserisci operazione di trasformazione
            query_operazione, value = (
                self.query_builder.
                table("Operazione")
                .insert(id_prodotto=prodotto_id, id_azienda = id_azienda, operazione="Trasformazione")
                .get_query()
            )
            db.execute_query(query_operazione, value)


        except Exception as e:
            # Se c'è un errore, rollback dell'intera transazione
            db.conn.rollback()
            raise Exception(f"Errore durante la creazione del prodotto trasformato: {e}")
   

    