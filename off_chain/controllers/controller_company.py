from model.Company import Company

class CompanyController:


    def get_emissions(self,company_id : int):
        return Company.get_company_emission(company_id)
    
    def newCompany(self, name, address, emissions: int):
        company = Company(1,name, address, emissions)
        company.save()