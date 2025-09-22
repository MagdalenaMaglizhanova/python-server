# main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import base64
import requests
import os

app = Flask(__name__)
CORS(app)

# Конфигурация
GOOGLE_VISION_API_URL = "https://vision.googleapis.com/v1/images:annotate"
API_KEY = os.environ.get('GOOGLE_VISION_API_KEY')  # Ще сетнеш в Render dashboard

# База данни със съставки (локална - няма нужда от големи модели)
harmful_e_numbers = {
    "E102", "E104", "E110", "E120", "E122", "E123", "E124", "E127", "E128", 
    "E129", "E131", "E132", "E133", "E142", "E151", "E154", "E155", "E180",
    "E210", "E211", "E212", "E213", "E214", "E215", "E216", "E217", "E218", 
    "E219", "E220", "E221", "E222", "E223", "E224", "E226", "E227", "E228",
    "E230", "E231", "E232", "E233", "E239", "E249", "E250", "E251", "E252",
    "E407", "E621", "E262", "E300", "E330", "E250"
}

harmful_keywords = {
    "нитрит": "Натриев нитрит – използва се в меса, свързан е с рак",
    "глутамат": "Натриев глутамат – може да предизвика главоболие и алергии",
    "карагинан": "Карагенан – свързан с възпаления в червата",
    "фосфат": "Фосфати – могат да влияят негативно на бъбреците",
    "консерван": "Консерванти – често съдържат нитрати или сулфити",
    "аспартам": "Изкуствен подсладител - потенциално вреден",
    "сахарин": "Изкуствен подсладител",
    "бензоат": "Бензоат натрия - може да причини алергии",
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
}

category_alternatives = {
    "преработено месо": [
        "🥗 Печено пилешко филе с подправки",
        "🍛 Леща яхния с моркови",
        "🥚 Яйца с авокадо",
        "🍗 Пушено пилешко филе",
        "🐟 Печен сьомга"
    ],
    "млечен продукт": [
        "🥥 Веган сирене от кашу",
        "🧄 Тофу с билки",
        "🥑 Авокадо за сосове",
        "🌰 Бадемово мляко"
    ]
}

def google_vision_ocr(image_data):
    """Използва Google Vision API за OCR"""
    if not API_KEY:
        return {"error": "Google Vision API key не е конфигуриран"}
    
    # Конвертиране на изображението до base64
    image_content = base64.b64encode(image_data).decode('utf-8')
    
    payload = {
        "requests": [
            {
                "image": {"content": image_content},
                "features": [{"type": "TEXT_DETECTION"}]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{GOOGLE_VISION_API_URL}?key={API_KEY}",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if 'responses' in result and result['responses']:
            text_annotations = result['responses'][0].get('textAnnotations', [])
            if text_annotations:
                return text_annotations[0].get('description', '')
        
        return ""
    except Exception as e:
        return {"error": f"Грешка при OCR: {str(e)}"}

def simple_text_analysis(text):
    """Локален анализ на текста (без външни зависимости)"""
    text_lower = text.lower()
    
    # Търсене на E-номера
    found_e_numbers = []
    for e_num in harmful_e_numbers:
        if e_num.lower() in text_lower:
            found_e_numbers.append(e_num)
    
    # Търсене на ключови думи
    found_keywords = []
    for keyword, description in harmful_keywords.items():
        if keyword in text_lower:
            found_keywords.append({"keyword": keyword, "description": description})
    
    # Определяне на категория
    product_category = None
    for keyword, category in food_categories.items():
        if keyword in text_lower:
            product_category = category
            break
    
    return found_e_numbers, found_keywords, product_category

@app.route('/api/scan', methods=['POST'])
def scan_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Няма качен файл'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Няма избран файл'}), 400

        # Прочитане на файла
        image_data = file.read()
        
        # OCR обработка
        ocr_result = google_vision_ocr(image_data)
        
        if isinstance(ocr_result, dict) and 'error' in ocr_result:
            # Fallback: опитай с Tesseract ако Google Vision не работи
            return jsonify({'error': ocr_result['error']}), 500
        
        # Анализ на текста
        found_e_numbers, found_keywords, product_category = simple_text_analysis(ocr_result)
        
        # Алтернативи
        alternatives = []
        if (found_e_numbers or found_keywords) and product_category:
            alternatives = category_alternatives.get(product_category, [])
        
        # Генериране на отчет
        report = generate_report(ocr_result, found_e_numbers, found_keywords, alternatives)
        
        result = {
            'success': True,
            'ocr_text': ocr_result,
            'harmful_e_numbers': found_e_numbers,
            'harmful_keywords': found_keywords,
            'product_category': product_category,
            'alternatives': alternatives,
            'report': report
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Грешка при обработка: {str(e)}'}), 500

@app.route('/api/scan-fallback', methods=['POST'])
def scan_fallback():
    """Алтернативен endpoint за тестване без OCR"""
    text = request.json.get('text', '')
    
    if not text:
        return jsonify({'error': 'Няма предоставен текст'}), 400
    
    # Анализ на текста
    found_e_numbers, found_keywords, product_category = simple_text_analysis(text)
    
    # Алтернативи
    alternatives = []
    if (found_e_numbers or found_keywords) and product_category:
        alternatives = category_alternatives.get(product_category, [])
    
    # Генериране на отчет
    report = generate_report(text, found_e_numbers, found_keywords, alternatives)
    
    result = {
        'success': True,
        'ocr_text': text,
        'harmful_e_numbers': found_e_numbers,
        'harmful_keywords': found_keywords,
        'product_category': product_category,
        'alternatives': alternatives,
        'report': report
    }
    
    return jsonify(result)

def generate_report(text, e_numbers, keywords, alternatives):
    report_lines = []
    report_lines.append("📄 АНАЛИЗ НА ХРАНИТЕЛЕН ЕТИКЕТ\n")
    report_lines.append("=" * 50)
    report_lines.append("\nРАЗПОЗНАТ ТЕКСТ:")
    report_lines.append(text)
    report_lines.append("\n" + "=" * 50)
    
    if e_numbers:
        report_lines.append("\n🚨 ВРЕДНИ E-НОМЕРА:")
        for e_num in e_numbers:
            report_lines.append(f"• {e_num}")
    else:
        report_lines.append("\n✅ Няма открити вредни E-номера")
    
    if keywords:
        report_lines.append("\n⚠️ ЗАСЕЧЕНИ СЪСТАВКИ:")
        for kw in keywords:
            report_lines.append(f"• {kw['keyword']}: {kw['description']}")
    else:
        report_lines.append("\n✅ Няма засечени опасни съставки")
    
    if alternatives:
        report_lines.append("\n🍽 ПРЕПОРЪЧАНИ АЛТЕРНАТИВИ:")
        for alt in alternatives:
            report_lines.append(f"• {alt}")
    
    return "\n".join(report_lines)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'OK', 
        'message': 'API работи успешно',
        'ocr_available': bool(API_KEY)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
