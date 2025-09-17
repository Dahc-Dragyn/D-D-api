# Dockerfile

# Use an official Python runtime as a parent image
# Using python:3.11 based on your environment, slim is smaller
FROM python:3.11-slim

# Set environment variables
# Ensures Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED=1
# Optionally prevent pip from caching (can make builds more consistent)
# ENV PIP_NO_CACHE_DIR=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if any were needed (e.g., build-essential for some packages)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*
# Currently, none seem strictly necessary based on successful pip install, but keep in mind if issues arise.

# Upgrade pip
RUN pip install --upgrade pip

# Copy the requirements file into the container at /app
# Copying requirements first takes advantage of Docker layer caching
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir can reduce final image size slightly
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# This includes main.py and the faiss_index directory
COPY main.py .
COPY faiss_index/ ./faiss_index/

# Make port 8080 available to the world outside this container
# Cloud Run expects the container to listen on port 8080 by default
EXPOSE 8080

# Define environment variables if needed by the app (e.g., API keys)
# ENV MY_VARIABLE="my_value"

# Run uvicorn server when the container launches
# Use port 8080 to match Cloud Run's default and the EXPOSE directive
# Do NOT use --reload in production containers
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]