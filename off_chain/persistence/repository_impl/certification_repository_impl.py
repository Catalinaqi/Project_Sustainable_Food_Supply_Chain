import datetime
from abc import ABC
#from configuration.log_load_setting import logger
from domain.repository.certification_repository import CertificationRepository
from configuration.database import Database
from persistence.query_builder import QueryBuilder


class CertificationRepositoryImpl(CertificationRepository, ABC):
    """
     Implementing the certificato repository.
     """    


    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()
        

    def get_certifications_by_product_interface(self,id_prodotto: int) -> list:

        query = """
        SELECT 
            Certificato.Id_certificato,
            Prodotto.Nome,
            Certificato.Descrizione,
            Azienda.Nome,
            Certificato.Data
        FROM Certificato
        JOIN Azienda ON Certificato.Id_azienda_certificatore = Azienda.Id_azienda
        JOIN Prodotto ON Certificato.Id_prodotto = Prodotto.Id_prodotto
        WHERE Certificato.Id_prodotto = ?;
        """
        query, value = (self.query_builder
                                .select("Certificato.Id_certificato", "Prodotto.Nome","Certificato.Descrizione",
                                        "Azienda.Nome","Certificato.Data"
                                        ).table("Certificato")
                                        .join("Azienda" , "Certificato.Id_azienda_certificatore", "Azienda.Id_azienda")
                                        .join( "Prodotto",  "Certificato.Id_prodotto" , "Prodotto.Id_prodotto")
                                        .where("Certificato.Id_prodotto", "=",id_prodotto)
                                        .get_query()
        )
        
        return self.db.fetch_results(query, value)
         

    def get_numero_certificazioni(self, id_azienda: int) -> int:
        query, values = (
                self.query_builder
                    .table("Certificato")
                    .select("COUNT(*)")
                    .where("Id_azienda_certificatore", "=", id_azienda)
                    .get_query()
        )
        try:
            return int(self.db.fetch_results(query, values)[0])
        except:
            raise ValueError

    def is_certificato(self, id_prodotto: int) -> bool:
        query, value = (
            self.query_builder 
                    .table("Certificato")
                    .select("*")
                    .where("Id_prodotto","=", id_prodotto)
                    .get_query()
        )
        if not self.db.fetch_results(query, value):
            return False
        return True

    def inserisci_certificato(self, prodotto: int, tipo: str, azienda: int, data: datetime):
        #TODO
        query, values = (
                self.query_builder
                .table("Certificato")
                .insert(Id_prodotto="?", Descrizione="?", Id_azienda_certificatore="?", Data="?")
                .get_query()
        )
        query = """
        INSERT INTO Certificato (Id_prodotto, Descrizione, Id_azienda_certificatore, Data)
        VALUES (?, ?, ?, ?);
        """
        self.db.execute_query(query, (prodotto, tipo, azienda, data))
    # Restituisce la certificazione del prodotto selezionato
    def get_certificazione_by_prodotto(self, prodotto):
        query, values = (
            self.query_builder
                    .select("Certificato.Id_certificato",
                        "Prodotto.Nome",
                        "Certificato.Descrizione",
                        "Azienda.Nome",
                        "Certificato.Data"
                    )
                    .table("Certificato")
                    .join("Azienda", "Certificato.Id_azienda_certificatore", "Azienda.Id_azienda")
                    .join( "Prodotto", "Certificato.Id_prodotto", "Prodotto.Id_prodotto")
                    .where("Certificato.Id_prodotto", "=", prodotto)
                    .get_query()
                    )

        return self.db.fetch_results(query, values)
