# Use a Python 3.10 runtime as a parent image for fish-audio-sdk compatibility
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# We also install ffmpeg which is required for many audio operations
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Make port 7860 available to the world outside this container
EXPOSE 7860

# Command to run the application using gunicorn, a production-ready server
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "600", "app:app"] 