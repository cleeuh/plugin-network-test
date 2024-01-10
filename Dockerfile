FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

RUN apt-get -y update
RUN apt-get -y install iperf3

COPY . .

ENTRYPOINT ["python3", "main.py"]
