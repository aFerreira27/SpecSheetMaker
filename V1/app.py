from flask import Flask, render_template, request, send_file
import os
from SpecSheetMaker import generate_pdf, scrape_data

app = Flask(__name__)
BASE_OUTPUT_FOLDER = 'Output/'

@app.route('/', methods=['GET', 'POST'])
def index():
    baseUrl = "https://krowne.com/"
    features = None
    specs = None
    certs = None
    series = None
    if request.method == 'POST':
        sku = request.form['sku']
        if not sku:
            return render_template('index.html', message="❗ SKU is required.")
        try:
            prodName, series, prodImage, features, certs, specs = scrape_data(baseUrl, sku)
            generate_pdf(prodName, series, prodImage, features, certs, specs, sku)
            pdf_url = f"/pdf/{sku.upper()}"
            import time
            pdf_url += f"?t={int(time.time())}"
            return render_template('index.html', message=f"✅ PDF created for {sku.upper()}", pdf_url=pdf_url)
        except Exception as e:
            return render_template('index.html', message=f"❌ Error: {e}")
        
    return render_template('index.html')

@app.route('/pdf/<sku>')
def serve_pdf(sku):
    pdf_path = os.path.join(BASE_OUTPUT_FOLDER, f"{sku.upper()} Spec Sheet Folder", f"{sku.upper()} Spec Sheet.pdf")
    if not os.path.exists(pdf_path):
        return "PDF not found", 404
    return send_file(pdf_path, mimetype='application/pdf')

if __name__ == '__main__':

    app.run(debug=True)



