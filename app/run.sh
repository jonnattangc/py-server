#!/bin/sh
# export FLASK_APP=app
# export FLASK_DEBUG=development
echo "N de parametros: $#"
# python3 http-server.py 8085
echo "Se pega con los logs"
tail -f /usr/src/app/logger.log
