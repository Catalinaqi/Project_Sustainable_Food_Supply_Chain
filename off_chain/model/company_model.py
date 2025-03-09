from dataclasses import dataclass


@dataclass
class CompanyModel:
    """
    Data model for transporting product information between layers.
    """
    Id_azienda: int
    Tipo_azienda: str
    Nome_azienda: str
    Indirizzo: str


    def save(self):
        pass

    @classmethod
    def get_company_emission(cls, company_id):
        pass

