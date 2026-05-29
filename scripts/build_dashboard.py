#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import re

# Определяем корень проекта
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists("/app") and SCRIPT_DIR.startswith("/app"):
    BASE_DIR = "/app"
else:
    BASE_DIR = os.path.dirname(SCRIPT_DIR)

sys.path.insert(0, os.path.join(BASE_DIR, "analytics"))
from chart_engine import _json_default

ANALYTICS_DIR = os.path.join(BASE_DIR, "analytics")
TEMPLATE_HTML = os.path.join(BASE_DIR, "template", "index.html")
OUTPUT_HTML = os.path.join(BASE_DIR, "output", "index.html")
CHARTS_DATA_DIR = os.path.join(BASE_DIR, "output", "charts", "data")

def run_all_chart_scripts():
    print("Запуск всех графиков...")
    for filename in sorted(os.listdir(ANALYTICS_DIR)):
        if filename.startswith("chart") and filename.endswith(".py") and filename != "chart_engine.py":
            script_path = os.path.join(ANALYTICS_DIR, filename)
            print(f"  Выполняется {filename}...")
            result = subprocess.run([sys.executable, script_path], cwd=ANALYTICS_DIR, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"    Ошибка: {result.stderr}")
            else:
                print(f"    OK")
    print("Все графики сгенерированы.\n")

def load_chart_json(chart_num):
    json_path = os.path.join(CHARTS_DATA_DIR, f"chart{chart_num}.json")
    if not os.path.exists(json_path):
        print(f"Предупреждение: {json_path} не найден")
        return None
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_template(html_content):
    """Удаляет синтетические графики из шаблона, оставляя навигацию и стили."""
    # Ищем блок скрипта с навигацией
    pattern = r'(/\* ---------- Navigation ---------- \*/.*?)(\n\s*)(/\* ---------- Plotly base config ---------- \*/.*?)(</script>)'
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        navigation_block = match.group(1)
        return html_content.replace(match.group(0), navigation_block + "\n    <!-- CHARTS_SCRIPT_PLACEHOLDER -->\n" + match.group(4))
    else:
        return html_content.replace("</body>", "<!-- CHARTS_SCRIPT_PLACEHOLDER -->\n</body>")

def build_dashboard():
    # 1. Запускаем все скрипты графиков
    run_all_chart_scripts()

    # 2. Проверяем наличие шаблона
    if not os.path.exists(TEMPLATE_HTML):
        print(f"Шаблон {TEMPLATE_HTML} не найден. Дашборд не собран.")
        return

    # 3. Читаем и очищаем шаблон от синтетики
    with open(TEMPLATE_HTML, 'r', encoding='utf-8') as f:
        raw_html = f.read()
    html = clean_template(raw_html)

    # 4. Загружаем JSON всех графиков и формируем JavaScript
    charts_js = []
    for i in range(1, 14):
        data = load_chart_json(i)
        if data is None:
            charts_js.append(f"// chart{i} not available")
            continue
        traces_json = json.dumps(data["traces"], ensure_ascii=False, default=_json_default)
        layout_json = json.dumps(data["layout"], ensure_ascii=False, default=_json_default)
        js = f"""
        (function() {{
            var traces{i} = {traces_json};
            var layout{i} = {layout_json};
            Plotly.newPlot('plot-{i}', traces{i}, layout{i}, {{
                responsive: true, displaylogo: false, displayModeBar: false
            }});
        }})();
        """
        charts_js.append(js)

    # 5. Вставляем скрипты вместо плейсхолдера
    placeholder = "<!-- CHARTS_SCRIPT_PLACEHOLDER -->"
    if placeholder in html:
        final_html = html.replace(placeholder, "\n".join(charts_js))
    else:
        final_html = html.replace("</body>", "\n".join(charts_js) + "\n</body>")

    # 6. Сохраняем дашборд
    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Единый дашборд сохранён: {OUTPUT_HTML}")

if __name__ == "__main__":
    build_dashboard()