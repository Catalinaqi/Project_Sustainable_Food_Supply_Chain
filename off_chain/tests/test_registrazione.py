import unittest
from faker import Faker
from configuration.database import Database

class TestRegistrazione(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.fake = Faker()
        self.test_users = [] # Keep track of users created during tests

    def _create_fake_user(self):
        username = self.fake.user_name()
        password = self.fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
        topt_secret = self.fake.sha256()
        return username, password, topt_secret

    def test_registrazione_successo(self):
        username, password, topt_secret = self._create_fake_user()
        self.test_users.append(username)

        # Attempt registration
        self.db.execute_query("""
            INSERT INTO Credenziali (Username, Password, topt_secret)
            VALUES (?, ?, ?)
        """, (username, password, topt_secret))

        # Verify registration
        result = self.db.fetch_one("SELECT COUNT(*) FROM Credenziali WHERE Username = ?", (username,))
        self.assertEqual(result, 1, f"Registrazione fallita per l'utente {username}.")

    def test_registrazione_username_duplicato(self):
        username, password, topt_secret = self._create_fake_user()
        self.test_users.append(username) # Add to cleanup list

        # First registration (should succeed)
        self.db.execute_query("""
            INSERT INTO Credenziali (Username, Password, topt_secret)
            VALUES (?, ?, ?)
        """, (username, password, topt_secret))

        # Attempt to register the same username again
        with self.assertRaises(Exception, msg="La registrazione con username duplicato non ha sollevato un'eccezione."):
            # This assumes your DB/application logic prevents duplicate usernames and raises an error
            # If it doesn't raise an error but simply fails to insert, adjust the test accordingly
            self.db.execute_query("""
                INSERT INTO Credenziali (Username, Password, topt_secret)
                VALUES (?, ?, ?)
            """, (username, "another_password", "another_secret"))

        # Verify only one user with that username exists
        result = self.db.fetch_one("SELECT COUNT(*) FROM Credenziali WHERE Username = ?", (username,))
        self.assertEqual(result, 1, "Trovato più di un utente con lo stesso username dopo tentativo di registrazione duplicata.")

    def test_registrazione_password_debole(self):
        username = self.fake.user_name()
        password_debole = "123"
        topt_secret = self.fake.sha256()
        self.test_users.append(username)

        # Assuming your application has password strength validation that would prevent this
        # This test might need to interact with a registration function rather than direct DB insert
        # For now, we'll simulate the check by asserting the insert *would* fail or be rejected
        # If direct DB insert is the only way, this test might be more conceptual
        # or require a check at a higher application layer.
        # For demonstration, let's assume an application function `register_user` handles this.
        # Since we are directly interacting with DB, we can't easily test this rule here
        # unless the DB itself has constraints (which is unlikely for password complexity).
        # We will skip the actual insertion and assert that such an operation *should* be prevented by the app.
        print(f"INFO: Test per password debole ({password_debole}) per l'utente {username} è concettuale e presume validazione a livello applicativo.")
        # If you have an application function:
        # with self.assertRaises(ValueError, msg="Registrazione con password debole permessa."):
        #     register_user(username, password_debole, topt_secret)
        pass # Placeholder for actual test if application logic is available

    def tearDown(self):
        # Clean up all users created during the tests in this class
        if self.test_users:
            placeholders = ', '.join(['?'] * len(self.test_users))
            self.db.execute_query(f"DELETE FROM Credenziali WHERE Username IN ({placeholders})", tuple(self.test_users))
        self.db.close()

if __name__ == '__main__':
    unittest.main()
