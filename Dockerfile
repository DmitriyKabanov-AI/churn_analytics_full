FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY analytics/ ./analytics/
COPY scripts/ ./scripts/
COPY template/ ./template/
COPY function/ ./function/
COPY init_db.sql ./
RUN mkdir -p output/charts/data
ENV DB_HOST=postgres DB_PORT=5432 DB_NAME=churn_db DB_USER=churn_user DB_PASSWORD=churn123
CMD ["python", "scripts/run_pipeline.py"]