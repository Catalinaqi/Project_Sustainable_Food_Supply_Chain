from abc import ABC
from configuration.db_manager_setting import DatabaseManagerSetting
from configuration.log_load_setting import logger
from domain.repository.product_repository import ProductRepository


class ProductRepositoryImpl(ProductRepository, ABC):
    """
     Implementing the prodotto repository.
     """
    # Class variable that stores the single instance
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProductRepositoryImpl, cls).__new__(cls)
            cls._instance.db_manager_setting = DatabaseManagerSetting()
            logger.info("BackEnd: Successfully initializing the instance for ProductRepositoryImpl.")
        return cls._instance

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
        return self.db_manager_setting.fetch_query(query, (prodotto,))

    def co2_consumata_prodotti(self, prodotti: [int]) -> list:
        lista_con_co2 = []
        for prodotto in prodotti:
            #repo = ProductRepositoryImpl()
            storico = self.get_storico_prodotto(prodotto[0])
            totale_co2 = sum(t[4] for t in storico)
            lista_con_co2.append((prodotto, totale_co2))
        return lista_con_co2

    def get_lista_prodotti(self) -> list:
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
            WHERE Operazione.Operazione = "Messo sugli scaffali";        
        """
        return self.co2_consumata_prodotti(self.db_manager_setting.fetch_query(query))

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
        return self.db_manager_setting.fetch_query(query, (nome,))

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
        return self.db_manager_setting.fetch_query(query, (rivenditore,))

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
        #prodotti = self.db_manager_setting.fetch_query(query)
        #logger.info(f"get_prodotti_certificati - prodotti: {prodotti}")
        #if not prodotti:
        #    return []
        #return ProductRepositoryImpl.co2_consumata_prodotti(prodotti)

        result = self.db_manager_setting.fetch_query(query)
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
            self.db_manager_setting.fetch_query(query, (id_rivenditore,)))

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
            self.db_manager_setting.fetch_query(query, (nome,)))

    def get_prodotti_to_rivenditore(self) -> list:
        query = """
        SELECT Id_prodotto, Nome, Quantita FROM Prodotto WHERE Stato = 11;
        """
        return self.db_manager_setting.fetch_query(query)

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
        return self.db_manager_setting.fetch_query(query, (azienda,))
