# Start from the requestprocessor-builder:latest image
FROM receipt-processor-builder:latest AS app

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade --requirement requirements.txt

# Copy over project files
COPY ./app /app

# Run Fast API
CMD ["fastapi", "run", "main.py", "--port", "80"]
