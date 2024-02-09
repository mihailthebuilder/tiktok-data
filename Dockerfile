FROM python:3.11.8

WORKDIR /usr/src/app

COPY chrome_profile .env ./

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps chromium

RUN apt-get install xvfb

RUN apt-get install -y xauth

COPY main.py .

CMD ["xvfb-run", "-a","python", "main.py"]