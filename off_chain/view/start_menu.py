from controller.ControllerProduct import ProductController
from view.CompanyMenu import Company


class Menu:

    def login(self):
        pass

    def reg(self):
        pass


    def __init__(self):
        self.product_controller = ProductController()
        self.company_menu = Company()
        
        self.options = {
            1: ("Login", self.login),
            2: ("Register", self.reg),
            3: ("Company menu", self.company_menu.company_menu),
            4: ("Close Application", exit)
            
        }

        while True:

            for key,value in self.options.items():
                print(str(key) + "-"+ value[0])

            scelta = input("Scegli un'opzione (1/2/3): ")

            try:
                scelta = int(scelta)
            except ValueError:
                print("Per favore inserisci un numero valido!")
                continue

            if scelta in self.options:
                if not self.options[scelta][1]():
                     continue
                
                
            else:
                print("Opzione non valida, per favore scegli 1, 2 o 3.")



    

        

    