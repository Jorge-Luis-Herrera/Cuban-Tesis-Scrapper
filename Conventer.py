#Funciona no tocar, me costo (menos pero igual)
from pathlib import Path
from markitdown import MarkItDown

carpeta_entrada = Path("pdfs")
carpeta_salida = Path("mds")


def procesar_nombre(name: str) -> str:
    print('Procesando el nombre')
    """Genera el nombre destino con extensión .mk a partir de un nombre de archivo."""
    if not name:
        return "documento.md"
    print(f"Generando nombre valido a {name}")
    stem = (str(name).rsplit('.', 1))[0]
    print('Devolviendo el nombre')
    print('')
    return stem + '.md'


def convertir_pdfs():
    print('Empezo la conversion')
    """Convierte todos los PDFs de `carpeta_entrada` a archivos .mk en `carpeta_salida`."""
    i = 0
    mk = MarkItDown()
    for pdf in list(carpeta_entrada.glob("*.pdf")):
        if not pdf.is_file() or pdf.suffix.lower() != '.pdf':
            continue

        print(f'Analizando {pdf.name}')
        print('')
        name = procesar_nombre(pdf.name)
        out_path = carpeta_salida / name
        print(f"Convirtiendo: {pdf} -> {out_path}")
        print('')
        resultado = mk.convert(pdf)
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(str(resultado))
        print(f"Creó el archivo mk número {i}")
        i = i + 1 

print('Empezando el convertidor')
print('')
try:
    convertir_pdfs()
    print('Termino el convertidor')
except Exception as e:
    print(e)