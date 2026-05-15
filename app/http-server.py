#!/usr/bin/python
"""Entry point for the Flask application."""

import logging
import sys

from app import create_app

logger = logging.getLogger('HTTP')

if __name__ == "__main__":
    listen_port = 8085
    if len(sys.argv) == 1:
        logger.error("Se requiere el puerto como parametro")
        exit(0)
    try:
        logger.info("Server listen at: " + sys.argv[1])
        listen_port = int(sys.argv[1])
        app = create_app()
        app.run(host='0.0.0.0', port=listen_port)
    except Exception as e:
        print("ERROR MAIN:", e)

    logging.info("PROGRAM FINISH")
