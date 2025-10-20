import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fpdf import FPDF
import os

def descargar_pdf(url_pdf, nombre_archivo="descargado.pdf"):
    try:
        respuesta = requests.get(url_pdf, timeout=10)
        with open(nombre_archivo, "wb") as f:
            f.write(respuesta.content)
        print(f"✅ PDF descargado: {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error al descargar PDF: {e}")

def guardar_texto_como_pdf(texto, nombre_archivo="contenido_convertido.pdf"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        for linea in texto.split("\n"):
            pdf.multi_cell(0, 10, linea)

        pdf.output(nombre_archivo)
        print(f"📄 Contenido guardado como PDF: {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error al crear PDF: {e}")

def procesar_pagina(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # Buscar enlaces a archivos PDF
        enlaces = soup.find_all("a", href=True)
        for enlace in enlaces:
            href = enlace['href']
            if href.lower().endswith(".pdf"):
                url_pdf = urljoin(url, href)
                descargar_pdf(url_pdf)
                return

        # Si no hay PDF, extraer texto y convertirlo
        texto = soup.get_text(separator="\n", strip=True)
        guardar_texto_como_pdf(texto)

    except Exception as e:
        print(f"❌ Error al procesar la página: {e}")

# Ejemplo de uso
url = "https://repositorio.uci.cu"
procesar_pagina(url)
