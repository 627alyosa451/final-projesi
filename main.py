import os
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

# Dosya yolları
XML_FILE = "urls.xml"
TXT_FILE = "query_log.txt"

# XML dosyasını oluştur
def create_xml_file():
    if not os.path.exists(XML_FILE) or os.stat(XML_FILE).st_size == 0:
        root = ET.Element("urls")
        tree = ET.ElementTree(root)
        tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)

# TXT dosyasını oluştur
def create_txt_file():
    if not os.path.exists(TXT_FILE):
        with open(TXT_FILE, "w", encoding="utf-8") as f:
            f.write("Sorgulama Logları:\n")

# XML dosyasına yeni bir kayıt ekle
def add_url_to_xml(data):
    if not os.path.exists(XML_FILE) or os.stat(XML_FILE).st_size == 0:
        create_xml_file()

    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
    except ET.ParseError:
        create_xml_file()
        tree = ET.parse(XML_FILE)
        root = tree.getroot()

    url_element = ET.SubElement(root, "url")
    for key, value in data.items(): #data sözlüğünden key ve value alma
        element = ET.SubElement(url_element, key)
        element.text = value

    tree.write(XML_FILE, encoding='utf-8', xml_declaration=True) #Verileri kaydetme

# TXT dosyasına sorgulama sonuçlarını kaydet
def log_query_to_txt(name, status):
    create_txt_file()
    with open(TXT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{name}: {status}\n")

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    kaynakID = request.form.get("kaynakID")
    kaynakAdi = request.form.get("kaynakAdi")
    kaynakDetay = request.form.get("kaynakDetay")
    kaynakURL = request.form.get("kaynakURL")
    kaynakZamanDamgasi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = requests.get(kaynakURL, timeout=5)
        status = f"Erişilebilir! Durum kodu: {response.status_code}"
    except requests.exceptions.RequestException as e:
        status = f"Erişim başarısız: {str(e)}"

    data = {
        "kaynakID": kaynakID,
        "kaynakAdi": kaynakAdi,
        "kaynakDetay": kaynakDetay,
        "kaynakURL": kaynakURL,
        "kaynakZamanDamgasi": kaynakZamanDamgasi,
        "status": status
    }
    add_url_to_xml(data)
    log_query_to_txt(kaynakAdi, status)

    return render_template("success.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
