from model.company_model import CompanyModel
import time
class Session:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Session, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._current_user: CompanyModel = None  # Rende l'attributo privato
        self.logged_in = False
        self.start_app = time.strftime("%Y/%m/%d/%H-%M")
        self.session_start_time = None
        self.session_timeout = 3600
        self.session_token = None

    def start_session(self, user_data: CompanyModel):
        """Avvia una nuova sessione"""
        self._current_user = user_data
        self.logged_in = True
        self.session_start_time = time.time()
        self.session_token = f"token_{int(self.session_start_time)}"
        return self.session_token

    def end_session(self):
        """Termina la sessione e pulisce i dati"""
        self._current_user = None
        self.logged_in = False
        self.session_start_time = None
        self.session_token = None

    def is_authenticated(self):
        """Verifica se la sessione è ancora valida"""
        if not self.logged_in:
            return False
        if self.session_start_time and time.time() - self.session_start_time > self.session_timeout:
            self.end_session()
            return False
        return True

    @property
    def current_user(self):
        """Restituisce una copia sicura dell'utente, senza informazioni sensibili"""
        if self.logged_in:
            return {
                "id": self._current_user.Id_azienda,
                "username": self._current_user.Nome,
                "role": self._current_user.Tipo,
                "id_azienda" : self._current_user.Id_azienda,
                "co2_consumata" : self._current_user.Co2_consumata,
                "co2_compensata" : self._current_user.Co2_compensata,
                "Token": self._current_user.Token

                 # Solo info essenziali
            }
        return None
