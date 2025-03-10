from dataclasses import dataclass


@dataclass
class UserModel:
    """
    Data Transfer Object (DTO) for user authentication.
    """
    Id_credential: int
    Username: str
    Password: str
    Topt_secret: str
