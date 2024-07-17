FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy the .env file into the container
COPY .env .env

EXPOSE 50051

CMD ["python", "-m", "src.server.pdf_service"]
