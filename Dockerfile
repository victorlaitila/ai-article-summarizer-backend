FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
  libxslt1-dev libxml2-dev python3-dev gcc curl && \
  rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]