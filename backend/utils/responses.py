from flask import jsonify

def success_response(data=None, message="Operation successful", status_code=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status_code

def error_response(message="An error occurred", error_code="ERROR", status_code=400, data=None):
    return jsonify({
        "success": False,
        "message": message,
        "error_code": error_code,
        "data": data
    }), status_code
