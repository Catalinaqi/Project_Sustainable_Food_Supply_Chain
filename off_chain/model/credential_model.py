# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from dataclasses import dataclass
import hashlib
import re

from domain.exception.authentication_exceptions import PasswordTooShortError, PasswordWeakError


@dataclass
class UserModel:
    """
    Data Transfer Object (DTO) for user authentication.
    """
    Id_credential: int
    Username: str
    Password: str
    Topt_secret: str

    def __init__(self,Id_credenziali,Username,Password):
         self.Id_credential = Id_credenziali
         self.Username =Username
         self.Password = Password
         

    @staticmethod
    def validate_password(password : str):
        if len(password) < 8:
                raise PasswordTooShortError("La password deve contenere almeno 8 caratteri!")

        # Controllo complessità con regex
        if not re.search(r'[A-Z]', password):  # Almeno una lettera maiuscola
            raise PasswordWeakError("La password deve contenere almeno una lettera maiuscola.")
        if not re.search(r'[a-z]', password):  # Almeno una lettera minuscola
            raise PasswordWeakError("La password deve contenere almeno una lettera minuscola.")
        if not re.search(r'[0-9]', password):  # Almeno un numero
            raise PasswordWeakError("La password deve contenere almeno un numero.")
        if not re.search(r'\W', password):  # Almeno un carattere speciale
            raise PasswordWeakError("La password deve contenere almeno un carattere speciale (!, @, #, etc.).")
        
    @staticmethod
    def hash_password(password: str) -> str:
        """Restituisce un hash SHA-256 della password."""
        return hashlib.sha256(password.encode()).hexdigest()

