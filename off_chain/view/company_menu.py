from controller.ControllerProduct import ProductController
from controller.ControllerCompany import CompanyController

class Company():
    def __init__(self):
        self.product_controller = ProductController()
        self.company_controller = CompanyController()


    def add_product(self):
            print('You can now insert the information of the product...')
            product_type =  input('Product Type: ')
            company_id = input('Company ID: ')
            name = input('Name: ')
            type = input('Type: ')
            quantity = input('Quantity: ')
            emissions = input('Emissions: ')

            self.product_controller.new_product(product_type, company_id, name, type, quantity, emissions)

            return True

    def see_contract(self):
            product_list = self.product_controller.see_all_products()

            for product in product_list:
                print(product)

            return True

    def check_company_emission(self):
        """Prendere il company id dal login"""
        print("Emissions:" + str(self.company_controller.get_emissions(1)))

        return True
      
    def exit(self):
            return False
    
    def createCompany(self):
         self.company_controller.newCompany("prova1","pippo",100)
         return True

    def company_menu(self):

        options = {
            1: ("Add Product", self.add_product),
            2: ("See Contract", self.see_contract),
            3: ("Check Emissions", self.check_company_emission),
            4: ("Exit", self.exit ),
            100:("create company for test", self.createCompany)
            
        }

        while True:

            for key,value in options.items():
                print(str(key) + "-"+ value[0])

            scelta = input("Scegli un'opzione (1/2/3): ")

            try:
                scelta = int(scelta)
            except ValueError:
                print("Per favore inserisci un numero valido!")
                continue

            if scelta in options:
                if not options[scelta][1]():
                    return False
            else:
                print("Opzione non valida, per favore scegli 1, 2 o 3.")

          


    """
    
        3: "Check Emissions",
        4: "Add Compensatory Action",
        5: "Check Company Emission",
        """