import pyotp
from configuration.log_load_setting import logger
from domain.exception.authentication_exceptions import PasswordTooShortError, PasswordWeakError
from domain.exception.database_exceptions import UniqueConstraintError, DatabaseError
from persistence.repository_impl.credential_repository_impl import CredentialRepositoryImpl


class ControllerAutenticazione:

    def __init__(self):
        self.credential = CredentialRepositoryImpl()
        logger.info("BackEnd: Successful initialization of 'class instances' for repository implements")

    # Effettua la registrazione
    def registrazione(self, username, password, tipo, indirizzo):
        """Tenta di aggiungere un utente, gestendo eventuali errori."""
        try:
            # Genera una chiave segreta per l'autenticazione a due fattori
            secret_key = pyotp.random_base32()

            # Inserisce le credenziali e la chiave segreta nel database
            # repo1 = CredentialRepositoryImpl()
            self.credential.inserisci_credenziali_e_azienda(username, password, tipo, indirizzo, secret_key)

            # Restituisce il successo insieme alla chiave segreta
            return True, "Utente registrato con successo!", secret_key
        except PasswordTooShortError as e:
            return False, str(e), None
        except PasswordWeakError as e:
            return False, str(e), None
        except UniqueConstraintError:
            return False, "Errore: Username già esistente.", None
        except DatabaseError:
            return False, "Errore nel database.", None

    # Effettua il login
    def login(self, username, password, otp_code=None):
        try:
            # repo = CredentialRepositoryImpl()
            credenziali = self.credential.get_lista_credenziali()
            logger.info(f"Username inserito: {username}, Password inserita: {password}")
            logger.info(f"Credenziali recuperate: {credenziali}")
            print(f"Credenziali recuperate: {credenziali}")
        except Exception as e:
            logger.warning(f"Errore durante il recupero delle credenziali: {str(e)}")
            return

        if (username, password) not in [(t[1], t[2]) for t in credenziali]:
            return None
        else:
            # Cerca le credenziali dell'utente
            for credenziale in credenziali:
                if credenziale[1] == username and credenziale[2] == password:
                    id_ = credenziale[0]

                    # Recupera l'azienda dell'utente

                    # azienda = CredentialRepositoryImpl.get_azienda_by_id(id_)
                    azienda = self.credential.get_azienda_by_id(id_)

                    # Recupera la chiave segreta OTP per questo utente
                    secret_key = credenziale[3]  # Supponiamo che la chiave segreta OTP sia nel campo 3 dell'azienda

                    # Verifica il codice OTP (se presente)
                    if otp_code:
                        totp = pyotp.TOTP(secret_key)
                        if not totp.verify(otp_code):  # Verifica se l'OTP è corretto
                            print('errore')
                            return None  # Se l'OTP non è valido, ritorna None

                    return azienda[0]  # Se le credenziali e l'OTP sono corretti, ritorna l'azienda dell'utente
