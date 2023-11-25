FROM python:latest

# Install the dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# # Install zbar
RUN apt-get update && apt-get install libzbar0 -y && pip install pyzbar

# Copy all files from the current directory
COPY . /app

# Set the working directory
WORKDIR /app

# Expose port 8000
EXPOSE 8000

# Start the API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]