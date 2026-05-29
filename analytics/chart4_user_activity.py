from chart_engine import generate_from_template, save_chart_json,  generate_html
# analytics/chart4_user_activity.py
import plotly.express as px
from db_utils import query_to_df

df = query_to_df("""
    SELECT u.user_id, COUNT(e.event_id) AS events_count
    FROM users u LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id
""")
fig = px.histogram(df, x='events_count', log_y=True, nbins=50, title='User Activity (events count, log scale)')
# Сохраняем JSON для дашборда
save_chart_json(fig, "../output/charts/data/chart4.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(fig, "../template/charts/chart4_template.html", "../output/charts/chart4.html", plot_id="plot-4")
