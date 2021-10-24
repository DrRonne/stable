FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .

# Install requirements
RUN pip3 install -r requirements.txt

# Set server variables
ENV DATABASE_SERVER="Tasks"
ENV DATABASE_USER="outsideaccess"
ENV DATABASE_PW="db_pw_123"

COPY . .

EXPOSE 5000

CMD [ "python", "main.py" ]