# analytics/chart3_income_distribution.py
from chart_engine import generate_from_template, save_chart_json, generate_html
import plotly.graph_objects as go
import numpy as np
from db_utils import query_to_df
from plotly_theme import COLORS

# Загрузка данных
df = query_to_df("SELECT income FROM users")
income = df['income'].dropna().values

# ----- KDE (как в эталонном JavaScript) -----
def kde_python(data, points=100):
    min_val = np.min(data)
    max_val = np.max(data)
    bw = (max_val - min_val) / 30   # ширина окна, как в эталоне
    xs = np.linspace(min_val, max_val, points)
    ys = np.zeros_like(xs)
    for x_idx, x in enumerate(xs):
        s = 0.0
        for d in data:
            u = (x - d) / bw
            s += np.exp(-0.5 * u * u)
        ys[x_idx] = s / (len(data) * bw * np.sqrt(2 * np.pi))
    return xs, ys

xs_kde, ys_kde = kde_python(income)

# Создаём фигуру
fig = go.Figure()

# Гистограмма (плотность вероятности)
fig.add_trace(go.Histogram(
    x=income,
    name='Income',
    histnorm='probability density',   # как в эталоне
    marker_color=COLORS['primary'],
    opacity=0.75,
    nbinsx=40,
    marker_line=dict(color='#1a1f27', width=1)
))

# Линия KDE
fig.add_trace(go.Scatter(
    x=xs_kde, y=ys_kde,
    mode='lines',
    name='KDE',
    line=dict(color=COLORS['orange'], width=2.5)
))

# Оформление (тема из plotly_theme)
fig.update_layout(
    title='Distribution of Income',
    xaxis_title='Income, ₽',
    yaxis_title='Density',
    barmode='overlay',
    legend=dict(orientation='v', x=0.7, y=0.95)
)

# Сохраняем результаты
save_chart_json(fig, "../output/charts/data/chart3.json")
generate_from_template(fig, "../template/charts/chart3_template.html", "../output/charts/chart3.html", plot_id="plot-3")
