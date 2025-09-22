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
# На Render Tesseract е предварително инсталиран и се намира в PATH
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# --- Вредни E-номера, ключови думи, категории и алтернативи ---
# (тук поставяш същите dict-ове: harmful_e_numbers, harmful_keywords,
# food_categories, category_alternatives както в твоя код)
# ... 

# Функции за OCR и анализ на текст
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

# --- Flask Endpoints ---
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

# --- Локално тестване ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
