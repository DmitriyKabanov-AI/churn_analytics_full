# Дашборд аналитики оттока клиентов (Churn Analytics)

**Публичный проект** для генерации синтетических данных, расчёта метрик оттока и визуализации ключевых показателей.  
Включает PostgreSQL (100 000+ пользователей), 13 интерактивных графиков Plotly и веб‑дашборд.  
Всё запускается одной командой через Docker — данные и графики генерируются автоматически.

## 🚀 Быстрый старт

```bash
git clone https://github.com/ваш-репозиторий/churn_analytics_full.git
cd churn_analytics_full
docker-compose up --build
```

После завершения сборки:

Grafana → http://localhost:3001 (логин/пароль admin/admin)

Контейнер python сам:

сгенерирует тестовые данные (при первом запуске),

построит все 13 графиков Plotly,

соберёт единый дашборд output/index.html.

Контейнер web (nginx) отдаёт статический дашборд.
Повторные запуски не пересоздают данные (если нужно с нуля — docker-compose down -v).

```
📊 Графики Plotly (13 штук)
№ 1
Название: Доход vs Отток
Тип: Ящик с усами
─────────────────────

№ 2
Название: Тарифный план vs Отток
Тип: Столбчатая (с накоплением)
─────────────────────

№ 3
Название: Распределение дохода
Тип: Гистограмма + KDE
─────────────────────

№ 4
Название: Активность пользователей (события)
Тип: Гистограмма (лог. шкала)
─────────────────────

№ 5
Название: Корреляционная матрица
Тип: Тепловая карта
─────────────────────

№ 6
Название: События vs Отток
Тип: Ящик с усами
─────────────────────

№ 7
Название: ROC‑кривая
Тип: Линии (Random Forest, LogReg)
─────────────────────

№ 8
Название: Важность признаков
Тип: Горизонтальные столбцы
─────────────────────

№ 9
Название: Матрица ошибок
Тип: Тепловая карта
─────────────────────

№ 10
Название: Метрики моделей
Тип: Таблица (AUC, F1 и др.)
─────────────────────

№ 11
Название: Кумулятивный LTV
Тип: Временные ряды по когортам
─────────────────────

№ 12
Название: Скользящее среднее ARPU
Тип: Дневное + 7-дневное среднее
─────────────────────

№ 13
Название: Динамика оттока
Тип: Временной ряд (завершённые подписки)
📈 Grafana (опционально, но уже настроена)
→ Автоматическая настройка через provisioning
```
Источник данных ChurnDB подключается к PostgreSQL (параметры в datasources/postgres.yaml).

Дашборды загружаются из папки dashboards/ – в них уже встроены SQL-запросы к таблицам daily_metrics, retention_cohorts, rfm, ltv.

После запуска откройте http://localhost:3001 (логин/пароль admin/admin).
Вы увидите предустановленные графики:

DAU, ARPU, Conversion to Purchase (из daily_metrics)

Retention heatmap (из retention_cohorts)

Распределение RFM-сегментов (из rfm)

LTV по когортам (из ltv)

Вы можете редактировать эти дашборды или создавать свои – изменения сохранятся в томе grafana_data.

### 📊 SQL-запросы для Grafana

```sql
-- DAU (Daily Active Users)
SELECT date::timestamp as time, dau as value 
FROM daily_metrics 
ORDER BY date;

-- ARPU (Average Revenue Per User)
SELECT date::timestamp as time, arpu as value 
FROM daily_metrics 
ORDER BY date;

-- Conversion to Purchase
SELECT date::timestamp as time, conversion_to_purchase as value 
FROM daily_metrics 
ORDER BY date;

-- Retention Heatmap
SELECT cohort_month::date as time, months_diff as metric, retention_rate as value 
FROM retention_cohorts 
ORDER BY cohort_month, months_diff;

-- RFM-сегменты
SELECT rfm_score, COUNT(*) as users 
FROM rfm 
GROUP BY rfm_score 
ORDER BY users DESC;

-- LTV по когортам
SELECT purchase_month::date as time, cohort_month, ltv 
FROM ltv 
ORDER BY purchase_month, cohort_month;
```

🧪 Тестирование
```bash
Python‑тесты (pytest)
pytest tests/python/
```

SQL‑тесты (схема и функции)
```bash
docker exec -i churn_postgres psql -U churn_user -d churn_db < tests/sql/test_schema.sql
```
(транзакция откатывается — данные не изменяются)

🛠 Технологии
PostgreSQL 15 – хранение данных, SQL‑функции генерации

Python 3.14 – аналитика, построение графиков (pandas, numpy, scikit-learn, plotly)

Docker + docker-compose – контейнеризация

Nginx – раздача статического дашборда

Grafana – дополнительная визуализация (опционально)

📁 Структура проекта и описание папок / файлов
```
churn_analytics_full/
├── analytics/               # Python‑скрипты для построения графиков
│   ├── chart1_*.py … chart13_*.py   # каждый скрипт строит один график (получает данные из БД)
│   ├── chart_engine.py      # общие функции: генерация HTML/JSON, работа с шаблонами
│   ├── db_utils.py          # подключение к PostgreSQL (через переменные окружения)
│   └── plotly_theme.py      # единая тёмная тема и цвета для всех графиков
│
├── scripts/                 # Скрипты-оркестраторы
│   ├── build_dashboard.py   # запускает все chart*.py, затем собирает единый index.html из шаблона
│   └── run_pipeline.py      # ждёт БД, генерирует тестовые данные (если их нет), запускает build_dashboard
│
├── template/                # HTML‑шаблоны (без встроенных данных)
│   ├── index.html           # шаблон дашборда (стили, навигация, пустые контейнеры plot-1..plot-13)
│   └── charts/              # 13 шаблонов для отдельных страниц графиков (chartX_template.html)
│
├── output/                  # ВСЕ СГЕНЕРИРОВАННЫЕ ФАЙЛЫ (создаётся при запуске)
│   ├── index.html           # финальный дашборд со всеми 13 реальными графиками
│   └── charts/              # отдельные страницы каждого графика (chartX.html) + папка data/ с JSON
│
├── function/                # SQL‑функции для PostgreSQL
│   ├── generate_churn_data  # генерация тестовых данных (100k users, 3M events)
│   ├── ltv.sql, rfm.sql, retention_cohorts.sql, daily_metrics.sql
│
├── dashboards/              # Конфигурация provisioning для Grafana
│   └── dashboard.yaml       # указывает Grafana, откуда загружать дашборды
├── datasources/             # Источники данных для Grafana
│   └── postgres.yaml        # подключение к PostgreSQL (хост, порт, БД, пользователь, пароль)
│
├── tests/                   # Тесты
│   ├── python/              # pytest‑тесты (test_db_utils.py, test_charts.py)
│   ├── sql/                 # SQL‑тесты (test_schema.sql) – проверка таблиц и функций
│   └── conftest.py          # фикстуры для pytest
│
├── init_db.sql              # Схема базы данных (таблицы + функции)
├── docker-compose.yml       # Описание сервисов: postgres, python, web, grafana
├── Dockerfile               # Сборка образа для python‑сервиса
├── requirements.txt         # Python‑зависимости
├── .dockerignore            # Исключения для Docker‑образа
├── .gitignore               # Исключения для Git
└── README.md                # Этот файл
```
Пояснение ключевых элементов

analytics/db_utils.py – подключается к БД через переменные окружения (DB_HOST, DB_PORT...). Внутри Docker подставляются значения из docker-compose.yml, локально – значения по умолчанию (localhost:5435).

scripts/build_dashboard.py – запускает все chartX.py, затем читает сгенерированные JSON, очищает шаблон template/index.html от синтетических графиков и вставляет реальные. Результат – output/index.html.

scripts/run_pipeline.py – точка входа для контейнера python: ждёт БД, при отсутствии данных вызывает generate_churn_data, затем запускает build_dashboard.py.

output/ – монтируется как том, поэтому сгенерированные файлы остаются после остановки контейнера. Веб‑сервер (nginx) читает файлы именно отсюда.

template/index.html – содержит стили, боковое меню, навигацию и пустые div для графиков. В процессе сборки из него удаляются синтетические Plotly.newPlot и вставляются реальные.

📝 Лицензия
MIT – свободное использование, модификация, распространение.