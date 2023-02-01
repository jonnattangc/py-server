FROM python:3.9-slim

LABEL VERSION=1.1
LABEL DESCRIPCION="Python Server HTTP V2"

# variables importantes
ARG SECRET_KEY
ARG HOST_BD
ARG USER_BD
ARG PASS_BD
ARG USER_BD_LOGIA
ARG PASS_BD_LOGIA
ARG AES_KEY
ARG AWS_ACCESS_KEY
ARG AWS_SECRET_KEY

ENV SECRET_KEY=${SECRET_KEY}
ENV HOST_BD=${HOST_BD}
ENV USER_BD=${USER_BD}
ENV PASS_BD=${PASS_BD}
ENV USER_BD_LOGIA=${USER_BD_LOGIA}
ENV PASS_BD_LOGIA=${PASS_BD_LOGIA}
ENV AES_KEY=${AES_KEY}
ENV AWS_ACCESS_KEY=${AWS_ACCESS_KEY}
ENV AWS_SECRET_KEY=${AWS_SECRET_KEY}

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

