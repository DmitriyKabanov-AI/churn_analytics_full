# analytics/chart1_income_vs_churn.py
from db_utils import query_to_df
from chart_engine import generate_from_template, save_chart_json,  generate_html
from plotly_theme import COLORS

df = query_to_df("""
    SELECT u.income, (s.end_date IS NOT NULL)::int AS churn
    FROM users u
    LEFT JOIN subscriptions s ON u.user_id = s.user_id
""")

# Подготовка данных для box plot
traces = []
for churn_val, name in [(0, 'Retained'), (1, 'Churned')]:
    y = df[df['churn'] == churn_val]['income'].dropna().tolist()
    traces.append({
        'y': y,
        'type': 'box',
        'name': name,
        'marker': {'color': COLORS['green'] if churn_val == 0 else COLORS['red']},
        'boxmean': True
    })

# Сохраняем JSON для дашборда
save_chart_json(traces, "../output/charts/data/chart1.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(traces, "../template/charts/chart1_template.html", "../output/charts/chart1.html", plot_id="plot-1")
