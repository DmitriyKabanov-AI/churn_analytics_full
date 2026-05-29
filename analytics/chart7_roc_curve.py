from chart_engine import generate_from_template, save_chart_json,  generate_html
# analytics/chart7_roc_curve.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go
import pandas as pd
from db_utils import query_to_df

df = query_to_df("""
    SELECT u.income, u.plan, u.region,
           COUNT(e.event_id) AS events,
           SUM(CASE WHEN e.event_type='purchase' THEN 1 ELSE 0 END) AS purchases,
           (s.end_date IS NOT NULL)::int AS churn
    FROM users u
    LEFT JOIN events e ON u.user_id = e.user_id
    LEFT JOIN subscriptions s ON u.user_id = s.user_id
    GROUP BY u.user_id, u.income, u.plan, u.region, s.end_date
""")
df = pd.get_dummies(df, columns=['plan', 'region'], drop_first=True)
X = df.drop('churn', axis=1)
y = df['churn']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

lr = LogisticRegression(max_iter=1000).fit(X_train, y_train)
rf = RandomForestClassifier(n_estimators=100).fit(X_train, y_train)

fpr_lr, tpr_lr, _ = roc_curve(y_test, lr.predict_proba(X_test)[:,1])
fpr_rf, tpr_rf, _ = roc_curve(y_test, rf.predict_proba(X_test)[:,1])

fig = go.Figure()
fig.add_trace(go.Scatter(x=fpr_lr, y=tpr_lr, mode='lines', name=f'LogReg (AUC={auc(fpr_lr, tpr_lr):.3f})'))
fig.add_trace(go.Scatter(x=fpr_rf, y=tpr_rf, mode='lines', name=f'RF (AUC={auc(fpr_rf, tpr_rf):.3f})'))
fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random', line=dict(dash='dash')))
fig.update_layout(title='ROC Curve', xaxis_title='False Positive Rate', yaxis_title='True Positive Rate')
# Сохраняем JSON для дашборда
save_chart_json(fig, "../output/charts/data/chart7.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(fig, "../template/charts/chart7_template.html", "../output/charts/chart7.html", plot_id="plot-7")
