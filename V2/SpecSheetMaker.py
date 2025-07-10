from dataclasses import dataclass
class ProductData:
    def __init__(self):
        self.prodName = None
        self.series = None
        self.sku = None
        self.imageLocation = None
        self.features = []
        self.specs = []
        self.certs = []

data = ProductData()