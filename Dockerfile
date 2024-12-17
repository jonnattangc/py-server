FROM python:3.13-slim

LABEL VERSION=1.7
LABEL DESCRIPCION="Python Server HTTP V1.7"

ENV HOST_BD ''
ENV USER_BD ''
ENV PASS_BD ''
ENV USER_BD_LOGIA ''
ENV PASS_BD_LOGIA ''
ENV NOTIFICATION_URL ''
ENV HUB_SELENIUM_URL ''
ENV AWS_PINPOINT_APP_ID ''
ENV API_KEY_ROBOT_UPTIME ''
ENV ATTLASIAN_TOKEN ''
ENV ATTLASIAN_URL ''
ENV ATTLASIAN_USER ''
ENV WAZA_BEARER_TOKEN ''
ENV AWS_S3_BUCKET ''
ENV LOGIA_API_KEY ''
ENV PHONE_ID ''
ENV WAZA_API_VERSION ''
ENV UUID_WZ ''
ENV CHATBOT_API_KEY ''
ENV FILE_CHAT_KEY ''

ENV FLASK_APP app
ENV FLASK_DEBUG development

RUN addgroup --gid 10101 jonnattan && \
    adduser --home /home/jonnattan --uid 10100 --gid 10101 --disabled-password jonnattan

COPY ./requirements.txt /home/jonnattan/requirements.txt

RUN cd /home/jonnattan && \
    mkdir -p /home/jonnattan/.local/bin && \
    export PATH=$PATH:/home/jonnattan/.local/bin && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    chmod -R 755 /home/jonnattan  && \
    chown -R jonnattan:jonnattan /home/jonnattan

WORKDIR /home/jonnattan/app

USER jonnattan

EXPOSE 8085

CMD [ "python", "http-server.py", "8085"]
# python3 http-server.py 8085
# CMD [ "tail", "-f", "/home/jonnattan/requirements.txt" ]
# pip freeze > requirements.txt
