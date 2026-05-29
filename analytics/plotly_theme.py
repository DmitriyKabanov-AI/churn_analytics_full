# analytics/plotly_theme.py

COLORS = {
    'primary': '#4f8cff',
    'purple': '#8b5cf6',
    'green': '#3fb950',
    'red': '#f85149',
    'orange': '#ff9f43',
    'cyan': '#22d3ee',
    'pink': '#ec4899',
    'grid': '#2a313c',
    'text': '#8b949e',
    'textBright': '#e6edf3',
    'muted': '#6e7681'
}

PALETTE = [COLORS['primary'], COLORS['purple'], COLORS['cyan'], COLORS['orange'], COLORS['green'], COLORS['pink'], COLORS['red']]

def base_layout():
    axis = {
        'gridcolor': COLORS['grid'],
        'linecolor': COLORS['grid'],
        'zerolinecolor': COLORS['grid'],
        'tickfont': {'color': COLORS['text']}
    }
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'family': 'Inter, -apple-system, sans-serif', 'color': COLORS['text'], 'size': 12},
        'margin': {'l': 60, 'r': 30, 't': 30, 'b': 50},
        'xaxis': axis,
        'yaxis': axis,
        'legend': {'font': {'color': COLORS['textBright']}, 'bgcolor': 'rgba(0,0,0,0)'},
        'hoverlabel': {'bgcolor': '#1c2128', 'bordercolor': '#3a4250', 'font': {'color': COLORS['textBright']}}
    }