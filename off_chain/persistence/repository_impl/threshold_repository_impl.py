from abc import ABC

from configuration.database import Database
from configuration.log_load_setting import logger
from domain.repository.threshold_repository import ThresholdRepository
from model.threshold_model import ThresholdModel
from persistence.query_builder import QueryBuilder


class ThresholdRepositoryImpl(ThresholdRepository, ABC):
    # Class variable that stores the single instance

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()
   

    def get_lista_soglie(self, tipo_azienda : str) -> list[ThresholdModel]:
            self.query_builder.select("*").table("Soglie")


            #TODO aggiungere stringhe giuste
            if tipo_azienda == "Agricola":
                self.query_builder.where("Operazione", "=", "Produzione")
                self.query_builder.where("Tipo", "=", "materia prima")
            elif tipo_azienda == "Azienda di trasformazione":
                self.query_builder.where("Tipo", "=", "prodotto finale")
            elif tipo_azienda == "Azienda di trasporto":
                self.query_builder.where("Tipo", "=", "trasporto")
            else:
                logger.error("Tipo di azienda non valido") 
                
            query, value = (self.query_builder.get_query() )

            try:
            
                return [ThresholdModel(*x) for x in self.db.fetch_results(query, value)]
        
            except Exception as e:
               logger.error(f"Errore durante il recupero delle soglie: {e}")
            return []
        
            
    



    def get_prodotti_to_azienda_agricola(self):
        query = """
        SELECT DISTINCT Prodotto FROM Soglie WHERE Tipo = "materia prima";
        """
        lista_finale = []
        for i in self.db_manager_setting.fetch_results(query):
            lista_finale.append(i[0])
        return lista_finale

    def get_prodotti_to_azienda_trasporto(self, destinatario: str) -> list:
        query_to_trasformazione = """
        SELECT Prodotto.Id_prodotto, Prodotto.Nome, Prodotto.Quantita
        FROM Prodotto
        WHERE Prodotto.Stato = 00 OR Prodotto.Stato = 10
        AND Prodotto.Nome IN (
            SELECT Tipo
            FROM Soglie
            WHERE Tipo = "materia prima"
        );
        """
        query_to_rivenditore = """
        SELECT Id_prodotto, Nome, Quantita 
        FROM Prodotto
        WHERE Prodotto.Stato = 00 OR Prodotto.Stato = 10;
        """
        if destinatario == "Azienda di trasformazione":
            return self.db_manager_setting.fetch_results(query_to_trasformazione)
        return self.db_manager_setting.execute_transaction(query_to_rivenditore)

    def get_prodotti_to_azienda_trasformazione(self, id_operation: int) -> list:
        if id_operation == "Trasformazione":
            query = """
            SELECT Id_prodotto, Nome, Quantita FROM Prodotto WHERE Stato = 01;
            """
        else:
            query = """
            SELECT DISTINCT Prodotto FROM Soglie WHERE Tipo = "prodotto finale"
            """
            lista_finale = []
            for i in self.db_manager_setting.fetch_results(query):
                lista_finale.append(i[0])
            return lista_finale
        return self.db_manager_setting.fetch_results(query)

    def get_soglia_by_operazione_and_prodotto(self, operazione: str, prodotto: str) -> int:
        query = """
        SELECT Soglia_Massima FROM Soglie WHERE Operazione = ? AND Prodotto = ?;
        """
        if not self.db_manager_setting.fetch_results(query, (operazione, prodotto)):
            print('non ce')
            return 999
        return self.db_manager_setting.fetch_results(query, (operazione, prodotto))[0][0]
