FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt .

# Install requirements
RUN pip3 install -r requirements.txt

# Set server variables
ENV DATABASE_SERVER="barn"
ENV DATABASE_USER="outsideaccess"
ENV DATABASE_PW="db_pw_123"
ENV REDIS_SERVER="guard-dog"
ENV REDIS_PW="account_access_123"

COPY . .

EXPOSE 5000

CMD [ "python", "main.py" ]