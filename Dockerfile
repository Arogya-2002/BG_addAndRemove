# Use Python 3.10 slim version as the base image
FROM python:3.10-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the local directory to the container
COPY . /app

# Update apt packages and install AWS CLI
RUN apt update -y && apt install awscli -y

# Install the dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your app
CMD ["python", "app.py"]
