from utils.helpers import is_valid_uuid, is_int
from flask import jsonify


def is_valid_abonent_id(abonent_id):
    return is_valid_uuid(abonent_id)


def is_valid_amount(amount):
    return is_int(amount)


def create_response(status: int, result: bool = True, addition: str = '', description: str = ""):
    return jsonify(
        status=status,
        result=result,
        addition=addition,
        description=description
    ), status
