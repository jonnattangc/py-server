from flask import Blueprint, jsonify, request
import logging

mail_bp = Blueprint('mail', __name__)

@mail_bp.route('/mail/<path:subpath>', methods=['POST', 'GET'])
def mail_process(subpath):
    from app.legacy.utilmail import MailProcess
    mp = MailProcess()
    data, code = mp.request_process(request, subpath)
    del mp
    return data, code
