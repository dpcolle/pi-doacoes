FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONUNBUFFERED=1 DATABASE_PATH=/data/dengue.sqlite
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m app && mkdir -p /data && chown app /data
USER app
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/api/saude')"
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000"]
