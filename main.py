from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import io
import os
import re

app = Flask(__name__)
CORS(app)

# Tesseract конфигурация за Render
# На Render Tesseract е предварително инсталиран
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Вредни Е-номера с описания
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
    "кашкавал": "млечен продукт",
    "шоколад": "сладкиши",
    "бисквита": "сладкиши",
    "бонбони": "сладкиши",
    "вафла": "сладкиши",
    "сок": "напитки",
    "лимонада": "напитки",
    "кока-кола": "напитки"
}

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

def extract_text_from_image(image_data):
    """Извлича текст от изображение с Tesseract OCR"""
    try:
        # Отваряне на изображението
        image = Image.open(io.BytesIO(image_data))
        
        # Конвертиране към RGB ако е необходимо
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # OCR обработка с български и английски език
        text = pytesseract.image_to_string(image, lang='bul+eng')
        
        return text.strip()
        
    except Exception as e:
        return f"Грешка при OCR обработка: {str(e)}"

def analyze_text(text):
    """Анализира текста за вредни съставки"""
    text_lower = text.lower()
    
    # Търсене на E-номера
    found_e_numbers = []
    for e_num, description in harmful_e_numbers.items():
        # Търси E-номера с и без интервали: E102, E 102
        pattern = re.compile(r'\b' + re.escape(e_num) + r'\b', re.IGNORECASE)
        if pattern.search(text):
            found_e_numbers.append({
                'code': e_num,
                'description': description
            })
    
    # Търсене на ключови думи
    found_keywords = []
    for keyword, description in harmful_keywords.items():
        if keyword.lower() in text_lower:
            found_keywords.append({
                'keyword': keyword,
                'description': description
            })
    
    # Определяне на категорията на продукта
    product_category = None
    for keyword, category in food_categories.items():
        if keyword in text_lower:
            product_category = category
            break
    
    return found_e_numbers, found_keywords, product_category

def generate_report(ocr_text, e_numbers, keywords, category, alternatives):
    """Генерира текстов отчет"""
    report_lines = []
    report_lines.append("📄 OCR АНАЛИЗ НА ХРАНИТЕЛЕН ЕТИКЕТ")
    report_lines.append("=" * 50)
    
    report_lines.append("\n📖 РАЗПОЗНАТ ТЕКСТ:")
    report_lines.append(ocr_text if ocr_text else "Не е разпознат текст")
    report_lines.append("\n" + "=" * 50)
    
    if e_numbers:
        report_lines.append("\n🚨 ВРЕДНИ E-НОМЕРА:")
        for item in e_numbers:
            report_lines.append(f"• {item['code']}: {item['description']}")
    else:
        report_lines.append("\n✅ Няма открити вредни E-номера")
    
    if keywords:
        report_lines.append("\n⚠️ ЗАСЕЧЕНИ СЪСТАВКИ:")
        for item in keywords:
            report_lines.append(f"• {item['keyword']}: {item['description']}")
    else:
        report_lines.append("\n✅ Няма засечени опасни съставки")
    
    if category:
        report_lines.append(f"\n🏷️ КАТЕГОРИЯ НА ПРОДУКТА: {category}")
    
    if alternatives:
        report_lines.append("\n🍽 ПРЕПОРЪЧАНИ АЛТЕРНАТИВИ:")
        for alt in alternatives:
            report_lines.append(f"• {alt}")
    
    return "\n".join(report_lines)

@app.route('/api/scan', methods=['POST'])
def scan_image():
    """Основен endpoint за сканиране на изображения"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Няма качен файл'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Няма избран файл'}), 400
        
        # Проверка на файловия тип
        if not file.content_type.startswith('image/'):
            return jsonify({'error': 'Файлът трябва да е изображение (JPEG, PNG)'}), 400
        
        # Прочитане на изображението
        image_data = file.read()
        
        # OCR обработка
        ocr_text = extract_text_from_image(image_data)
        
        if ocr_text.startswith("Грешка"):
            return jsonify({'error': ocr_text}), 500
        
        # Анализ на текста
        e_numbers, keywords, category = analyze_text(ocr_text)
        
        # Определяне на алтернативи
        alternatives = []
        if (e_numbers or keywords) and category:
            alternatives = category_alternatives.get(category, [])
        
        # Генериране на отчет
        report = generate_report(ocr_text, e_numbers, keywords, category, alternatives)
        
        result = {
            'success': True,
            'ocr_text': ocr_text,
            'harmful_e_numbers': e_numbers,
            'harmful_keywords': keywords,
            'product_category': category,
            'alternatives': alternatives,
            'report': report
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Грешка при обработка: {str(e)}'}), 500

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text_endpoint():
    """Endpoint за анализ на текст без OCR"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Няма предоставен текст'}), 400
        
        text = data['text']
        if not text.strip():
            return jsonify({'error': 'Текстът е празен'}), 400
        
        # Анализ на текста
        e_numbers, keywords, category = analyze_text(text)
        
        # Определяне на алтернативи
        alternatives = []
        if (e_numbers or keywords) and category:
            alternatives = category_alternatives.get(category, [])
        
        # Генериране на отчет
        report = generate_report(text, e_numbers, keywords, category, alternatives)
        
        result = {
            'success': True,
            'harmful_e_numbers': e_numbers,
            'harmful_keywords': keywords,
            'product_category': category,
            'alternatives': alternatives,
            'report': report
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Грешка при анализ: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'message': 'OCR API работи успешно',
        'version': '1.0.0'
    })

@app.route('/')
def home():
    """Начална страница"""
    return jsonify({
        'message': 'OCR API за анализ на хранителни етикети',
        'endpoints': {
            'POST /api/scan': 'Сканиране на изображение',
            'POST /api/analyze-text': 'Анализ на текст',
            'GET /api/health': 'Проверка на състоянието'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
