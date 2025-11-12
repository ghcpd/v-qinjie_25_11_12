FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip && pip install -r requirements.txt && python -m playwright install
EXPOSE 5001
CMD ["python", "src/app.py"]
