# Step 1: Use an official Python runtime as a parent image
FROM python:3.9-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy just the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the rest of the backend application code
COPY . .

# Step 5: Expose the port the app runs on
EXPOSE 8000

# Step 6: Define the command to run the application for production
# --- FIX: Increased timeout from 120 to 300 seconds for long-running tasks ---
CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "300", "main:app"]

