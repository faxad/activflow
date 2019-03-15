FROM python:3

LABEL maintainer="Fawad Qureshi <fawad@outlook.com>"

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
ADD . /app/

# Install dependencies
RUN pip install -r requirements.txt

EXPOSE 8000

# Execute on container start
CMD ["sh", "./app/scripts/on-container-start.sh"]
