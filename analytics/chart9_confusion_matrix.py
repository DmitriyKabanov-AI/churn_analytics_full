from chart_engine import generate_from_template, save_chart_json,  generate_html
# analytics/chart9_confusion_matrix.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
import plotly.express as px
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

rf = RandomForestClassifier(n_estimators=100).fit(X_train, y_train)
cm = confusion_matrix(y_test, rf.predict(X_test))
fig = px.imshow(cm, text_auto=True, x=['Pred: 0', 'Pred: 1'], y=['Actual: 0', 'Actual: 1'],
                title='Confusion Matrix (Random Forest)', color_continuous_scale='Blues')
# Сохраняем JSON для дашборда
save_chart_json(fig, "../output/charts/data/chart9.json")
# Генерируем отдельный HTML из шаблона
generate_from_template(fig, "../template/charts/chart9_template.html", "../output/charts/chart9.html", plot_id="plot-9")
