FROM python:3.9-slim

WORKDIR /src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY tenable_helpers ./tenable_helpers
COPY setup.py .
COPY README.md .
RUN pip install -e .
