
FROM python:3.10
WORKDIR /app
COPY backend /app/backend
COPY frontend /app/frontend
COPY .env /app/.env
COPY backend/requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y build-essential libta-lib0 libta-lib0-dev
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
EXPOSE 8000 8501
CMD bash -c "uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/streamlit_app.py --server.port 8501 --server.enableCORS false"
