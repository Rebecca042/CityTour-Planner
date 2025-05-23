FROM python:3.11-slim

RUN apt-get update && apt-get install -y git gcc graphviz && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app

EXPOSE 8501 8000

CMD ["bash", "-c", "streamlit run app/streamlit_app.py --server.runOnSave false & uvicorn app.api:app --port 8000 --host 0.0.0.0"]
