import pyotp
from configuration.log_load_setting import logger
from domain.exception.authentication_exceptions import PasswordTooShortError, PasswordWeakError
from domain.exception.database_exceptions import UniqueConstraintError, DatabaseError
from persistence.repository_impl.credential_repository_impl import CredentialRepositoryImpl
from session import Session
from model.company_model import CompanyModel


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
            credenziali = self.credential.get_user(username)
            logger.info(f"Username inserito: {username}, Password inserita: {password}")
            logger.info(f"Credenziali recuperate: {credenziali}")
        except Exception as e:
            logger.warning(f"Errore durante il recupero delle credenziali: {str(e)}")
            return

        if credenziali is not None :
            if credenziali.Password == password :
                """# Verifica il codice OTP (se presente)
                    if otp_code:
                        totp = pyotp.TOTP(secret_key)
                        if not totp.verify(otp_code):  # Verifica se l'OTP è corretto
                            print('errore')
                            return None  # Se l'OTP non è valido, ritorna None"""
                try:
                    azienda = self.credential.get_azienda_by_id(credenziali.Id_credential)
                    sessione = Session()
                    sessione.start_session(azienda)
                    logger.info(f"Username {username} ha eseguito l'accesso")

                except Exception as e:
                    logger.warning(f"Errore durante la creazione dellla sessione: {str(e)}")
                    return
                
            
                return True
            
        else:
            logger.info(f"Tentativo di login fallito")
            return False

            