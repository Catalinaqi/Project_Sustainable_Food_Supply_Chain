# pylint: disable=import-error

from configuration.log_load_setting import logger
from domain.exception.authentication_exceptions import PasswordTooShortError, PasswordWeakError
from domain.exception.database_exceptions import UniqueConstraintError, DatabaseError
from domain.exception.login_exceptions import HaveToWaitException, ToManyTryLogEXcepition, LoginFailExetion
from persistence.repository_impl.credential_repository_impl import CredentialRepositoryImpl
from session import Session
from model.company_model import CompanyModel
from model.credential_model import UserModel


class ControllerAutenticazione:
    """Controller per la gestione dell'autenticazione e registrazione degli utenti."""

    def __init__(self):
        self.credential = CredentialRepositoryImpl()
        self.sessione = Session()
        logger.info("BackEnd: Inizializzazione completata dei repository")

    def registrazione(self, username, password, tipo, indirizzo):
        """
        Registra un nuovo utente.

        Returns:
            tuple: (successo: bool, messaggio: str, valore opzionale: None)
        """
        try:
            self.credential.register(username, password, tipo, indirizzo)
            return True, "Utente registrato con successo!", None

        except PasswordTooShortError as exc:
            return False, str(exc), None
        except PasswordWeakError as exc:
            return False, str(exc), None
        except UniqueConstraintError:
            return False, "Errore: Username già esistente.", None
        except DatabaseError:
            return False, "Errore nel database.", None

    def login(self, username, password, otp_code=None):
        """
        Effettua il login di un utente.

        Returns:
            bool: True se il login ha successo

        Raises:
            HaveToWaitException
            ToManyTryLogEXcepition
            LoginFailExetion
        """
        try:
            self.sessione.can_log()
            credenziali = self.credential.get_user(username)
            logger.info("Tentativo login - Username: %s", username)

            if credenziali and credenziali.Password == UserModel.hash_password(password):
                try:
                    azienda = self.credential.get_azienda_by_id(credenziali.Id_credential)
                    self.sessione.start_session(azienda)
                    logger.info("Login effettuato con successo per %s", username)
                    return True
                except Exception as exc:
                    logger.warning("Errore durante la creazione della sessione: %s", str(exc))
                    return False

            raise LoginFailExetion()

        except HaveToWaitException as exc:
            raise exc
        except ToManyTryLogEXcepition as exc:
            raise exc
        except Exception as exc:
            logger.warning("Errore durante il recupero delle credenziali: %s", str(exc))
            logger.info("Tentativi falliti: %s", self.sessione.tentativi)
            raise LoginFailExetion()

    def get_user(self) -> CompanyModel:
        """
        Restituisce l'azienda associata all'utente loggato.

        Returns:
            CompanyModel
        """
        try:
            user_id = Session().current_user["id_azienda"]
            return self.credential.get_azienda_by_id(user_id)
        except Exception as exc:
            logger.error("Errore nel recupero dell'utente: %s", str(exc))
            raise exc

    def verifica_password(self, old_password: str) -> bool:
        """
        Verifica che la password corrente sia corretta.

        Returns:
            bool: True se corretta
        """
        try:
            user_id = Session().current_user["id_azienda"]
            return self.credential.verifica_password(old_password, user_id)
        except Exception as exc:
            logger.error("Errore nella verifica password: %s", str(exc))
            return False

    def cambia_password(self, password: str):
        """
        Cambia la password dell'utente attualmente loggato.
        """
        try:
            user_id = Session().current_user["id_azienda"]
            self.credential.cambia_password(password, user_id)
        except Exception as exc:
            logger.error("Errore durante il cambio password: %s", str(exc))
            raise exc
