from chart_engine import generate_from_template, save_chart_json,  generate_html
# analytics/chart12_rolling_arpu.py
import plotly.graph_objects as go
from db_utils import query_to_df

df = query_to_df("SELECT date, arpu FROM daily_metrics ORDER BY date")
df['ma7'] = df['arpu'].rolling(window=7).mean()
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['date'], y=df['arpu'], mode='lines', name='Daily ARPU', opacity=0.5))
fig.add_trace(go.Scatter(x=df['date'], y=df['ma7'], mode='lines', name='7-day MA', line=dict(width=3)))
fig.update_layout(title='ARPU with 7-day Rolling Average', xaxis_title='Date', yaxis_title='ARPU')
# Сохраняем JSON для дашборда
save_chart_json(fig, "../output/charts/data/chart12.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(fig, "../template/charts/chart12_template.html", "../output/charts/chart12.html", plot_id="plot-12")
