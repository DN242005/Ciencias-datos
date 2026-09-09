FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY hello-dash.py autos_10000.csv ./

EXPOSE 8501

CMD ["sh", "-c", "streamlit run hello-dash.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]