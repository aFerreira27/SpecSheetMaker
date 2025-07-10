import requests
import re
import os
from bs4 import BeautifulSoup
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter


def scrape_data(baseUrl, sku):
    features = None
    specs = None
    certs = None
    series = None

    response = requests.get(baseUrl+sku)
    soup = BeautifulSoup(response.content, 'html.parser')

    h3_tag = soup.find('h3', class_='font-size24')
    prodName = h3_tag.strong.get_text(strip=True) if h3_tag and h3_tag.strong else 'Product Name Not Found'
    print("Product Name:", prodName)

    image_div = soup.find('div', class_='mainProductImage')
    style_attr = image_div.get('style') if image_div else ''
    match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style_attr)
    relative_path = match.group(1) if match else ''
    prodImage_url = baseUrl + relative_path if relative_path else None
    
    folder = f'Output/{sku.upper()} Spec Sheet Folder'
    os.makedirs(folder, exist_ok=True)
    prodImage = f"{sku.upper()}.jpg"
    prodImagePath = os.path.join(folder, prodImage)
    if not prodImage_url:
        print("❌ Image URL not found.")
    else:  
        img_data = requests.get(prodImage_url).content
        with open(prodImagePath, 'wb') as f:
            f.write(img_data)
        print(f"✅ Image saved as: {prodImage}")

    features = []
    ul = soup.find('ul', class_='productDetailInfoList')
    if ul:
        for li in ul.find_all('li'):
            text = li.get_text(strip=True)
            if text:
                features.append(text)

    # Scrape specs from the table under the h3 with class 'font-size24'
    specs = []
    h3 = soup.find('h3', class_='font-size24')
    if h3:
        table = h3.find_next('table')
        if table:
            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    val = cells[1].get_text(strip=True)
                    if key and val:
                        # If the key is 'Series', save to series variable
                        if key.lower() == 'series':
                            series = val
                        else:
                            specs.append((key, val))

    return prodName, series, prodImagePath, features, certs, specs

def merge_with_template(sku):
    template = PdfReader('static/template.pdf')
    overlay = PdfReader(f'Output/{sku.upper()} Spec Sheet Folder/{sku.upper()} Spec Sheet.pdf')
    writer = PdfWriter()

    templatePage = template.pages[0]
    overlayPage = overlay.pages[0]

    # Merge template UNDER overlay so overlay content is always visible
    overlayPage.merge_page(templatePage)
    writer.add_page(overlayPage)

    with open(f'Output/{sku.upper()} Spec Sheet Folder/{sku.upper()} Spec Sheet.pdf', 'wb') as outFile:
        writer.write(outFile)

    print(f"✅ Final PDF saved: {f'Output/{sku.upper()} Spec Sheet Folder/{sku.upper()} Spec Sheet.pdf'}")

def addProdName(pdf,prodName):
    # Auto-resize font to fit width
    max_width = 180  # adjust as needed for your layout
    font_size = 15
    pdf.set_font('HelveticaNeueLTStd-Bd', 'B', font_size)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(18,39)
    while pdf.get_string_width(prodName) > max_width and font_size > 6:
        font_size -= 1
        pdf.set_font('HelveticaNeueLTStd-Bd', 'B', font_size)
    pdf.cell(max_width, 20, prodName, align='L')
def addSeries(pdf,series):
    if series != 'MasterTap':
        pdf.set_font('HelveticaNeueLTStd-Bd', 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(148, 39)
        pdf.cell(50, 20, series, align='R')
    else:
        pdf.image('static/MasterTapLogo.png', x=162, y=46, w=35)
def addProdImage(pdf,prodImage):
    pdf.image(prodImage, x=20, y=60, w=80)
def addFeatures(pdf,features):
    # Title: Standard Features (bold, 12pt)
    pdf.set_font('HelveticaNeueLTStd-Bd', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(120, 53)
    pdf.cell(0, 10, 'Standard Features', ln=1, align='L')
    # Draw horizontal line under title
    y_line = pdf.get_y()-2
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.1)
    pdf.line(120, y_line, 190, y_line)

    pdf.set_font('HelveticaNeueLTStd-Lt', '', 8)
    bullet = u"\u2022"
    x = 120
    y = y_line + 1
    line_height = 4  # Tighter line spacing (was 8)
    for feature in features:
        pdf.set_xy(x, y)
        pdf.cell(0, line_height, f"{bullet} {feature}", ln=1, align='L')
        y += line_height
    
    return len(features)
def addSpecs(pdf,specs, featureCount):
    # Title: Specifications (bold, 12pt)
    pdf.set_font('HelveticaNeueLTStd-Bd', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(120, 70 + featureCount * 3)
    pdf.cell(0, 10, 'Specifications', ln=1, align='L')
    # Draw horizontal line under title (copy spacing from addFeatures)
    y_line = pdf.get_y() - 2
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.1)
    pdf.line(120, y_line, 200, y_line)

    # Table: 2 columns (key, value) with grid lines
    pdf.set_font('HelveticaNeueLTStd-Lt', '', 8)
    x_key = 120
    x_val = 160
    x_end = 200
    y = y_line + 1
    line_height = 5
    row_count = 0
    if specs:
        # Draw vertical lines (column separators)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.25)
        num_rows = len(specs)
        table_top = y
        table_bottom = y + num_rows * line_height
        # Left border
        # pdf.line(x_key, table_top, x_key, table_bottom)
        # Middle border
        pdf.line(x_val, table_top, x_val, table_bottom)

        for spec in specs:
            if isinstance(spec, (list, tuple)) and len(spec) == 2:
                key, val = spec
            elif isinstance(spec, dict):
                key, val = list(spec.items())[0]
            else:
                continue
            # Draw horizontal line above each row (except first)
            if row_count > 0:
                pdf.set_draw_color(0, 0, 0)
                pdf.set_line_width(0.25)
                pdf.line(x_key, y, x_end, y)
            pdf.set_xy(x_key, y)
            pdf.cell(x_val - x_key - 2, line_height, str(key), align='L')
            pdf.set_xy(x_val, y)
            pdf.cell(x_end - x_val, line_height, str(val), align='L')
            y += line_height
            row_count += 1
        # Draw bottom border
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.25)
        pdf.line(x_key, y, x_end, y)
def addCerts(pdf,certs):
    # Title: Certifications (bold, 12pt)
    pdf.set_font('HelveticaNeueLTStd-Bd', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(18, 150)
    pdf.cell(0, 10, 'Certifications:', ln=1, align='L')
    # Draw horizontal line under title (copy spacing from addFeatures)
    y_line = pdf.get_y() - 2
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.1)
    pdf.line(18, y_line, 100, y_line)

    pdf.set_font('HelveticaNeueLTStd-Lt', '', 8)
    bullet = u"\u2022"
    x = 18
    y = y_line + 1
    line_height = 4
    if certs:
        for cert in certs:
            pdf.set_xy(x, y)
            pdf.cell(0, line_height, f"{bullet} {cert}", ln=1, align='L')
            y += line_height
def addDatedReview(pdf,sku):
    # Get page width and height
    page_w = pdf.w
    page_h = pdf.h
    margin = 10
    from datetime import datetime
    date_str = datetime.now().strftime('%m/%Y')
    bullet = u"\u2022"
    # Compose the full string
    full_str = f"{date_str} {bullet} {sku.upper()}"
    # Calculate width for right alignment
    pdf.set_font('HelveticaNeueLTStd-Lt', '', 8)
    date_width = pdf.get_string_width(date_str)
    pdf.set_font('HelveticaNeueLTStd-Bd', 'B', 8)
    bullet_width = pdf.get_string_width(f" {bullet} ")
    sku_width = pdf.get_string_width(sku)
    total_width = date_width + bullet_width + sku_width
    x = page_w - margin - total_width -2
    y = page_h - margin - 15

    # Draw date (right-aligned)
    pdf.set_font('HelveticaNeueLTStd-Lt', '', 8)
    pdf.set_xy(x, y)
    pdf.cell(date_width, 5, date_str, align='R')
    # Draw bullet (right-aligned)
    pdf.set_font('HelveticaNeueLTStd-Bd', 'B', 8)
    pdf.set_xy(x + date_width, y)
    pdf.cell(bullet_width, 5, f" {bullet} ", align='R')
    # Draw SKU (right-aligned)
    pdf.set_font('HelveticaNeueLTStd-Bd', 'B', 8)
    pdf.set_xy(x + date_width + bullet_width, y)
    pdf.cell(sku_width, 5, sku, align='R')
    
def generate_pdf(prodName, series, prodImage, features, certs, specs, sku):
    featureCount = 0

    pdf = FPDF()  # width, height in mm (legal size)
    pdf.add_page()

    pdf.add_font('HelveticaNeueLTStd-Bd', 'B', 'static/fonts/HelveticaNeueLTStd-Bd.ttf')
    pdf.add_font('HelveticaNeueLTStd-Lt', '', 'static/fonts/HelveticaNeueLTStd-Lt.ttf')

    sku = sku.upper()

    addProdName(pdf,prodName)
    addSeries(pdf,series)
    addProdImage(pdf,prodImage)
    if features:
        featureCount = addFeatures(pdf,features)
    if specs:
        addSpecs(pdf,specs, featureCount)
    if certs:
        addCerts(pdf,certs)
    addDatedReview(pdf,sku)
    folder = f'Output/{sku} Spec Sheet Folder'
    os.makedirs(folder, exist_ok=True)
    # ✅ Save the PDF to the folder
    output_path = os.path.join(folder, f'{sku} Spec Sheet.pdf')
    pdf.output(output_path)
    merge_with_template(sku)