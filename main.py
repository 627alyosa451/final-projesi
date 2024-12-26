import os
import xml.etree.ElementTree as ET
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Dosya yolları
XML_FILE = "urls.xml"
TXT_FILE = "query_log.txt"

# XML dosyasını oluştur
def create_xml_file():
    if not os.path.exists(XML_FILE):
        root = ET.Element("urls")
        tree = ET.ElementTree(root)
        tree.write(XML_FILE)

# TXT dosyasını oluştur
def create_txt_file():
    if not os.path.exists(TXT_FILE):
        with open(TXT_FILE, "w") as f:
            f.write("Sorgulama Logları:\n")

# URL'yi XML dosyasına kaydet
def add_url_to_xml(name, url):
    if not os.path.exists(XML_FILE):
        create_xml_file()
    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    url_element = ET.SubElement(root, "url")
    name_element = ET.SubElement(url_element, "name")
    name_element.text = name
    link_element = ET.SubElement(url_element, "link")
    link_element.text = url
    tree.write(XML_FILE)

# Sorgulama sonuçlarını TXT dosyasına kaydet
def log_query_to_txt(url, status):
    if not os.path.exists(TXT_FILE):
        create_txt_file()
    with open(TXT_FILE, "a") as f:
        f.write(f"URL: {url}, Durum: {status}\n")

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    url = request.form.get("url")
    add_url_to_xml(name, url)
    return render_template("success.html", name=name)

@app.route("/query")
def query():
    return render_template("query.html")

@app.route("/query_result", methods=["POST"])
def query_result():
    url = request.form.get("url")
    try:
        response = requests.get(url, timeout=5)
        status = f"Erişilebilir! Durum kodu: {response.status_code}"
    except requests.exceptions.RequestException as e:
        status = f"Erişim başarısız: {str(e)}"
    log_query_to_txt(url, status)
    return render_template("query_result.html", url=url, status=status)

if __name__ == "__main__":
    app.run(debug=True)
