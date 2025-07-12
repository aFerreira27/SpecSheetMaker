from typing import Dict, Optional, List

from ProductData import ProductData

# In-memory store for products, using SKU as the key
productStore: Dict[str, ProductData] = {}

def addProduct(product: ProductData) -> None:
    """Add or update a product in the store."""
    if not product.sku:
        raise ValueError("Product must have an SKU.")
    productStore[product.sku] = product

def getProduct(sku: str) -> Optional[ProductData]:
    """Retrieve a product by SKU."""
    return productStore.get(sku)

def removeProduct(sku: str) -> None:
    """Remove a product by SKU."""
    productStore.pop(sku, None)

def listProducts() -> List[ProductData]:
    """Return a list of all products."""
    return list(productStore.values())
