#source /home/austiticleo/School/Cuban-Tesis-Scrapper/venv/bin/activate 
#Funciona no tocar porfavor me costó
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, unquote
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
carpeta = BASE_DIR /  './pdfs/'
url_principal = "https://revistas.reduc.edu.cu/"
headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }
 

def normalize_href(base_url, raw_href):
        """Normaliza y limpia un href extraído del HTML.
        - decodifica percent-encoding
        - separa por comas y elige la parte más específica
        - convierte rutas relativas a absolutas usando `base_url`
        - si la parte parece un dominio sin esquema, antepone 'https://'
        - elimina duplicación del host en el path (ej. https://a.com/a.com/...)"""

        if not raw_href:
                return None
        href = unquote(raw_href).strip()

        # elegir parte entre múltiples separadas por comas
        if ',' in href:
                parts = [p.strip() for p in href.split(',') if p.strip()]
                for p in reversed(parts):
                        if 'index.php' in p or p.lower().startswith('http'):
                                candidate = p
                                break
                if not candidate:
                        candidate = max(parts, key=len)
                href = candidate

        # si no tiene esquema, decidir cómo convertir a absoluto
        if not href.lower().startswith(('http://', 'https://')):
                if re.match(r'^[\w.-]+\.[a-zA-Z]{2,}(/|$)', href):
                        href = 'https://' + href
                else:
                        href = urljoin(base_url, href)

        # eliminar duplicación de host en el path: https://a.com/a.com/path -> https://a.com/path
        parsed = urlparse(href)
        host = parsed.netloc
        path = parsed.path or ''
        # si el path comienza con el host (p.ej. '/revistas.reduc.edu.cu/index...') o sin slash
        stripped_path = path.lstrip('/')
        if stripped_path.startswith(host):
                # quitar la porción duplicada del comienzo
                new_path = stripped_path[len(host):]
                if not new_path.startswith('/'):
                        new_path = '/' + new_path
                rebuilt = parsed._replace(path=new_path)
                href = rebuilt.geturl()
        return href

def extraer_titulo_pdf(soup):
        """Extrae el título de la página HTML y lo limpia.
        
        Si el título comienza con 'Vista de ', lo elimina.
        Devuelve el título limpio o None si no se encuentra."""
        try:
                title_tag = soup.find('title')
                if not title_tag:
                        return None
                titulo = title_tag.get_text().strip()
                # eliminar prefijo 'Vista de ' si existe
                if titulo.lower().startswith('vista de '):
                        titulo = titulo[8:].strip()  # len('Vista de ') = 8
                return titulo if titulo else None
        except Exception:
                return None

def sanitizar_nombre_archivo(nombre):
        """Limpia caracteres problemáticos en el nombre de archivo."""
        # reemplazar caracteres que no son válidos en filenames
        nombre = re.sub(r'[<>:"/\\|?*]', '_', nombre)
        nombre = re.sub(r'\s+', '_', nombre)  # espacios a guiones bajos
        return nombre.strip('_')

def encontrar_botones_descarga(soup):
        """Busca botones de descarga en una página usando múltiples filtros:
        - Elementos <a> con clase 'obj_galley_link pdf'
        - Elementos <a> con atributo rel='bookmark'
        - Elementos <a> con atributo role='button'"""

        botones = []
        # Filtro 1: clase obj_galley_link pdf
        botones.extend(soup.find_all('a', class_='obj_galley_link pdf'))
        
        # Filtro 2: rel=bookmark
        botones.extend(soup.find_all('a', rel='bookmark'))
        
        # Filtro 3: role=button (cualquier etiqueta)
        botones.extend(soup.find_all('a', attrs={'role': 'button'}))
        
        # Deduplicar: usar id() para identificar elementos únicos de BeautifulSoup
        vistos = set()
        resultado = []
        for boton in botones:
                boton_id = id(boton)
                if boton_id not in vistos:
                        vistos.add(boton_id)
                        resultado.append(boton)
        
        return resultado

#Devuelve el cuerpo del enlace url(no tocar esta perfecto)
def abrirenlace(url):
        """Intenta conectar a una URL con reintentos exponenciales."""
        try:
                enlace = requests.get(url, headers=headers, timeout=30)
                enlace.raise_for_status()
                print(f'Se pudo conectar perfecto a {url}')
                print('')
                return BeautifulSoup(enlace.content, 'lxml')
        except requests.exceptions.RequestException as e:
                print(f'Error al conectar a {url}: {e}')
                raise Exception(f'No se pudo conectar a {url} ')
       
#Devuelve una lista de todos los enlaces q hay dentro de de la pagina url_principal
def encontrarenlaces(url):
        soup = abrirenlace(url)
        encontrados = soup.find_all("a", rel='bookmark')
        enlaces = []
        for a in encontrados:
             enlaces.append(a.get('href'))
        print(f'Cantidad de enlaces encontrados {len(enlaces)}')
        print('')
        return enlaces

#Debe descargar todos los pdfs en los subenlaces y guardarlos en la carpeta
def descargar(url):
        realurl = url
        print(f"Analizando: {realurl}")
        print('')
        soup = abrirenlace(url)
        botones_descarga = encontrar_botones_descarga(soup)
        print(f'Cantidad de botones de descarga encontrados: {len(botones_descarga)}')

        # asegurar que la carpeta de salida exista
        os.makedirs(carpeta, exist_ok=True)

        for botones in botones_descarga:
                print('Descargando...')  # 1
                if not botones:
                        continue
                print('Descargando...')  # 2
                raw_href = botones.get('href')
                print(f'Raw href: {raw_href}')
                href = normalize_href(url_principal, raw_href)
                if not href:
                        continue
                print(f'Clean href: {href}')
                soup2 = abrirenlace(href)
                print('Descargando...')  # 3
                enlace = soup2.find('a', class_="download")
                if not enlace:
                        continue
                print('Descargando...')  # 4
                raw_pdf_href = enlace.get('href')
                pdf_href = normalize_href(url_principal, raw_pdf_href)
                if not pdf_href:
                        continue
                # determinar el nombre de archivo destino usando el título de la página
                titulo = extraer_titulo_pdf(soup2)
                if titulo:
                        pdf_name = sanitizar_nombre_archivo(titulo) + '.pdf'
                else:
                        # fallback: usar el nombre derivado de la URL
                        pdf_name = os.path.basename(urlparse(pdf_href).path)
                        if not pdf_name:
                                parsed_href = urlparse(enlace.get('href'))
                                candidate = parsed_href.path.strip('/').split('/')[-1]
                                if candidate:
                                        pdf_name = candidate
                                else:
                                        pdf_name = f"documento_{abs(hash(enlace.get('href')))}.pdf"
                        if not pdf_name.lower().endswith('.pdf'):
                                pdf_name += '.pdf'

                out_path = os.path.join(carpeta, pdf_name)

                # si el archivo ya existe y tiene contenido, saltar la descarga
                try:
                        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                                print(f"Ya existe {out_path}, se salta la descarga.")
                                continue
                except OSError:
                        # en caso de errores al consultar el archivo, proceder a descargar
                        pass

                pdf = requests.get(pdf_href, stream=True, headers=headers)
                if not pdf:
                        continue
                print('Descargando...')  # 5
                pdf.raise_for_status()
                print('Descargando...')  # 6

                with open(out_path, 'wb') as realpdf:
                        for chunk in pdf.iter_content(chunk_size=8192):
                                realpdf.write(chunk)
                print(f'Se descargó correctamente el archivo: {out_path}')

print('Empieza el programa ')
i = 1
for enlace in encontrarenlaces(url_principal):
        print('Empieza la descarga')
        descargar(enlace) 
        print(f'Con exito el {i} enlace')
        i = i + 1 