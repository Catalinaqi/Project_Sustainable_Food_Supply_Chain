import unittest
import sqlite3
from faker import Faker
from off_chain.configuration.database import Database


class TestOperazioni(unittest.TestCase):
    """Test per la gestione delle operazioni nel database."""

    def setUp(self):
        self.db = Database()
        self.fake = Faker()
        self.test_data_ids = {
            "credenziali": [],
            "aziende": [],
            "prodotti": [],
            "operazioni": [],  # Identificatori unici Id_lotto per operazioni
        }
        self._crea_dati_prerequisiti()

    def _crea_utente_azienda_prodotto(self):
        """Crea credenziali, azienda e prodotto fittizi e li inserisce nel DB."""
        username_azienda = self.fake.user_name() + "_azienda"
        password_azienda = self.fake.password(length=12)
        totp_secret_azienda = self.fake.sha256()

        self.db.execute_query(
            """
            INSERT OR IGNORE INTO Credenziali (Username, Password, totp_secret)
            VALUES (?, ?, ?)
            """,
            (username_azienda, password_azienda, totp_secret_azienda),
        )
        cred_id = self.db.fetch_one(
            "SELECT Id_credenziali FROM Credenziali WHERE Username = ?",
            (username_azienda,),
        )
        if not cred_id:
            self.fail(f"Creazione/fetch credenziali fallito per {username_azienda}")
        self.test_data_ids["credenziali"].append(username_azienda)

        nome_azienda = self.fake.company() + " TestOp"
        tipo_azienda = self.fake.random_element(
            elements=("Agricola", "Trasportatore", "Trasformatore", "Rivenditore", "Certificatore")
        )
        indirizzo_azienda = self.fake.address()

        self.db.execute_query(
            """
            INSERT INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo)
            VALUES (?, ?, ?, ?)
            """,
            (cred_id, tipo_azienda, nome_azienda, indirizzo_azienda),
        )
        az_id = self.db.fetch_one(
            "SELECT Id_azienda FROM Azienda WHERE Nome = ?", (nome_azienda,)
        )
        if not az_id:
            self.fail(f"Creazione/fetch azienda fallito per {nome_azienda}")
        self.test_data_ids["aziende"].append(nome_azienda)

        nome_prodotto = self.fake.word() + "_prodotto_test"
        stato_prodotto = self.fake.random_int(min=0, max=2)

        self.db.execute_query(
            """
            INSERT INTO Prodotto (Nome, Stato)
            VALUES (?, ?)
            """,
            (nome_prodotto, stato_prodotto),
        )
        prod_id = self.db.fetch_one(
            "SELECT Id_prodotto FROM Prodotto WHERE Nome = ?", (nome_prodotto,)
        )
        if not prod_id:
            self.fail(f"Creazione/fetch prodotto fallito per {nome_prodotto}")
        self.test_data_ids["prodotti"].append(nome_prodotto)

        return az_id, prod_id

    def _crea_dati_prerequisiti(self):
        """Crea i dati base usati dai test."""
        self.az_id_test, self.prod_id_test = self._crea_utente_azienda_prodotto()

    def test_registrazione_operazione_successo(self):
        """Verifica l'inserimento corretto di un'operazione valida."""
        id_lotto = self.fake.random_number(digits=8, fix_len=True)
        consumo_co2 = round(
            self.fake.random_number(digits=3, fix_len=True)
            * self.fake.random_digit_not_null()
            / 10,
            2,
        )
        quantita = self.fake.random_int(min=1, max=1000)
        tipo_operazione = self.fake.random_element(
            elements=("produzione", "trasporto", "vendita")
        )
        self.test_data_ids["operazioni"].append(id_lotto)

        self.db.execute_query(
            """
            INSERT INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                self.az_id_test,
                self.prod_id_test,
                id_lotto,
                consumo_co2,
                quantita,
                tipo_operazione,
            ),
        )

        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM Operazione WHERE Id_lotto = ? AND Id_azienda = ? AND Id_prodotto = ?",
            (id_lotto, self.az_id_test, self.prod_id_test),
        )
        self.assertEqual(
            result,
            1,
            "Operazione non registrata correttamente nel database.",
        )

    def test_registrazione_operazione_azienda_inesistente(self):
        """Verifica che l'inserimento con azienda inesistente fallisca."""
        id_azienda_inesistente = self.fake.random_number(digits=10, fix_len=True)
        id_lotto = self.fake.random_number(digits=8, fix_len=True)
        consumo_co2 = round(
            self.fake.random_number(digits=3, fix_len=True)
            * self.fake.random_digit_not_null()
            / 10,
            2,
        )
        quantita = self.fake.random_int(min=1, max=1000)
        tipo_operazione = "produzione"

        with self.assertRaises(Exception, msg="Inserimento operazione con Id_azienda inesistente non ha sollevato eccezione."):
            self.db.execute_query(
                """
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    id_azienda_inesistente,
                    self.prod_id_test,
                    id_lotto,
                    consumo_co2,
                    quantita,
                    tipo_operazione,
                ),
            )

        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM Operazione WHERE Id_lotto = ?", (id_lotto,)
        )
        self.assertEqual(
            result,
            0,
            "Operazione inserita erroneamente con Id_azienda inesistente.",
        )

    def test_registrazione_operazione_prodotto_inesistente(self):
        """Verifica che l'inserimento con prodotto inesistente sollevi eccezione IntegrityError."""
        id_lotto = self.fake.random_number(digits=8, fix_len=True)
        consumo_co2 = round(
            self.fake.random_number(digits=3, fix_len=True)
            * self.fake.random_digit_not_null()
            / 10,
            2,
        )
        quantita = self.fake.random_int(min=1, max=1000)
        tipo_operazione = "trasporto"
        id_prodotto_inesistente = 999999999  # Id grande per non esistente

        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute_query(
                """
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    self.az_id_test,
                    id_prodotto_inesistente,
                    id_lotto,
                    consumo_co2,
                    quantita,
                    tipo_operazione,
                ),
            )

        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM Operazione WHERE Id_lotto = ?", (id_lotto,)
        )
        self.assertEqual(
            result,
            0,
            "Operazione inserita erroneamente con Id_prodotto inesistente.",
        )

    def tearDown(self):
        """Pulisce il database eliminando i dati creati durante i test."""
        if self.test_data_ids["operazioni"]:
            placeholders = ", ".join(["?"] * len(self.test_data_ids["operazioni"]))
            self.db.execute_query(
                f"DELETE FROM Operazione WHERE Id_lotto IN ({placeholders})",
                tuple(self.test_data_ids["operazioni"]),
            )

        if self.test_data_ids["prodotti"]:
            placeholders = ", ".join(["?"] * len(self.test_data_ids["prodotti"]))
            self.db.execute_query(
                f"DELETE FROM Prodotto WHERE Nome IN ({placeholders})",
                tuple(self.test_data_ids["prodotti"]),
            )

        if self.test_data_ids["aziende"]:
            placeholders = ", ".join(["?"] * len(self.test_data_ids["aziende"]))
            self.db.execute_query(
                f"DELETE FROM Azienda WHERE Nome IN ({placeholders})",
                tuple(self.test_data_ids["aziende"]),
            )

        if self.test_data_ids["credenziali"]:
            placeholders = ", ".join(["?"] * len(self.test_data_ids["credenziali"]))
            self.db.execute_query(
                f"DELETE FROM Credenziali WHERE Username IN ({placeholders})",
                tuple(self.test_data_ids["credenziali"]),
            )

        self.db.close()


if __name__ == "__main__":
    unittest.main()
