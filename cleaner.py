import os
import re
from pathlib import Path
import logging
import time

# Configuración
MD_FOLDER = Path("mds")
CLEANED_FOLDER = Path("mds_limpios")
CLEANING_LOG = "limpieza_log.txt"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('limpieza_errores.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def setup_folders():
    """Crear las carpetas necesarias"""
    os.makedirs(CLEANED_FOLDER, exist_ok=True)
    print(f"📁 Carpeta MD original: {os.path.abspath(MD_FOLDER)}")
    print(f"📁 Carpeta MD limpiados: {os.path.abspath(CLEANED_FOLDER)}")

def get_markdown_files():
    """Obtener lista de archivos Markdown"""
    md_files = []
    for file in os.listdir(MD_FOLDER):
        if file.lower().endswith('.md'):
            md_files.append(file)
    return sorted(md_files)

def log_cleaning(md_file, original_lines, cleaned_lines, issues_fixed):
    """Registrar resultados de la limpieza"""
    with open(CLEANING_LOG, 'a', encoding='utf-8') as f:
        f.write(f"📄 {md_file}\n")
        f.write(f"   Líneas originales: {original_lines}\n")
        f.write(f"   Líneas limpias: {cleaned_lines}\n")
        f.write(f"   Problemas corregidos: {issues_fixed}\n")
        f.write(f"   Reducción: {((original_lines - cleaned_lines) / original_lines * 100):.1f}%\n")
        f.write("-" * 50 + "\n")

def remove_control_characters(text):
    """Eliminar caracteres de control no deseados"""
    # Mantener saltos de línea, tabs y retornos de carro básicos
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    return cleaned

def fix_encoding_issues(text):
    """Corregir problemas comunes de codificación"""
    # Reemplazar caracteres comunes mal decodificados
    replacements = {
        'â€œ': '"',      # Comillas izquierdas
        'â€': '"',      # Comillas derechas  
        'â€˜': "'",      # Comilla simple izquierda
        'â€™': "'",      # Apostrofe/comilla simple derecha
        'â€¦': '...',    # Puntos suspensivos
        'â€"': '—',      # Guión largo
        'â€“': '–',      # Guión medio
        'â€¢': '•',      # Viñeta
        'â€¡': '¡',      # ¡
        'â€º': '»',      # »
        'â€¼': '«',      # «
        'Ã¡': 'á',       # á
        'Ã©': 'é',       # é
        'Ã­': 'í',       # í
        'Ã³': 'ó',       # ó
        'Ãº': 'ú',       # ú
        'Ã±': 'ñ',       # ñ
        'Ã': 'Á',       # Á
        'Ã‰': 'É',       # É
        'Ã': 'Í',       # Í
        'Ã“': 'Ó',       # Ó
        'Ãš': 'Ú',       # Ú
        'Ã‘': 'Ñ',       # Ñ
    }
    
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    
    return text

def normalize_whitespace(text):
    """Normalizar espacios en blanco"""
    # Reemplazar múltiples espacios por uno solo
    text = re.sub(r' +', ' ', text)
    # Reemplazar múltiples saltos de línea por máximo 2
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Eliminar espacios al inicio y final de líneas
    text = '\n'.join(line.strip() for line in text.split('\n'))
    return text

def remove_page_numbers(text):
    """Eliminar números de página"""
    # Patrones comunes de números de página
    patterns = [
        r'^\s*\d+\s*$',                          # Línea con solo número
        r'\n\s*\d+\s*\n',                        # Número solo en línea
        r'Página\s*\d+',                         # "Página X"
        r'Page\s*\d+',                           # "Page X"
        r'\d+\s*/\s*\d+',                        # "X / Y"
        r'-\s*\d+\s*-',                          # "- X -"
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    return text

def fix_headings(text):
    """Arreglar encabezados Markdown"""
    # Detectar líneas que parecen títulos (cortas, sin punto final, mayúsculas)
    lines = text.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Si la línea está en mayúsculas y tiene longitud moderada, podría ser un título
        if (len(stripped) < 100 and 
            stripped.isupper() and 
            len(stripped.split()) > 2):
            # Convertir a formato título (primera letra de cada palabra en mayúscula)
            title_case = ' '.join(word.capitalize() for word in stripped.lower().split())
            cleaned_lines.append(f"## {title_case}")
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def remove_repetitive_content(text):
    """Eliminar contenido repetitivo o basura"""
    # Eliminar líneas que son solo caracteres especiales
    text = re.sub(r'^\s*[^\w\s]+\s*$', '', text, flags=re.MULTILINE)
    
    # Eliminar secuencias repetitivas de caracteres
    text = re.sub(r'(.)\1{5,}', '', text)  # 5+ repeticiones del mismo carácter
    
    # Eliminar URLs largas (a veces se rompen en múltiples líneas)
    text = re.sub(r'http\S+\s+', '', text)
    
    return text

def fix_punctuation(text):
    """Arreglar puntuación"""
    # Espacios antes de puntuación
    text = re.sub(r'\s+([.,;!?])', r'\1', text)
    # Puntuación repetida
    text = re.sub(r'([.,;!?])\1+', r'\1', text)
    # Espacios después de puntuación (excepto si sigue un número o otra puntuación)
    text = re.sub(r'([.,;!?])([A-Za-z])', r'\1 \2', text)
    
    return text

def improve_readability(text):
    """Mejorar la legibilidad general"""
    # Asegurar que los párrafos estén separados por líneas en blanco
    paragraphs = text.split('\n\n')
    cleaned_paragraphs = []
    
    for para in paragraphs:
        if para.strip():  # Solo párrafos no vacíos
            # Unificar el párrafo (eliminar saltos internos)
            unified = ' '.join(para.split())
            cleaned_paragraphs.append(unified)
    
    return '\n\n'.join(cleaned_paragraphs)

def detect_and_remove_boilerplate(text):
    """Detectar y eliminar texto repetitivo de plantillas"""
    # Patrones comunes de texto de plantilla en tesis
    boilerplate_patterns = [
        r'UNIVERSIDAD.*MATANZAS.*',
        r'REPOSITORIO.*INSTITUCIONAL.*',
        r'TESIS.*DE.*(MAESTRÍA|DOCTORADO|GRADO).*',
        r'DIRECTOR.*DE.*TESIS.*',
        r'TUTOR.*ACADÉMICO.*',
        r'JURADO.*CALIFICADOR.*',
        r'MES.*AÑO.*',
        r'©.*COPYRIGHT.*',
        r'Todos los derechos reservados.*',
        r'Esta tesis.*propiedad intelectual.*',
    ]
    
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    return text

def clean_markdown_file(md_path, cleaned_path):
    """Limpiar un archivo Markdown específico"""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        original_lines = len(original_content.split('\n'))
        issues_fixed = 0
        
        # Aplicar todas las transformaciones de limpieza
        content = original_content
        
        # 1. Caracteres de control
        content_before = content
        content = remove_control_characters(content)
        if content != content_before:
            issues_fixed += 1
        
        # 2. Problemas de codificación
        content_before = content
        content = fix_encoding_issues(content)
        if content != content_before:
            issues_fixed += 1
        
        # 3. Espacios en blanco
        content_before = content
        content = normalize_whitespace(content)
        if content != content_before:
            issues_fixed += 1
        
        # 4. Números de página
        content_before = content
        content = remove_page_numbers(content)
        if content != content_before:
            issues_fixed += 1
        
        # 5. Texto repetitivo/plantilla
        content_before = content
        content = detect_and_remove_boilerplate(content)
        if content != content_before:
            issues_fixed += 1
        
        # 6. Contenido repetitivo
        content_before = content
        content = remove_repetitive_content(content)
        if content != content_before:
            issues_fixed += 1
        
        # 7. Puntuación
        content_before = content
        content = fix_punctuation(content)
        if content != content_before:
            issues_fixed += 1
        
        # 8. Encabezados
        content_before = content
        content = fix_headings(content)
        if content != content_before:
            issues_fixed += 1
        
        # 9. Legibilidad
        content_before = content
        content = improve_readability(content)
        if content != content_before:
            issues_fixed += 1
        
        cleaned_lines = len(content.split('\n'))
        
        # Guardar archivo limpio
        with open(cleaned_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, original_lines, cleaned_lines, issues_fixed
        
    except Exception as e:
        logging.error(f"Error limpiando {md_path}: {str(e)}")
        return False, 0, 0, 0

def main():
    """Función principal"""
    print("🧹 INICIANDO LIMPIEZA DE ARCHIVOS MARKDOWN")
    print("=" * 60)
    
    # Configurar carpetas
    setup_folders()
    
    # Obtener lista de archivos
    md_files = get_markdown_files()
    
    if not md_files:
        print("❌ No se encontraron archivos Markdown en la carpeta.")
        return
    
    print(f"📚 Encontrados {len(md_files)} archivos Markdown para limpiar")
    print("=" * 60)
    
    # Inicializar log
    with open(CLEANING_LOG, 'w', encoding='utf-8') as f:
        f.write("LOG DE LIMPIEZA DE MARKDOWN\n")
        f.write("=" * 50 + "\n")
    
    # Estadísticas
    total_files = len(md_files)
    successful_cleanings = 0
    failed_cleanings = 0
    total_issues_fixed = 0
    total_original_lines = 0
    total_cleaned_lines = 0
    
    # Procesar cada archivo
    for i, md_file in enumerate(md_files, 1):
        md_path = os.path.join(MD_FOLDER, md_file)
        cleaned_path = os.path.join(CLEANED_FOLDER, md_file)
        
        print(f"[{i}/{total_files}] 🧹 Limpiando: {md_file}")
        
        success, original_lines, cleaned_lines, issues_fixed = clean_markdown_file(md_path, cleaned_path)
        
        if success:
            print(f"   ✅ Limpiado exitosamente")
            print(f"   📊 Líneas: {original_lines} → {cleaned_lines} ({issues_fixed} problemas)")
            successful_cleanings += 1
            total_issues_fixed += issues_fixed
            total_original_lines += original_lines
            total_cleaned_lines += cleaned_lines
            
            # Registrar en log
            log_cleaning(md_file, original_lines, cleaned_lines, issues_fixed)
        else:
            print(f"   ❌ Error en limpieza")
            failed_cleanings += 1
        
        # Pequeña pausa
        if i < total_files:
            time.sleep(0.1)
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("🎉 LIMPIEZA COMPLETADA")
    print("=" * 60)
    print(f"📊 ESTADÍSTICAS:")
    print(f"   📁 Archivos procesados: {total_files}")
    print(f"   ✅ Limpiezas exitosas: {successful_cleanings}")
    print(f"   ❌ Limpiezas fallidas: {failed_cleanings}")
    print(f"   🔧 Problemas corregidos: {total_issues_fixed}")
    
    if total_original_lines > 0:
        reduction = ((total_original_lines - total_cleaned_lines) / total_original_lines) * 100
        print(f"   📉 Reducción total: {reduction:.1f}%")
    
    print(f"\n📁 Archivos limpios guardados en: {os.path.abspath(CLEANED_FOLDER)}")
    print(f"📋 Log de limpieza: {os.path.abspath(CLEANING_LOG)}")
    print(f"🐛 Log de errores: {os.path.abspath('limpieza_errores.log')}")


main()