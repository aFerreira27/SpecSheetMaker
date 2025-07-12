from flask import Flask, jsonify, request, send_file, render_template
from productStore import addProduct, getProduct, removeProduct, listProducts
from ProductData import ProductData
from SiteScraper import scrapeSite
from PDFMaker import generate_pdf
import os

app = Flask(__name__)
BASE_OUTPUT_FOLDER = 'Output/'

@app.route('/')
def home():
    return 'Spec Sheet Maker API is running.'

@app.route('/products', methods=['GET'])
def get_all_products():
    products = listProducts()
    # Convert ProductData objects to dicts for JSON serialization
    products_dicts = [product.__dict__ for product in products]
    return jsonify(products_dicts)

@app.route('/product/<sku>', methods=['GET'])
def get_product(sku):
    product = getProduct(sku)
    if product:
        return jsonify(product.__dict__)
    return jsonify({'error': 'Product not found'}), 404

@app.route('/product', methods=['POST'])
def add_product():
    data = request.json
    product = ProductData()
    product.prodName = data.get('prodName')
    product.series = data.get('series')
    product.sku = data.get('sku')
    product.imageLocation = data.get('imageLocation')
    product.features = data.get('features', [])
    product.specs = data.get('specs', [])
    product.certs = data.get('certs', [])
    addProduct(product)
    return jsonify({'message': 'Product added/updated.'}), 201

@app.route('/product/<sku>', methods=['DELETE'])
def delete_product(sku):
    removeProduct(sku)
    return jsonify({'message': 'Product removed (if it existed).'}), 200

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    sku = data.get('sku')
    if not sku:
        return jsonify({'error': 'SKU is required.'}), 400
    try:
        prodName, series, prodImagePath, features, certs, specs = scrapeSite('https://krowne.com/', sku)
        product = ProductData()
        product.prodName = prodName
        product.series = series
        product.sku = sku
        product.imageLocation = prodImagePath
        product.features = features
        product.specs = specs
        product.certs = certs
        addProduct(product)
        folder = os.path.join(BASE_OUTPUT_FOLDER, f"{sku.upper()} Spec Sheet Folder")
        os.makedirs(folder, exist_ok=True)
        pdf_path = os.path.join(folder, f"{sku.upper()} Spec Sheet.pdf")
        generate_pdf(product, pdf_path)
        return jsonify({'message': f'PDF created for {sku.upper()}', 'pdf_url': f'/pdf/{sku.upper()}'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ui', methods=['GET', 'POST'])
def ui():
    message = None
    pdf_url = None
    if request.method == 'POST':
        sku = request.form.get('sku')
        if not sku:
            message = '❗ SKU is required.'
        else:
            try:
                prodName, series, prodImagePath, features, certs, specs = scrapeSite('https://krowne.com/', sku)
                product = ProductData()
                product.prodName = prodName
                product.series = series
                product.sku = sku
                product.imageLocation = prodImagePath
                product.features = features
                product.specs = specs
                product.certs = certs
                addProduct(product)
                folder = os.path.join(BASE_OUTPUT_FOLDER, f"{sku.upper()} Spec Sheet Folder")
                os.makedirs(folder, exist_ok=True)
                pdf_path = os.path.join(folder, f"{sku.upper()} Spec Sheet.pdf")
                generate_pdf(product, pdf_path)
                import time
                pdf_url = f"/pdf/{sku.upper()}?t={int(time.time())}"
                message = f'✅ PDF created for {sku.upper()}'
            except Exception as e:
                message = f'❌ Error: {e}'
    return render_template('Pages/index.html', message=message, pdf_url=pdf_url)

@app.route('/pdf/<sku>', methods=['GET'])
def serve_pdf(sku):
    pdf_path = os.path.join(BASE_OUTPUT_FOLDER, f"{sku.upper()} Spec Sheet Folder", f"{sku.upper()} Spec Sheet.pdf")
    if not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF not found'}), 404
    return send_file(pdf_path, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
