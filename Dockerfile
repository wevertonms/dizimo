# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev curl && \
    apt-get clean

# Copy project files
COPY requirements.txt /app/

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the project
COPY . /app/

# Copy entrypoint script
COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "dizimo.wsgi:application", "--bind", "0.0.0.0:8000"]