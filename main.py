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
    for key, value in data.items():
        element = ET.SubElement(url_element, key)
        element.text = value

    tree.write(XML_FILE, encoding='utf-8', xml_declaration=True)

# TXT dosyasına sorgulama sonuçlarını kaydet
def log_all_queries_to_txt(results):
    create_txt_file()
    with open(TXT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\nSorgulama Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for result in results:
            f.write(f"{result['kaynakAdi']} ({result['kaynakURL']}): {result['status']}\n")

# XML dosyasındaki tüm kayıtları sorgula
def query_all_urls():
    if not os.path.exists(XML_FILE):
        create_xml_file()

    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
    except ET.ParseError:
        return []

    results = []
    for url_element in root.findall("url"):
        kaynakAdi = url_element.find("kaynakAdi").text
        kaynakURL = url_element.find("kaynakURL").text
        try:
            response = requests.get(kaynakURL, timeout=5)
            status = f"Erişilebilir! Durum kodu: {response.status_code}"
        except requests.exceptions.RequestException as e:
            status = f"Erişim başarısız: {str(e)}"
        results.append({"kaynakAdi": kaynakAdi, "kaynakURL": kaynakURL, "status": status})

    return results

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

    return render_template("success.html", data=data)

@app.route("/query_all", methods=["GET"])
def query_all():
    results = query_all_urls()
    log_all_queries_to_txt(results)
    return render_template("query_all.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
