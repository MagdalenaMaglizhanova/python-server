from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import io
import os
import re

app = Flask(__name__)
CORS(app)

# Tesseract конфигурация
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# --------------------
# Вредни E-номера с описания
# --------------------
harmful_e_numbers = {
    "E102": "Тартразин - може да причини алергии",
    "E104": "Жълт хинолин - потенциално канцерогенен",
    "E110": "Жълт залез - алергичен реакции",
    "E120": "Кошеніл - алергичен реакции",
    "E122": "Азорубин - може да причини хиперактивност",
    "E123": "Амарант - забранен в много страни",
    "E124": "Понсо 4R - може да причини астма",
    "E127": "Еритрозин - влияе на щитовидната жлеза",
    "E129": "Червен очарователен - хиперактивност",
    "E131": "Синя патентована - оток на кожата",
    "E132": "Индиготин - повръщане и алергии",
    "E142": "Зелена S - канцерогенен",
    "E150": "Карамел - може да съдържа канцерогени",
    "E151": "Брилянтна черна - алергии",
    "E154": "Кафяв - натрапващ се в черния дроб",
    "E155": "Кафяв - алергичен реакции",
    "E180": "Литол рубин - стомашни проблеми",
    "E210": "Бензоена киселина - алергии",
    "E211": "Натриев бензоат - може да образува канцерогени",
    "E212": "Калиев бензоат - стомашни проблеми",
    "E213": "Калциев бензоат - алергии",
    "E214": "Етилов естер - забранен в много страни",
    "E215": "Натриев етилов естер - канцерогенен",
    "E216": "Пропилов естер - забранен",
    "E217": "Натриев пропил естер - канцерогенен",
    "E218": "Метилов естер - алергии",
    "E219": "Натриев метилов естер - канцерогенен",
    "E220": "Серен диоксид - астма и алергии",
    "E221": "Натриев сулфит - стомашни проблеми",
    "E222": "Натриев хидросулфит - алергии",
    "E223": "Натриев метасулфит - разрушава витамин B1",
    "E224": "Калиев метасулфит - стомашни проблеми",
    "E226": "Калциев сулфит - забранен в много страни",
    "E227": "Калциев хидросулфит - алергии",
    "E228": "Калиев хидросулфит - астма",
    "E230": "Дифенил - канцерогенен",
    "E231": "Ортофенилфенол - кожни проблеми",
    "E232": "Натриев ортофенилфенол - канцерогенен",
    "E233": "Тиабендазол - токсичен",
    "E239": "Хексаметилентетрамин - канцерогенен",
    "E249": "Калиев нитрит - образува нитрозамини",
    "E250": "Натриев нитрит - риск от рак",
    "E251": "Натриев нитрат - образува нитрозамини",
    "E252": "Калиев нитрат - риск от рак",
    "E407": "Карагенан - възпаления, храносмилателни проблеми",
    "E621": "Натриев глутамат - главоболие, алергии",
    "E262": "Натриев ацетат - дразни стомаха",
    "E300": "Аскорбинова киселина - в големи дози дразни стомаха",
    "E330": "Лимонена киселина - уврежда зъбния емайл"
}

# --------------------
# Вредни ключови думи
# --------------------
harmful_keywords = {
    "нитрит": "Натриев нитрит – използва се в меса, свързан е с рак",
    "глутамат": "Натриев глутамат – може да предизвика главоболие и алергии",
    "карагинан": "Карагенан – свързан с възпаления в червата",
    "фосфат": "Фосфати – могат да влияят негативно на бъбреците",
    "консерван": "Консерванти – често съдържат нитрати или сулфити",
    "аспартам": "Изкуствен подсладител - потенциално вреден",
    "сахарин": "Изкуствен подсладител - може да е канцерогенен",
    "бензоат": "Бензоат натрия - може да причини алергии",
    "сулфит": "Сулфити - астма и алергични реакции",
    "тартразин": "Тартразин - хиперактивност при деца",
    "транс": "Транс мазнини - повишават холестерола",
    "глутен": "Глутен - проблеми при непоносимост",
    "лактоза": "Лактоза - стомашен дискомфорт при непоносимост",
    "олестра": "Олестра - намалява абсорбцията на витамини"
}

# --------------------
# Категории храни
# --------------------
food_categories = {
    "луканка": "преработено месо",
    "салам": "преработено месо",
    "наденица": "преработено месо",
    "суджук": "преработено месо",
    "пастет": "преработено месо",
    "сирене": "млечен продукт",
    "кашкавал": "млечен продукт",
    "кисело": "млечен продукт",
    "мляко": "млечен продукт",
    "йогурт": "млечен продукт",
    "шоколад": "сладкиши",
    "бисквита": "сладкиши",
    "бонбони": "сладкиши",
    "вафла": "сладкиши",
    "сок": "напитки",
    "лимонада": "напитки",
    "кока-кола": "напитки"
}

# --------------------
# Алтернативи
# --------------------
category_alternatives = {
    "преработено месо": [
        "🥗 Печено пилешко филе с подправки",
        "🍛 Леща яхния с моркови и подправки",
        "🥚 Яйца с авокадо и свежи зеленчуци",
        "🍗 Пушено пилешко филе",
        "🐟 Печен сьомга или паламуд",
        "🥩 Домашни кюфтета от телешко"
    ],
    "млечен продукт": [
        "🥥 Веган сирене от кашу",
        "🧄 Тофу с билки – идеално за салата",
        "🥑 Авокадо за сосове и пасти",
        "🌰 Бадемово, овесно или соево мляко",
        "🌿 Кокосов йогурт"
    ],
    "сладкиши": [
        "🍎 Пресни плодове",
        "🍌 Бананово сладолед",
        "🌰 Фурми и ядки",
        "🍯 Мед с орехи",
        "🍓 Домашен плодов салати"
    ],
    "напитки": [
        "💧 Вода с лимон и мента",
        "🍵 Зелен чай",
        "🥤 Домашен лимонада",
        "🍎 Пресни плодови сокове",
        "🌿 Билочен чай"
    ]
}

# --------------------
# Функции
# --------------------
def extract_text_from_image(image_data):
    try:
        image = Image.open(io.BytesIO(image_data))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        text = pytesseract.image_to_string(image, lang='bul+eng')
        return text.strip()
    except Exception as e:
        return f"Грешка при OCR обработка: {str(e)}"

def analyze_text(text):
    text_lower = text.lower()
    found_e_numbers = []
    for e_num, desc in harmful_e_numbers.items():
        pattern = re.compile(r'\b' + re.escape(e_num) + r'\b', re.IGNORECASE)
        if pattern.search(text):
            found_e_numbers.append({'code': e_num, 'description': desc})
    found_keywords = []
    for keyword, desc in harmful_keywords.items():
        if keyword.lower() in text_lower:
            found_keywords.append({'keyword': keyword, 'description': desc})
    product_category = None
    for keyword, category in food_categories.items():
        if keyword in text_lower:
            product_category = category
            break
    return found_e_numbers, found_keywords, product_category

def generate_report(ocr_text, e_numbers, keywords, category, alternatives):
    lines = ["📄 OCR АНАЛИЗ НА ХРАНИТЕЛЕН ЕТИКЕТ", "="*50]
    lines.append("\n📖 РАЗПОЗНАТ ТЕКСТ:")
    lines.append(ocr_text if ocr_text else "Не е разпознат текст")
    lines.append("\n" + "="*50)
    if e_numbers:
        lines.append("\n🚨 ВРЕДНИ E-НОМЕРА:")
        for item in e_numbers:
            lines.append(f"• {item['code']}: {item['description']}")
    else:
        lines.append("\n✅ Няма открити вредни E-номера")
    if keywords:
        lines.append("\n⚠️ ЗАСЕЧЕНИ СЪСТАВКИ:")
        for item in keywords:
            lines.append(f"• {item['keyword']}: {item['description']}")
    else:
        lines.append("\n✅ Няма засечени опасни съставки")
    if category:
        lines.append(f"\n🏷️ КАТЕГОРИЯ НА ПРОДУКТА: {category}")
    if alternatives:
        lines.append("\n🍽 ПРЕПОРЪЧАНИ АЛТЕРНАТИВИ:")
        for alt in alternatives:
            lines.append(f"• {alt}")
    return "\n".join(lines)

# --------------------
# Flask Endpoints
# --------------------
@app.route('/api/scan', methods=['POST'])
def scan_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Няма качен файл'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Няма избран файл'}), 400
        if not file.content_type.startswith('image/'):
            return jsonify({'error': 'Файлът трябва да е изображение (JPEG, PNG)'}), 400
        image_data = file.read()
        ocr_text = extract_text_from_image(image_data)
        if ocr_text.startswith("Грешка"):
            return jsonify({'error': ocr_text}), 500
        e_numbers, keywords, category = analyze_text(ocr_text)
        alternatives = category_alternatives.get(category, []) if (e_numbers or keywords) and category else []
        report = generate_report(ocr_text, e_numbers, keywords, category, alternatives)
        return jsonify({
            'success': True,
            'ocr_text': ocr_text,
            'harmful_e_numbers': e_numbers,
            'harmful_keywords': keywords,
            'product_category': category,
            'alternatives': alternatives,
            'report': report
        })
    except Exception as e:
        return jsonify({'error': f'Грешка при обработка: {str(e)}'}), 500

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text_endpoint():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Няма предоставен текст'}), 400
        text = data['text']
        if not text.strip():
            return jsonify({'error': 'Текстът е празен'}), 400
        e_numbers, keywords, category = analyze_text(text)
        alternatives = category_alternatives.get(category, []) if (e_numbers or keywords) and category else []
        report = generate_report(text, e_numbers, keywords, category, alternatives)
        return jsonify({
            'success': True,
            'harmful_e_numbers': e_numbers,
            'harmful_keywords': keywords,
            'product_category': category,
            'alternatives': alternatives,
            'report': report
        })
    except Exception as e:
        return jsonify({'error': f'Грешка при анализ: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'message': 'OCR API работи успешно', 'version': '1.0.0'})

@app.route('/')
def home():
    return jsonify({
        'message': 'OCR API за анализ на хранителни етикети',
        'endpoints': {
            'POST /api/scan': 'Сканиране на изображение',
            'POST /api/analyze-text': 'Анализ на текст',
            'GET /api/health': 'Проверка на състоянието'
        }
    })

# --------------------
# Локално стартиране
# --------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
