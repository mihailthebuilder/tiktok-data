FROM python:3.11.6

WORKDIR /usr/src/app

COPY chrome_profile .env ./

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps chromium

COPY main.py .

CMD ["python", "main.py", "--headless=True"]