from chart_engine import generate_from_template, save_chart_json,  generate_html
# analytics/chart6_events_vs_churn.py
import plotly.express as px
from db_utils import query_to_df

df = query_to_df("""
    SELECT COUNT(e.event_id) AS events, (s.end_date IS NOT NULL)::int AS churn
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    LEFT JOIN subscriptions s ON u.user_id = s.user_id
    GROUP BY u.user_id, s.end_date
""")
fig = px.box(df, x='churn', y='events', color='churn', title='Events count vs Churn')
# Сохраняем JSON для дашборда
save_chart_json(fig, "../output/charts/data/chart6.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(fig, "../template/charts/chart6_template.html", "../output/charts/chart6.html", plot_id="plot-6")
