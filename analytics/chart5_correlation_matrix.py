from chart_engine import generate_from_template, save_chart_json,  generate_html
# analytics/chart5_correlation_matrix.py
import plotly.express as px
import pandas as pd
from db_utils import query_to_df

df = query_to_df("""
    SELECT u.income, COUNT(e.event_id) AS events,
           SUM(CASE WHEN e.event_type='purchase' THEN 1 ELSE 0 END) AS purchases
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u.income
""")
corr = df[['income', 'events', 'purchases']].corr()
fig = px.imshow(corr, text_auto=True, title='Correlation Matrix')
# Сохраняем JSON для дашборда
save_chart_json(fig, "../output/charts/data/chart5.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(fig, "../template/charts/chart5_template.html", "../output/charts/chart5.html", plot_id="plot-5")
