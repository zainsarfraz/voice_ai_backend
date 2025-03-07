# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code including scripts
COPY . .

# Ensure the script has execute permissions
RUN chmod +x ./scripts/start-backend.sh

# Expose the port your application runs on
EXPOSE 8000

# Set the entry point to the start script
ENTRYPOINT ["./scripts/start-backend.sh"]
