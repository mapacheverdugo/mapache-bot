from libs.solotodo.models.price import Price
from libs.solotodo.models.product import Product


class ProductSummary:
    def __init__(self, product: Product, lower_offer_price: Price, lower_normal_price: Price, pricing_history: list[Price]):
        self.product = product
        self.lower_offer_price = lower_offer_price
        self.lower_normal_price = lower_normal_price
        self.pricing_history = pricing_history
