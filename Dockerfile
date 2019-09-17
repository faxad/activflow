FROM python:3

LABEL maintainer="Fawad Qureshi <fawad@outlook.com>" \
      version="1.0.0"

ENV PYTHONUNBUFFERED 1

# Prepare
RUN mkdir /app
WORKDIR /app

# Handle dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Deploy codebase
COPY . .

EXPOSE 8000

# Execute on image run / container start 
ENTRYPOINT ["sh", "./scripts/on-container-start.sh"]
