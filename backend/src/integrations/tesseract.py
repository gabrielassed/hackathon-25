from pathlib import Path
from typing import List

from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image, ImageOps
from unidecode import unidecode

def extract_text_native(pdf_path: str) -> List[str]:
    """Extrai texto nativo com pypdf, uma string por página."""
    reader = PdfReader(pdf_path)
    texts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        texts.append(txt)
    return [unidecode(line).strip() for line in '\n'.join(texts).splitlines()]

def ocr_page_image(image: Image.Image, lang: str = "por") -> str:
    gray = ImageOps.grayscale(image)
    content = pytesseract.image_to_string(gray, lang=lang)
    return [unidecode(line).strip() for line in content.splitlines()]

def hybrid_pdf_to_text(
    pdf_path: str,
    min_chars_per_page: int = 50,   # limiar para considerar que “tem texto”
    dpi: int = 300,                 # resolução para o OCR
    lang: str = "por"               # idioma do tesseract (instale o pacote do idioma)
) -> str:
    """
    Tenta texto nativo primeiro; se a página tiver pouco texto, faz OCR só nela.
    Retorna o texto completo (todas as páginas).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    # 1) Extrair texto nativo
    native_texts = extract_text_native(str(pdf_path))

    # 2) Descobrir quais páginas precisam de OCR
    pages_needing_ocr = [i for i, t in enumerate(native_texts) if len(t.strip()) < min_chars_per_page]

    # 3) Se nenhuma precisa, retorna o nativo
    if not pages_needing_ocr:
        # Formata com cabeçalho por página
        out = []
        for i, t in enumerate(native_texts, start=1):
            out.append(f"\n\n=== Página {i} (texto nativo) ===\n{t}")
        return "".join(out)

    # 4) Converter apenas as páginas que precisam de OCR para imagem
    #    convert_from_path usa numeração base 1 em `first_page`/`last_page`, 
    #    então vamos converter um intervalo contínuo por vez para eficiência.
    #    Para simplificar, converteremos todas as páginas e só OCR nas necessárias.
    images = convert_from_path(str(pdf_path), dpi=dpi)

    # 5) Montar saída final, escolhendo nativo ou OCR por página
    out_pages = []
    for idx, (txt_native, img) in enumerate(zip(native_texts, images), start=1):
        if (idx - 1) in pages_needing_ocr:
            txt_ocr = ocr_page_image(img, lang=lang)
            out_pages.append(f"\n\n=== Página {idx} (OCR) ===\n{txt_ocr}")
        else:
            out_pages.append(f"\n\n=== Página {idx} (texto nativo) ===\n{txt_native}")

    return "".join(out_pages)

def extract_text_ocr(filepath):
    images = convert_from_path(filepath)

    texts = [
        ocr_page_image(image) for image in images
    ]
    new_text = []
    for text in texts:
        new_text.extend(text)

    new_text = [line for line in new_text if line]

    return new_text