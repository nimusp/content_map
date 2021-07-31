FROM python:3

WORKDIR /usr/src/app

RUN python3 -m venv .env
RUN . .env/bin/activate

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]