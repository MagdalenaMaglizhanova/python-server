# scanner_api.py
from fastapi import APIRouter, UploadFile, File
import easyocr
import numpy as np
from PIL import Image

# Създаваме router
router = APIRouter()

# ===== Инициализираме OCR reader само веднъж =====
reader = easyocr.Reader(['bg', 'en'])  # кеширане за по-бързо първо сканиране

# Вредни Е-номера
harmful_e_numbers = {
    "E407": "Карагенан (възпаления, храносмилателни проблеми)",
    "E621": "Натриев глутамат (главоболие, алергии)",
    "E262": "Натриев ацетат (дразни стомаха)",
    "E300": "Аскорбинова киселина (в големи дози дразни стомаха)",
    "E330": "Лимонена киселина (уврежда зъбния емайл)",
    "E250": "Натриев нитрит (риск от рак, в месо)",
}

# Вредни съставки по ключова дума
harmful_keywords = {
    "нитрит": "Натриев нитрит – използва се в меса, свързан е с рак",
    "глутамат": "Натриев глутамат – може да предизвика главоболие и алергии",
    "карагинан": "Карагенан – свързан с възпаления в червата",
    "фосфат": "Фосфати – могат да влияят негативно на бъбреците",
    "консерван": "Консерванти – често съдържат нитрати или сулфити",
    "лактоза": "Лактоза – може да причини стомашен дискомфорт при непоносимост",
}

# Категории продукти
food_categories = {
    "луканка": "преработено месо",
    "салам": "преработено месо",
    "наденица": "преработено месо",
    "суджук": "преработено месо",
    "пастет": "преработено месо",
    "сирене": "млечен продукт",
    "кашкавал": "млечен продукт",
}

# Алтернативи
category_alternatives = {
    "преработено месо": [
        "🥗 Вместо колбас – печено пилешко филе с подправки.",
        "🍛 Леща яхния с моркови и подправки.",
        "🥚 Яйца с авокадо и свежи зеленчуци.",
    ],
    "млечен продукт": [
        "🥥 Веган сирене от кашу.",
        "🧄 Тофу с билки – идеално за салата.",
    ]
}


@router.post("/scan")
async def scan_image(file: UploadFile = File(...)):
    # Отваряме и конвертираме изображението
    image = Image.open(file.file).convert("RGB")
    image_np = np.array(image)

    # OCR
    results = reader.readtext(image_np)

    # Обединяваме текста
    full_text = " ".join([text for _, text, _ in results])
    full_text_lower = full_text.lower()

    # Търсим вредни Е-номера
    found_e = {e: desc for e, desc in harmful_e_numbers.items() if e.lower() in full_text_lower}
    # Търсим ключови думи
    found_keywords = {word: reason for word, reason in harmful_keywords.items() if word in full_text_lower}

    # Определяме категорията на продукта
    product_category = None
    for keyword, category in food_categories.items():
        if keyword in full_text_lower:
            product_category = category
            break

    # Алтернативи, ако има вредни съставки и категория
    alternatives = []
    if (found_e or found_keywords) and product_category:
        alternatives = category_alternatives.get(product_category, [])

    # Генерираме отчет
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
