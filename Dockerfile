FROM python:3.9-slim

LABEL VERSION=1.1
LABEL DESCRIPCION="Python Server HTTP V2"

# variables importantes
ARG SECRET_KEY
ARG AES_KEY
ARG AWS_ACCESS_KEY
ARG AWS_SECRET_KEY

ENV HOST_BD ''
ENV USER_BD ''
ENV PASS_BD ''
ENV USER_BD_LOGIA ''
ENV PASS_BD_LOGIA ''
ENV NOTIFICATION_URL ''
ENV HUB_SELENIUM_URL ''

ENV FLASK_APP app
ENV FLASK_DEBUG development

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip && \
    pip3 install -r requirements.txt

EXPOSE 8085

CMD [ "python3", "http-server.py", "8085"]
# python3 http-server.py 8085
# CMD [ "/bin/sh", "./run.sh" ]

