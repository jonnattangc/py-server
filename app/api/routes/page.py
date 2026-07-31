from flask import Blueprint, jsonify, request, render_template, send_from_directory
from markupsafe import escape
import logging
import os

page_bp = Blueprint('page', __name__)

def _escape_response_data(value):
    if isinstance(value, dict):
        return {k: _escape_response_data(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_escape_response_data(item) for item in value]
    if isinstance(value, str):
        return str(escape(value))
    return value

@page_bp.get('/page')
def page_page():
    from app.legacy.pageprocessor import Page
    page = Page()
    data_response, http_status, is_page = page.request_process(request, "web")
    del page
    if is_page:
        return data_response, http_status
    else:
        return jsonify(_escape_response_data(data_response)), http_status

@page_bp.post('/page/csrf')
def csrf_token():
    logging.info('# Reciv ' + str(request.method) + ' Contex: /page/csrf')
    logging.info("# Reciv Header: " + str(request.headers))
    logging.info("# Reciv Data :\n" + str(request.data))
    logging.info("# Reciv Form :\n" + str(request.form))
    logging.info("# Reciv Cookies :\n" + str(request.cookies))
    return render_template('galery.html')

from app.extensions import csrf
@page_bp.post('/page/<path:subpath>')
@csrf.exempt
def post_page(subpath):
    from app.legacy.pageprocessor import Page
    page = Page()
    data_response, http_status, is_page = page.request_process(request, str(subpath))
    del page
    if is_page:
        return data_response, http_status
    else:
        return jsonify(_escape_response_data(data_response)), http_status


@page_bp.route('/page/<path:subpath>', methods=['GET', 'PUT'])
def process_page(subpath):
    from app.legacy.pageprocessor import Page
    page = Page()
    data_response, http_status, is_page = page.request_process(request, str(subpath))
    del page
    if is_page:
        return data_response, http_status
    else:
        return jsonify(_escape_response_data(data_response)), http_status

@page_bp.get('/page/image/<path:subpath>')
def process_image(subpath):
    return file_process('images', str(subpath))

@page_bp.get('/page/js/<path:subpath>')
def process_js(subpath):
    return file_process('js', str(subpath))

def file_process(type_file: str, path: str):
    try:
        path_split = path.split('/')
        if len(path_split) > 1:
            path_split = path_split[len(path_split) - 1]
        else:
            path_split = path
        file_name: str = path_split.replace('%20', ' ')
        file_name = file_name.strip()
        tmp_name = file_name.lower()
        if tmp_name.find('.jpeg') > 0 or tmp_name.find('.png') > 0 or tmp_name.find('.jpg') > 0 or tmp_name.find('.js') > 0:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static')
            file_path = os.path.join(file_path, type_file)
            return send_from_directory(file_path, str(file_name)), 200
    except Exception as e:
        print("ERROR file_process:", e)
        return None, 404
    return None, 404
