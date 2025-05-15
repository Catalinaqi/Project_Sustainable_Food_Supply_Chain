import unittest
from faker import Faker
from off_chain.configuration.database import Database


class TestRegistrazione(unittest.TestCase):
    """Test della registrazione utenti nel database Credenziali."""

    def setUp(self):
        self.db = Database()
        self.fake = Faker()
        self.test_users = []  # Traccia degli utenti creati per il cleanup

    def _create_fake_user(self):
        """Crea dati fittizi per un utente."""
        username = self.fake.user_name()
        password = self.fake.password(
            length=12,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )
        totp_secret = self.fake.sha256()
        return username, password, totp_secret

    def test_registrazione_successo(self):
        """Verifica che un utente possa registrarsi con successo."""
        username, password, totp_secret = self._create_fake_user()
        self.test_users.append(username)

        self.db.execute_query(
            """
            INSERT INTO Credenziali (Username, Password, totp_secret)
            VALUES (?, ?, ?)
            """,
            (username, password, totp_secret),
        )

        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM Credenziali WHERE Username = ?", (username,)
        )
        self.assertEqual(
            result,
            1,
            f"Registrazione fallita per l'utente {username}.",
        )

    def test_registrazione_username_duplicato(self):
        """Verifica che la registrazione con username duplicato sollevi eccezione."""
        username, password, totp_secret = self._create_fake_user()
        self.test_users.append(username)

        # Inserimento iniziale
        self.db.execute_query(
            """
            INSERT INTO Credenziali (Username, Password, totp_secret)
            VALUES (?, ?, ?)
            """,
            (username, password, totp_secret),
        )

        # Tentativo duplicato
        with self.assertRaises(Exception,\
                                msg="La registrazione con username duplicato non \
                                      ha sollevato un'eccezione."):
            self.db.execute_query(
                """
                INSERT INTO Credenziali (Username, Password, totp_secret)
                VALUES (?, ?, ?)
                """,
                (username, "another_password", "another_secret"),
            )

        count = self.db.fetch_one(
            "SELECT COUNT(*) FROM Credenziali WHERE Username = ?", (username,)
        )
        self.assertEqual(
            count,
            1,
            "Trovato più di un utente con lo stesso username dopo tentativo di registrazione duplicata.",
        )

    def test_registrazione_password_debole(self):
        """Test concettuale per password debole (presume validazione a livello applicativo)."""
        username = self.fake.user_name()
        password_debole = "123"
        totp_secret = self.fake.sha256()
        self.test_users.append(username)

        print(
            f"INFO: Test password debole ({password_debole}) per utente {username} è concettuale e richiede validazione esterna."
        )
        # Placeholder, da implementare se la validazione è gestita a livello applicativo
        pass

    def tearDown(self):
        """Rimuove gli utenti creati durante i test per mantenere pulito il database."""
        if self.test_users:
            placeholders = ", ".join(["?"] * len(self.test_users))
            self.db.execute_query(
                f"DELETE FROM Credenziali WHERE Username IN ({placeholders})",
                tuple(self.test_users),
            )
        self.db.close()


if __name__ == "__main__":
    unittest.main()
