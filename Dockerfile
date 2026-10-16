# Optional deployment recipe; Docker execution has not been verified in this assessment.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src src
COPY app app
COPY data data
COPY evaluation/metrics.json evaluation/metrics.json
COPY .streamlit .streamlit
RUN useradd --create-home appuser
USER appuser
EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "app/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
