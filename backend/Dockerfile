# Step 1: Use an official Python runtime as a parent image
FROM python:3.9-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy just the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the rest of the backend application code
COPY . .

# Step 5: Expose the port the app runs on (this is for documentation)
EXPOSE 8080

# Step 6: Define the command to run the application for production
# --- FINAL FIX: Changed to the more robust 'shell' syntax to guarantee $PORT expansion ---
CMD ["/bin/sh", "-c", "gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 300 main:app"]

