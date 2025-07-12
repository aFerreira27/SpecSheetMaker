from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ProductData import ProductData

def generate_pdf(product_data: ProductData, filename: str):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica", 12)
    # Title
    c.drawString(100, height - 50, f"Spec Sheet for {product_data.prodName}")

    # Product Image
    if product_data.imageLocation:
        c.drawImage(product_data.imageLocation, 100, height - 200, width=200, height=200)

    # Product Details
    y_position = height - 250
    c.drawString(100, y_position, f"SKU: {product_data.sku}")
    y_position -= 20
    c.drawString(100, y_position, f"Series: {product_data.series}")
    # Features
    y_position -= 40
    c.drawString(100, y_position, "Features:")
    for feature in product_data.features:
        y_position -= 20
        c.drawString(120, y_position, f"- {feature}")

    # Specs
    y_position -= 40
    c.drawString(100, y_position, "Specifications:")
    for spec in product_data.specs:
        y_position -= 20
        c.drawString(120, y_position, f"- {spec}")

    # Certifications
    if product_data.certs:
        y_position -= 40
        c.drawString(100, y_position, "Certifications:")
        for cert in product_data.certs:
            y_position -= 20
            c.drawString(120, y_position, f"- {cert}")

    c.save()