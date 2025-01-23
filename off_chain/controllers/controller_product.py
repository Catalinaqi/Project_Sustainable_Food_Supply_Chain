from model.Product import Product

class ProductController:


    def new_product(self, product_type, company_id, name, type, quantity, emissions):
        product = Product(1,product_type,company_id,name, type, quantity, "today", emissions)
        product.save()

    def see_all_products(self):
        return Product.see_all_products()