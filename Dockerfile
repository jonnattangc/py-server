FROM python:3.9-slim

LABEL VERSION=1.1
LABEL DESCRIPCION="Python Server HTTP V2"

# variables importantes
ARG SECRET_KEY
ARG AES_KEY
ARG AWS_ACCESS_KEY
ARG AWS_SECRET_KEY
ARG AWS_PINPOINT_APP_ID

ENV HOST_BD ''
ENV USER_BD ''
ENV PASS_BD ''
ENV USER_BD_LOGIA ''
ENV PASS_BD_LOGIA ''
ENV NOTIFICATION_URL ''
ENV HUB_SELENIUM_URL ''

ENV FLASK_APP app
ENV FLASK_DEBUG development

RUN addgroup --gid 10101 jonnattan && \
    adduser --home /home/jonnattan --uid 10100 --gid 10101 --disabled-password jonnattan

USER jonnattan  

COPY ./requirements.txt /home/jonnattan/requirements.txt

RUN cd /home/jonnattan && \ 
    mkdir -p /home/jonnattan/.local/bin && \
    export PATH=$PATH:/home/jonnattan/.local/bin && \
    pip install --upgrade pip && \
    pip install -r requirements.txt 

WORKDIR /home/jonnattan/app

EXPOSE 8085

CMD [ "python", "http-server.py", "8085"]
# python3 http-server.py 8085
# CMD [ "/bin/sh", "./run.sh" ]

