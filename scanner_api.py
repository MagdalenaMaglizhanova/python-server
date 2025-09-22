from fastapi import APIRouter, Query
import easyocr
import numpy as np
from PIL import Image
import os

router = APIRouter()

BASE_TEST_DIR = os.path.join("test")

# --- остават harmful_e_numbers, harmful_keywords, food_categories и category_alternatives ---
# (не променяни)

@router.get("/list-test-files")
async def list_test_files():
    if not os.path.exists(BASE_TEST_DIR):
        return {"files": []}
    files = [f for f in os.listdir(BASE_TEST_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    return {"files": files}

@router.get("/scan-from-test")
async def scan_from_test(filename: str = Query(..., description="Името на тестовото изображение")):
    file_path = os.path.join(BASE_TEST_DIR, filename)

    if not os.path.exists(file_path):
        return {"error": f"Файлът {filename} не съществува."}

    image = Image.open(file_path).convert("RGB")
    image_np = np.array(image)

    reader = easyocr.Reader(['bg', 'en'])
    results = reader.readtext(image_np)

    full_text = " ".join([text for _, text, _ in results])
    full_text_lower = full_text.lower()

    found_e = {e: desc for e, desc in harmful_e_numbers.items() if e.lower() in full_text_lower}
    found_keywords = {word: reason for word, reason in harmful_keywords.items() if word in full_text_lower}

    product_category = None
    for keyword, category in food_categories.items():
        if keyword in full_text_lower:
            product_category = category
            break

    alternatives = []
    if (found_e or found_keywords) and product_category:
        alternatives = category_alternatives.get(product_category, [])

    report_lines = []
    if found_e:
        report_lines.append("🧪 Вредни E-номера:")
        for e, desc in found_e.items():
            report_lines.append(f"{e} - {desc}")
    else:
        report_lines.append("✅ Няма открити E-номера.")

    if found_keywords:
        report_lines.append("🧬 Засечени съставки:")
        for w, reason in found_keywords.items():
            report_lines.append(f"{w} – {reason}")
    else:
        report_lines.append("✅ Няма засечени опасни съставки по ключова дума.")

    if alternatives:
        report_lines.append(f"🍽 Алтернативи на {product_category}:")
        report_lines.extend(alternatives)

    report_text = "📄 OCR отчет за етикета:\n\n"
    report_text += "РАЗПОЗНАТ ТЕКСТ:\n" + full_text + "\n\n"
    report_text += "\n".join(report_lines)

    return {
        "full_text": full_text,
        "found_e_numbers": found_e,
        "found_keywords": found_keywords,
        "product_category": product_category,
        "alternatives": alternatives,
        "report": report_text
    }
