from chart_engine import generate_from_template, save_chart_json,  generate_html
# analytics/chart11_cumulative_ltv.py
import plotly.express as px
import pandas as pd
from db_utils import query_to_df

df = query_to_df("""
    SELECT cohort_month, purchase_month, ltv
    FROM ltv
    ORDER BY cohort_month, purchase_month
""")
# Накопленный LTV для каждой когорты
df['cumulative_ltv'] = df.groupby('cohort_month')['ltv'].cumsum()
fig = px.line(df, x='purchase_month', y='cumulative_ltv', color='cohort_month',
              title='Cumulative LTV by Cohort', labels={'purchase_month': 'Month', 'cumulative_ltv': 'Cumulative LTV'})
# Сохраняем JSON для дашборда
save_chart_json(fig, "../output/charts/data/chart11.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(fig, "../template/charts/chart11_template.html", "../output/charts/chart11.html", plot_id="plot-11")
