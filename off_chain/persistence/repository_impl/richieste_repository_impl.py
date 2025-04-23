from configuration.database import Database
from model.richiesta_model import RichiestaModel
from persistence.query_builder import QueryBuilder
from configuration.log_load_setting import logger


class RichiesteRepositoryImpl():
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.query_builder = QueryBuilder()

    def inserisci_richiesta(self, id_az_richiedente: int,id_az_ricevente: int,id_az_trasporto: int, id_prodotto: int, quantita: int) :
        """
        Inserisce una nuova richiesta di prodotto nel database.
        """
        self.query_builder.table("Richiesta").insert(
            id_richiedente = id_az_richiedente,
            id_ricevente = id_az_ricevente,
            id_trasportatore = id_az_trasporto,
            id_prodotto = id_prodotto,
            quantita = quantita,
            stato_ricevente="In attesa",
            stato_trasportatore="In attesa",

        )
        query, value = self.query_builder.get_query()
        try:
            self.db.execute_query(query, value)
            
        except Exception as e:
            logger.error(f"Errore nell'inserimento della richiesta: {e}", exc_info=True)

    def get_richieste_ricevute(self, id_azienda: int) -> list[RichiestaModel]:
        """
        Restituisce tutte le richieste ricevute da un'azienda.
        """
        query, value = (
            self.query_builder
            .select(
                "r.Id_richiesta",
                "r.Id_richiedente", "rich.Nome AS Nome_richiedente",
                "r.Id_ricevente", "rice.Nome AS Nome_ricevente",
                "r.Id_trasportatore", "tras.Nome AS Nome_trasportatore",
                "r.Id_prodotto", "prod.Nome AS Nome_prodotto",
                "r.Quantita", "r.Stato_ricevente",
                "r.Stato_trasportatore", "r.Data"
            )
            .table("Richiesta AS r")
            .join("Azienda AS rich", "rich.Id_azienda", "r.Id_richiedente")
            .join("Azienda AS rice", "rice.Id_azienda", "r.Id_ricevente")
            .join("Azienda AS tras", "tras.Id_azienda", "r.Id_trasportatore")
            .join("Prodotto AS prod", "prod.Id_prodotto", "r.Id_prodotto")
            .where("r.Id_ricevente", "=", id_azienda)
            .get_query()
        )
        result = self.db.fetch_results(query, value)

        try:
            return [RichiestaModel(*x) for x in result]
        except Exception as e:
            logger.error(f"Errore nel recupero delle richieste ricevute: {e}", exc_info=True)
            return []
        
    def get_richieste_effettuate(self, id_azienda: int) -> list[RichiestaModel]:
        """
        Restituisce tutte le richieste effettuate da un'azienda.
        """
        query, value = (
                self.query_builder
                            .select(
                    "r.Id_richiesta",
                    "r.Id_richiedente", "rich.Nome AS Nome_richiedente",
                    "r.Id_ricevente", "rice.Nome AS Nome_ricevente",
                    "r.Id_trasportatore", "tras.Nome AS Nome_trasportatore",
                    "r.Id_prodotto", "prod.Nome AS Nome_prodotto",
                    "r.Quantita", "r.Stato_ricevente",
                    "r.Stato_trasportatore", "r.Data"
                )
                .table("Richiesta AS r")
                .join("Azienda AS rich", "rich.Id_azienda", "r.Id_richiedente")
                .join("Azienda AS rice", "rice.Id_azienda", "r.Id_ricevente")
                .join("Azienda AS tras", "tras.Id_azienda", "r.Id_trasportatore")
                .join("Prodotto AS prod", "prod.Id_prodotto", "r.Id_prodotto")
                .where("r.Id_richiedente", "=", id_azienda)
                .get_query()
            )
        result = self.db.fetch_results(query, value)

        try:
            if not result:
                logger.info(f"Nessuna richiesta effettuata trovata per l'azienda con ID {id_azienda}.")
                return []
            return [RichiestaModel(*x) for x in result]
        except Exception as e:
            logger.error(f"Errore nel recupero delle richieste effettuate: {e}", exc_info=True)
            return []

            
