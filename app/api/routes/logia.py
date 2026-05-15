from flask import Blueprint, jsonify, request
import logging
import os

logia_bp = Blueprint('logia', __name__)

@logia_bp.route('/logia/<path:subpath>', methods=['POST', 'GET'])
def gran_logia_process(subpath):
    from app.legacy.granl import GranLogia
    root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    gl = GranLogia(root_dir)
    data, code = gl.request_process(request, subpath)
    del gl
    return data, code
