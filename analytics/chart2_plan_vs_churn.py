from chart_engine import generate_from_template, save_chart_json,  generate_html
# analytics/chart2_plan_vs_churn.py
import pandas as pd
import plotly.graph_objects as go
from db_utils import query_to_df

df = query_to_df("""
    SELECT u.plan, (s.end_date IS NOT NULL)::int AS churn
    FROM users u
    LEFT JOIN subscriptions s ON u.user_id = s.user_id
""")
ct = pd.crosstab(df['plan'], df['churn'])
ct.columns = ['Retained', 'Churned']
fig = go.Figure(data=[
    go.Bar(name='Retained', x=ct.index, y=ct['Retained']),
    go.Bar(name='Churned', x=ct.index, y=ct['Churned'])
])
fig.update_layout(barmode='stack', title='Plan vs Churn', xaxis_title='Plan', yaxis_title='Customers')
# Сохраняем JSON для дашборда
save_chart_json(fig, "../output/charts/data/chart2.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(fig, "../template/charts/chart2_template.html", "../output/charts/chart2.html", plot_id="plot-2")
