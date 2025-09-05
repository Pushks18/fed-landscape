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
# --- FIX: Changed the CMD to use the $PORT environment variable provided by Cloud Run ---
# We use the 'shell' form of CMD (a plain string) so that the $PORT variable is correctly interpreted.
CMD exec gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind "0.0.0.0:$PORT" --timeout 300 main:app

