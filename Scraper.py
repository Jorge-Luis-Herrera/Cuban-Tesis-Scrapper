from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# 🔐 Configura tu API Key de SerpAPI
API_KEY = "TU_API_KEY"

# 🧠 Palabras clave que queremos encontrar
CLAVES = ["tesis", "maestría", "doctorado"]

# 🔍 Buscar en Google usando SerpAPI
def buscar_en_google():
    params = {
        "engine": "google",
        "q": "site:.cu tesis OR maestría OR doctorado",
        "api_key": API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    enlaces = [r["link"] for r in results.get("organic_results", [])]
    return enlaces

# 🧪 Extraer URLs que contengan las palabras clave
def extraer_urls_con_claves(base_url):
    urls = []
    try:
        html = requests.get(base_url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        for enlace in soup.find_all("a", href=True):
            href = enlace['href']
            texto = enlace.get_text()
            url_completa = urljoin(base_url, href)

            if any(c in href.lower() or c in texto.lower() for c in CLAVES):
                urls.append(url_completa)
    except Exception as e:
        print(f"Error en {base_url}: {e}")
    return urls

# 🧱 Flujo principal
def main():
    urls_google = buscar_en_google()
    urls_finales = []

    for url in urls_google:
        urls_finales.extend(extraer_urls_con_claves(url))

    # 📦 Guardar en archivo JSON
    with open("urls_tesis_cuba.json", "w", encoding="utf-8") as f:
        json.dump(urls_finales, f, indent=2, ensure_ascii=False)

    print(f"✅ Se guardaron {len(urls_finales)} URLs en urls_tesis_cuba.json")

main()
