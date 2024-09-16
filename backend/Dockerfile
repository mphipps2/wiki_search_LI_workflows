# Use the official Python image as the base
FROM python:3.10-slim

# Set the working directory to the backend folder
WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl

# Copy the wait-for script
COPY wait-for-phoenix.sh /app/wait-for-phoenix.sh
RUN chmod +x /app/wait-for-phoenix.sh

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code from backend/src to the working directory
COPY src/ /app/src/

# Expose the FastAPI port
EXPOSE 8000

# Run the wait-for script on container start
CMD ["/app/wait-for-phoenix.sh"]
