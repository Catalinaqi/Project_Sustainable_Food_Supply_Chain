# pylint: disable=import-error
from configuration.log_load_setting import logger
from domain.exception.authentication_exceptions import PasswordTooShortError, PasswordWeakError
from domain.exception.database_exceptions import UniqueConstraintError, DatabaseError
from domain.exception.login_exceptions import HaveToWaitException, ToManyTryLogEXcepition , LoginFailExetion
from persistence.repository_impl.credential_repository_impl import CredentialRepositoryImpl
from session import Session
from model.company_model import CompanyModel
from model.credential_model import UserModel


class ControllerAutenticazione:

    def __init__(self):
        self.credential = CredentialRepositoryImpl()
        logger.info("BackEnd: Successful initialization of 'class instances' for repository implements")
        self.sessione = Session()

    # Effettua la registrazione
    def registrazione(self, username, password, tipo, indirizzo):
        """Tenta di aggiungere un utente, gestendo eventuali errori."""
        try:
            

            # Inserisce le credenziali e la chiave segreta nel database
            # repo1 = CredentialRepositoryImpl()
            self.credential.register(username, password, tipo, indirizzo)

            # Restituisce il successo insieme alla chiave segreta
            return True, "Utente registrato con successo!"
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

            
            self.sessione.can_log()
            credenziali = self.credential.get_user(username)
            logger.info(f"Username inserito: {username}, Password inserita: {password}")

            if credenziali is not None :
                if credenziali.Password == UserModel.hash_password(password) :
                    try:
                        azienda = self.credential.get_azienda_by_id(credenziali.Id_credential)
                        self.sessione.start_session(azienda)
                        logger.info(f"Username {username} ha eseguito l'accesso")

                    except Exception as e:
                        logger.warning(f"Errore durante la creazione dellla sessione: {str(e)}")
                        return
                    
                
                    return True
            else: 
                raise Exception("qui")
            
        
        except HaveToWaitException as e:  
                raise e
        except  ToManyTryLogEXcepition as e:
                raise e
        except Exception as e:
            logger.warning(f"Errore durante il recupero delle credenziali: {str(e)}")
            logger.info(f"{self.sessione.tentativi}")
            raise LoginFailExetion()
        

    def get_user(self) -> CompanyModel:
        try:
             return self.credential.get_azienda_by_id(Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore nel'ottenimento del utente {e}")
            raise e

    def verifica_password(self,old_password: str) -> bool:
        try:
            return self.credential.verifica_password(old_password,Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Eccezione {e}")
            return False
        
    def cambia_password(self,password : str):
        try:
            self.credential.cambia_password(password,Session().current_user["id_azienda"])
        except Exception as e:
            raise e           