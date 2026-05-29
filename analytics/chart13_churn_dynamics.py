from chart_engine import generate_from_template, save_chart_json,  generate_html
# analytics/chart13_churn_dynamics.py
import plotly.express as px
from db_utils import query_to_df

df = query_to_df("""
    SELECT end_date::date AS date, COUNT(*) AS churns
    FROM subscriptions
    WHERE end_date IS NOT NULL
    GROUP BY end_date::date
    ORDER BY date
""")
fig = px.line(df, x='date', y='churns', title='Daily Churn Dynamics', labels={'churns': 'Churned users'})
# Сохраняем JSON для дашборда
save_chart_json(fig, "../output/charts/data/chart13.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(fig, "../template/charts/chart13_template.html", "../output/charts/chart13.html", plot_id="plot-13")
