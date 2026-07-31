FROM python:3.14.1-alpine3.21

LABEL VERSION=2.0
LABEL DESCRIPCION="Python Server HTTP V2.0"

ENV FLASK_APP app
ENV FLASK_DEBUG development

RUN adduser -h /home/jonnattan -u 10100 -g 10101 --disabled-password jonnattan

COPY ./requirements.txt /home/jonnattan/requirements.txt

RUN cd /home/jonnattan && \
    mkdir -p /home/jonnattan/.local/bin && \
    export PATH=$PATH:/home/jonnattan/.local/bin && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    chmod -R 755 /home/jonnattan  && \
    chown -R jonnattan:jonnattan /home/jonnattan

WORKDIR /home/jonnattan

USER jonnattan

EXPOSE 8085

CMD [ "python", "app/http-server.py", "8085"]
# python3 http-server.py 8085
# CMD [ "tail", "-f", "/home/jonnattan/requirements.txt" ]
# pip freeze > requirements.txt
