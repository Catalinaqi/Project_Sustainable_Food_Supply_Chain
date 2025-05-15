"""
Modulo per la gestione della sessione utente, implementato come singleton.
Gestisce lo stato di login, il timeout della sessione e i tentativi di accesso.
"""
import time
from typing import Optional, Dict, Any # Aggiunto per type hinting

# Assumiamo che questi import siano corretti e i moduli esistano
# pylint: disable=import-error
# (Disabilita temporaneamente l'errore di import se Pylint non trova i moduli
# durante l'analisi di questo snippet isolato. Rimuovi se i percorsi sono corretti
# nel tuo progetto.)
from model.company_model import CompanyModel
from domain.exception.login_exceptions import (
    HaveToWaitException,
    TooManyLoginAttemptsException, # Corretto il nome dell'eccezione
)
# pylint: enable=import-error

# Definiamo le costanti a livello di modulo o classe
SESSION_TIMEOUT_SECONDS = 3600  # 1 ora
MAX_LOGIN_ATTEMPTS = 6
LOCKOUT_DURATION_SECONDS = 30


class Session:
    """
    Gestore della sessione utente (Singleton).

    Mantiene traccia dell'utente loggato, dei tentativi di login e gestisce
    il timeout della sessione.
    """
    _instance: Optional['Session'] = None # Type hint per _instance

    # R0902: too-many-instance-attributes. Spostando costanti e ottimizzando,
    # cerchiamo di rimanere sotto il limite di default (spesso 7).
    # Se Pylint si lamenta ancora, potrebbe essere necessario valutare se alcuni
    # attributi possono essere raggruppati o se la classe fa troppe cose.
    # Per ora, gli attributi sembrano ragionevoli per una classe Session.

    def __new__(cls) -> 'Session':
        """
        Implementazione del pattern Singleton.
        Restituisce l'istanza esistente o ne crea una nuova.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls) # Python 3 super()
            cls._instance._initialize_session_attributes() # Chiamata al metodo di init
        return cls._instance

    def _initialize_session_attributes(self) -> None:
        """
        Inizializza gli attributi dell'istanza della sessione.
        Chiamato solo una volta durante la creazione dell'istanza singleton.
        """
        self._current_user: Optional[CompanyModel] = None
        self._logged_in: bool = False
        self._session_start_time: Optional[float] = None
        self._session_token: Optional[str] = None

        # Attributi per la gestione dei tentativi di login
        self._login_attempts: int = 0
        self._lockout_release_time: float = 0.0 # Timestamp di quando il lockout termina

        # Timestamp formattato della creazione dell'istanza (se rilevante)
        # Potrebbe essere più un "app_start_time" se l'istanza è globale
        self._instance_creation_time_str: str = time.strftime("%Y/%m/%d/%H-%M")

    def start_session(self, user_data: CompanyModel) -> str:
        """
        Avvia una nuova sessione per l'utente specificato.

        Args:
            user_data: L'oggetto CompanyModel dell'utente che sta effettuando il login.

        Returns:
            Il token di sessione generato.
        """
        self._current_user = user_data
        self._logged_in = True
        self._session_start_time = time.time()
        # Generazione token più robusta potrebbe usare uuid.uuid4().hex
        self._session_token = f"token_{user_data.id_azienda}_{int(self._session_start_time)}"
        self._login_attempts = 0 # Resetta i tentativi al login успешный
        self._lockout_release_time = 0.0 # Resetta il lockout
        return self._session_token

    def end_session(self) -> None:
        """Termina la sessione corrente, resettando gli attributi relativi."""
        self._current_user = None
        self._logged_in = False
        self._session_start_time = None
        self._session_token = None
        # Non resettiamo i tentativi di login qui, sono legati al processo di login,
        # non alla sessione attiva.

    def _increment_login_attempts(self) -> None:
        """Incrementa il contatore dei tentativi di login."""
        self._login_attempts += 1

    def validate_login_attempt(self) -> None:
        """
        Valida se un tentativo di login può procedere.
        Incrementa il contatore dei tentativi e controlla le condizioni di lockout.

        Raises:
            HaveToWaitException: Se l'utente deve attendere a causa di un lockout.
            TooManyLoginAttemptsException: Se l'utente ha superato il numero massimo
                                           di tentativi e viene bloccato.
        """
        current_time = time.time()

        # 1. Controlla se l'utente è attualmente in lockout
        if current_time < self._lockout_release_time:
            seconds_remaining = self._lockout_release_time - current_time
            raise HaveToWaitException(
                f"Account bloccato. Riprova tra {seconds_remaining:.0f} secondi."
            )

        # Se il lockout è scaduto e questo è il primo tentativo dopo,
        # resettiamo _login_attempts PRIMA di incrementarlo per questo nuovo tentativo.
        # Questo previene che un vecchio conteggio alto influenzi il nuovo ciclo.
        if self._login_attempts >= MAX_LOGIN_ATTEMPTS and current_time >= self._lockout_release_time:
            self._login_attempts = 0 # Reset dopo che il lockout è effettivamente terminato

        self._increment_login_attempts() # Incrementa per il tentativo corrente

        # 2. Controlla se questo tentativo supera il limite
        if self._login_attempts >= MAX_LOGIN_ATTEMPTS:
            self._lockout_release_time = current_time + LOCKOUT_DURATION_SECONDS
            # Non è necessario resettare _login_attempts qui,
            # lo faremo al prossimo tentativo se il lockout è scaduto (vedi sopra)
            # o al login successo.
            raise TooManyLoginAttemptsException(
                f"Troppi tentativi di login. Account bloccato per "
                f"{LOCKOUT_DURATION_SECONDS} secondi."
            )
        # Se nessuna eccezione è sollevata, il tentativo può procedere

    def is_authenticated(self) -> bool:
        """
        Verifica se la sessione corrente è autenticata e non scaduta.

        Returns:
            True se l'utente è loggato e la sessione è valida, False altrimenti.
        """
        if not self._logged_in or self._session_start_time is None:
            return False

        if time.time() - self._session_start_time > SESSION_TIMEOUT_SECONDS:
            self.end_session() # Termina la sessione se è scaduta
            return False
        return True

    @property
    def current_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Restituisce un dizionario con informazioni essenziali e sicure
        dell'utente corrente, se autenticato.

        Returns:
            Un dizionario con i dati dell'utente o None se non autenticato.
        """
        if self.is_authenticated() and self._current_user:
            # Assicurati che gli attributi di CompanyModel siano accessibili
            # e abbiano i nomi corretti.
            return {
                "id": self._current_user.id_azienda, # Spesso id_utente è più generico
                "username": self._current_user.nome,
                "role": self._current_user.tipo,
                "company_id": self._current_user.id_azienda,
            }
        return None

    @property
    def logged_in(self) -> bool:
        """Indica se un utente è attualmente loggato."""
        return self._logged_in

    @property
    def instance_creation_time(self) -> str:
        """Restituisce il timestamp formattato della creazione dell'istanza singleton."""
        return self._instance_creation_time_str

# Esempio di utilizzo (opzionale, per testare)
if __name__ == "__main__":
    # pylint: disable=duplicate-code
    # (Disabilita per questo blocco di esempio se hai codice simile altrove per test)
    session1 = Session()
    session2 = Session()
    print(f"Session1 e Session2 sono la stessa istanza: {session1 is session2}")
    print(f"Ora creazione istanza: {session1.instance_creation_time}")

    # Mock CompanyModel per test
    class MockCompanyModel: # pylint: disable=too-few-public-methods
        """Mock per CompanyModel."""
        def __init__(self, id_azienda, nome, tipo):
            self.id_azienda = id_azienda
            self.nome = nome
            self.tipo = tipo

    mock_user = MockCompanyModel(id_azienda="company123", nome="Test User", tipo="admin")

    # Test tentativi di login
    MAX_ATTEMPTS_FOR_TEST = 3 # Usa un numero basso per testare rapidamente
    ORIGINAL_MAX_ATTEMPTS = MAX_LOGIN_ATTEMPTS
    MAX_LOGIN_ATTEMPTS = MAX_ATTEMPTS_FOR_TEST # Sovrascrivi per il test

    print(f"\nInizio test tentativi di login (max {MAX_LOGIN_ATTEMPTS}):")
    for i in range(MAX_LOGIN_ATTEMPTS + 2):
        try:
            print(f"Tentativo {i + 1}: ", end="")
            session1.validate_login_attempt()
            print("OK")
        except HaveToWaitException as e:
            print(f"ERRORE: {e}")
            print(f"Attendo {LOCKOUT_DURATION_SECONDS + 1}s per sbloccare...")
            # time.sleep(LOCKOUT_DURATION_SECONDS + 1) # Rimuovi commento per testare attesa reale
            # Simula il passare del tempo per Pylint e test rapidi
            session1._lockout_release_time = time.time() -1 # pylint: disable=protected-access
            print("...lockout simulato come scaduto.")
        except TooManyLoginAttemptsException as e:
            print(f"ERRORE: {e}")
            # Al prossimo ciclo, dovrebbe scattare HaveToWaitException

    MAX_LOGIN_ATTEMPTS = ORIGINAL_MAX_ATTEMPTS # Ripristina valore originale

    # Test sessione
    if not session1.is_authenticated():
        print("\nUtente non autenticato. Avvio sessione...")
        token = session1.start_session(mock_user)
        print(f"Sessione avviata. Token: {token}")
        print(f"Utente autenticato: {session1.is_authenticated()}")
        user_details = session1.current_user_info
        if user_details:
            print(f"Dettagli utente: {user_details['username']} ({user_details['role']})")

    if session1.is_authenticated():
        print("\nTermino la sessione...")
        session1.end_session()
        print(f"Utente autenticato dopo end_session: {session1.is_authenticated()}")
        print(f"Dettagli utente dopo end_session: {session1.current_user_info}")