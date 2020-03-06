from utils.helpers import is_int, is_valid_uuid
from utils.hold_updater import HoldUpdater
from flask import Flask, jsonify, request
from database.database import db_session
from database.models import User
from database import database

import logging
import os

app = Flask(__name__)

app.logger.setLevel(logging.INFO)

app.secret_key = os.environ['APP_SECRET_KEY']


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/ping', methods=['GET'])
def ping_service():
    """Работоспособность сервиса"""

    return jsonify(
        status=200,
        result=True,
        addition='Running',
        description='Server status'
    )


@app.route('/api/add', methods=['PUT'])
def add_balance():
    """Пополнение баланса"""

    (is_valid_abonent, abonent_validation_result) = validate_user(request)
    if not is_valid_abonent:
        return abonent_validation_result

    (is_valid_amount, amount_validation_result) = validate_amount(request)
    if not is_valid_amount:
        return amount_validation_result

    abonent_id = abonent_validation_result
    amount = amount_validation_result
    abonent = User.query.get(abonent_id)

    if abonent is not None:
        if not abonent.account_status:
            return create_response(403, False, "Account is closed")
        abonent.balance += amount
        db_session.commit()
        return create_response(200, True, f"Successfully changed balance to '{abonent_id}'")

    return create_response(404, False, f"Abonent with {User.ABONENT_ID}:{abonent_id} not found")


@app.route('/api/substract', methods=['PUT'])
def substract_balance():
    """Уменьшение баланса"""

    (is_valid_abonent, abonent_validation_result) = validate_user(request)
    if not is_valid_abonent:
        return abonent_validation_result

    (is_valid_amount, amount_validation_result) = validate_amount(request)
    if not is_valid_amount:
        return amount_validation_result

    abonent_id = abonent_validation_result
    amount = amount_validation_result
    abonent = User.query.get(abonent_id)

    if abonent is not None:
        if not abonent.account_status:
            return create_response(403, False, "Account is closed")
        result = abonent.balance - abonent.holds - amount
        if result >= 0:
            abonent.balance = result
            db_session.commit()
            return create_response(200, True, f"Successfully changed balance to '{abonent_id}'")
        return create_response(403, False, 'Substraction is not available',
                               'Not enough balance for substraction considering holds')

    return create_response(404, False, f"Abonent with '{User.ABONENT_ID}':'{abonent_id}' not found")


@app.route('/api/status', methods=['GET'])
def get_status():
    """Статус по счету: остаток по балансу, открыт/закрыт счет"""

    if User.ABONENT_ID not in request.args:
        return create_response(400, False, 'Missing "{}"'.format(User.ABONENT_ID))

    abonent_id = request.args.get(User.ABONENT_ID)

    if not is_valid_uuid(abonent_id):
        return create_response(400, False, f"Invalid '{User.ABONENT_ID}':'{abonent_id}', should be uuid v4")

    abonent = User.query.get(abonent_id)

    if abonent is not None:
        return create_response(200, True, abonent.status, "Abonent status")
    return create_response(404, False, f"Abonent '{User.ABONENT_ID}':'{abonent_id}' not found")


def validate_user(request):
    if User.ABONENT_ID not in request.json:
        return False, create_response(400, False, f"Missing '{User.ABONENT_ID}'")

    abonent_id = request.json[User.ABONENT_ID]

    if not is_valid_uuid(abonent_id):
        return False, create_response(400, False, f"Invalid '{User.ABONENT_ID}':'{abonent_id}', should be uuid v4")

    return True, abonent_id


def validate_amount(request):
    if 'amount' not in request.json:
        return False, create_response(400, False, "Missing 'amount'")
    amount_str = request.json['amount']
    if not is_int(amount_str):
        return False, create_response(400, False, "Field 'amount' should be int")

    return True, int(amount_str)


def create_response(status: int, result: bool = True, addition: str = '', description: str = ""):
    return jsonify(
        status=status,
        result=result,
        addition=addition,
        description=description
    ), status


@app.route('/api/add_user', methods=['POST'])
def add_user():
    """Добавить пользователя"""

    if User.ABONENT_ID not in request.json:
        return create_response(400, False, f"Missing '{User.ABONENT_ID}'", '')

    if User.ABONENT_NAME not in request.json:
        return create_response(400, False, f"Missing '{User.ABONENT_NAME}'", '')

    if User.BALANCE not in request.json:
        return create_response(400, False, f"Missing '{User.BALANCE}'", '')

    if User.HOLDS not in request.json:
        return create_response(400, False, f"Missing '{User.HOLDS}'", '')

    if User.ACCOUNT_STATUS not in request.json:
        return create_response(400, False, f"Missing '{User.ACCOUNT_STATUS }'", '')

    account_id = request.json[User.ABONENT_ID]
    account_name = request.json[User.ABONENT_NAME]
    balance = request.json[User.BALANCE]
    holds = request.json[User.HOLDS]
    account_status = request.json[User.ACCOUNT_STATUS]

    user = User(account_id, account_name, balance, holds, account_status)
    # TODO: обработка ошибки
    db_session.add(user)
    db_session.commit()
    return create_response(200, True, "Successfully added new user", jsonify(user.serialize))


@app.route('/api/get_users', methods=['POST'])
def get_users():
    """Получить всех пользователей"""

    users = User.query.all()
    return jsonify([i.serialize for i in users])


def database_initialization_sequence():
    test_data = [
        User('26c940a1-7228-4ea2-a3bc-e6460b172040', 'Петров Иван Сергеевич', 1700, 300, True),
        User('7badc8f8-65bc-449a-8cde-855234ac63e1', 'Kazitsky Jason', 200, 200, True),
        User('5597cc3d-c948-48a0-b711-393edf20d9c0', 'Пархоменко Антон Александрович', 10, 300, True),
        User('867f0924-a917-4711-939b-90b179a96392', 'Петечкин Петр Измаилович', 1000000, 1, False)
    ]
    db_session.query(User).delete()
    db_session.add_all(test_data)
    db_session.commit()


if __name__ == '__main__':
    database.init_db()
    database_initialization_sequence()

    hold_updater = HoldUpdater(app.logger)
    hold_updater.start()

    app.run(host='0.0.0.0', debug=True)
