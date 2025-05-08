class LoginFailExetion(Exception):
    """Eccezione sollevata quando la quantità disponibile è insufficiente."""
    def __init__(self,):
        super().__init__(f"Login fallito: credenziali errate")

class ToManyTryLogEXcepition(Exception):
    """Eccezione sollevata quando la quantità disponibile è insufficiente."""
    def __init__(self,):
        super().__init__(f"Login fallito: troppi tentativi")
