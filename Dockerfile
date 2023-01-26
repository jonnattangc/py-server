FROM python:3.9-slim

LABEL VERSION=1.1
LABEL DESCRIPCION="Python Server HTTP V2"

ENV FLASK_APP app
ENV FLASK_DEBUG development

# variables importantes
ENV SECRET_KEY ''
ENV HOST_BD ''
ENV USER_BD ''
ENV PASS_BD ''
ENV AES_KEY ''
ENV AWS_ACCESS_KEY ''
ENV AWS_SECRET_KEY ''

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip && \
    pip3 install -r requirements.txt

EXPOSE 8085

CMD [ "python3", "http-server.py", "8085"]
# python3 http-server.py 8085
# CMD [ "/bin/sh", "./run.sh" ]

