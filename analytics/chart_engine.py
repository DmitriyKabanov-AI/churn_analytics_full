import json
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import plotly.graph_objects as go
from plotly_theme import base_layout, COLORS

def generate_html(fig_or_traces, output_path, title="Chart", width="100%", height="100%"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if isinstance(fig_or_traces, go.Figure):
        traces = [trace.to_plotly_json() for trace in fig_or_traces.data]
        user_layout = fig_or_traces.layout.to_plotly_json()
        base = base_layout()
        final_layout = base.copy()
        for key, val in user_layout.items():
            if key not in final_layout:
                final_layout[key] = val
            elif isinstance(val, dict) and isinstance(final_layout.get(key), dict):
                final_layout[key].update(val)
            else:
                final_layout[key] = val
        final_layout['paper_bgcolor'] = 'rgba(0,0,0,0)'
        final_layout['plot_bgcolor'] = 'rgba(0,0,0,0)'
        layout_dict = final_layout
    else:
        traces = fig_or_traces
        layout_dict = base_layout()
        if title and title != "Chart":
            layout_dict['title'] = {'text': title, 'font': {'color': COLORS['textBright']}}
    traces_json = json.dumps(traces, default=_json_default, ensure_ascii=False)
    layout_json = json.dumps(layout_dict, default=_json_default, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{title}</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>html,body{{margin:0;padding:0;width:100%;height:100%;background:transparent;}}</style>
</head>
<body><div id="chart-container" style="width:100%;height:100%;"></div>
<script>var traces={traces_json};var layout={layout_json};
Plotly.newPlot('chart-container',traces,layout,{{responsive:true,displaylogo:false}});</script>
</body></html>"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

def figure_to_json(fig_or_traces):
    if isinstance(fig_or_traces, go.Figure):
        traces = [trace.to_plotly_json() for trace in fig_or_traces.data]
        user_layout = fig_or_traces.layout.to_plotly_json()
        base = base_layout()
        final_layout = base.copy()
        for key, val in user_layout.items():
            if key not in final_layout:
                final_layout[key] = val
            elif isinstance(val, dict) and isinstance(final_layout.get(key), dict):
                final_layout[key].update(val)
            else:
                final_layout[key] = val
        final_layout['paper_bgcolor'] = 'rgba(0,0,0,0)'
        final_layout['plot_bgcolor'] = 'rgba(0,0,0,0)'
        layout = final_layout
    else:
        traces = fig_or_traces
        layout = base_layout()
    return {"traces": traces, "layout": layout}

def save_chart_json(fig_or_traces, output_json_path):
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    data = figure_to_json(fig_or_traces)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=_json_default)

def generate_from_template(fig_or_traces, template_path, output_html_path, plot_id="plot-1"):
    data = figure_to_json(fig_or_traces)
    traces_json = json.dumps(data["traces"], ensure_ascii=False, default=_json_default)
    layout_json = json.dumps(data["layout"], ensure_ascii=False, default=_json_default)
    js_code = f"""
var traces = {traces_json};
var layout = {layout_json};
Plotly.newPlot('{plot_id}', traces, layout, {{
    responsive: true, displaylogo: false, displayModeBar: false
}});
"""
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    final_html = template.replace("PLACEHOLDER_FOR_PLOTLY_SCRIPT", js_code)
    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

def _json_default(obj):
    import numpy as np, datetime
    if isinstance(obj, np.integer): return int(obj)
    if isinstance(obj, np.floating): return float(obj)
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, (datetime.datetime, datetime.date)): return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")