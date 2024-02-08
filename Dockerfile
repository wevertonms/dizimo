# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Make a new directory to put our code in.
RUN mkdir /code

# Change the working directory.
# Every command after this will be run from the /code directory.
WORKDIR /code

# Copy the requirements.txt file.
COPY ./requirements.txt /code/

# Upgrade pip
RUN pip install --upgrade pip

# Install the requirements.
RUN pip install -r requirements.txt

# Copy the rest of the code.
COPY . /code/

# RUN apt-get install wkhtml2pdf

ENV SECRET_KEY="asdasd5a4sd51asd65a1s6d1a6sd13a1sd6a1sd3a1s"

RUN python manage.py makemigrations && python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]