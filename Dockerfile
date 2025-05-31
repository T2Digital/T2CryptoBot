FROM python:3.10

WORKDIR /app

# نسخ الملفات
COPY backend /app/backend
COPY frontend /app/frontend
COPY .env /app/.env
COPY backend/requirements.txt /app/requirements.txt

# تثبيت build tools وتحميل ta-lib من المصدر
RUN apt-get update && apt-get install -y build-essential wget

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# تثبيت باقات البايثون
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# فتح البورتات
EXPOSE 8000 8501

# تشغيل الـ backend والـ frontend معًا
CMD bash -c "uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/streamlit_app.py --server.port 8501 --server.enableCORS false"
