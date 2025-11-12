FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install --with-deps
COPY src /app/src
COPY templates /app/templates
COPY static /app/static
ENV FLASK_APP=src/app.py
EXPOSE 5002
CMD ["python", "src/app.py"]
