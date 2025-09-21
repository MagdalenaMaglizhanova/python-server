# scanner_api.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import easyocr
import numpy as np
from PIL import Image

app = FastAPI()

# Разрешаваме CORS за React фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или конкретен фронтенд URL
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/scan")
async def scan_image(file: UploadFile = File(...)):
    # Отваряме изображението
    image = Image.open(file.file).convert("RGB")
    image_np = np.array(image)

    reader = easyocr.Reader(['bg', 'en'])
    results = reader.readtext(image_np)

    full_text = " ".join([text for _, text, _ in results])
    full_text_lower = full_text.lower()

    found_e = {e: desc for e, desc in harmful_e_numbers.items() if e.lower() in full_text_lower}
    found_keywords = {word: reason for word, reason in harmful_keywords.items() if word in full_text_lower}

    return {
        "full_text": full_text,
        "found_e_numbers": found_e,
        "found_keywords": found_keywords
    }
