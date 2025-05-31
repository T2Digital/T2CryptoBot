FROM python:3.10

WORKDIR /app

# انسخ الملفات
COPY backend /app/backend
COPY frontend /app/frontend
COPY .env /app/.env
COPY backend/requirements.txt /app/requirements.txt

# نثبت أدوات البناء وlibs الأساسية
RUN apt-get update && \
    apt-get install -y build-essential wget curl && \
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib*

# نثبت باقات بايثون
ENV LD_LIBRARY_PATH=/usr/local/lib
RUN pip install --upgrade pip && pip install ta-lib && pip install -r /app/requirements.txt

# نفتح البورتات
EXPOSE 8000 8501

# نشغل البوت والواجهة
CMD bash -c "uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/streamlit_app.py --server.port 8501 --server.enableCORS false"
