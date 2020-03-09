from utils.api_helper import is_valid_amount, is_valid_abonent_id, create_response
from utils.hold_updater import HoldUpdater
from flask import Flask, jsonify, request
from database.database import db_session, init_db, init_default_values
from database.models import User

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

    return create_response(200, True, 'Running', 'Server status')


@app.route('/api/add', methods=['PUT'])
def add_balance():
    """Пополнение баланса"""

    if User.ABONENT_ID not in request.json:
        return False, create_response(400, False, f"Missing '{User.ABONENT_ID}'")

    abonent_id = request.json[User.ABONENT_ID]

    if not is_valid_abonent_id(abonent_id):
        return create_response(400, False, f"Invalid '{User.ABONENT_ID}':'{abonent_id}', should be uuid v4")

    if 'amount' not in request.json:
        return False, create_response(400, False, "Missing 'amount'")

    amount_str = request.json['amount']

    if not is_valid_amount(amount_str):
        return create_response(400, False, "Field 'amount' should be int")

    amount = int(amount_str)
    abonent = User.query.get(abonent_id)

    if abonent is not None:
        if not abonent.is_opened:
            return create_response(403, False, "Account is closed")
        abonent.balance += amount
        db_session.commit()
        return create_response(200, True, f"Successfully changed balance to '{abonent_id}'")

    return create_response(404, False, f"Abonent with {User.ABONENT_ID}:{abonent_id} not found")


@app.route('/api/substract', methods=['PUT'])
def substract_balance():
    """Уменьшение баланса"""

    if User.ABONENT_ID not in request.json:
        return False, create_response(400, False, f"Missing '{User.ABONENT_ID}'")

    abonent_id = request.json[User.ABONENT_ID]

    if not is_valid_abonent_id(abonent_id):
        return create_response(400, False, f"Invalid '{User.ABONENT_ID}':'{abonent_id}', should be uuid v4")

    if 'amount' not in request.json:
        return False, create_response(400, False, "Missing 'amount'")

    amount_str = request.json['amount']

    if not is_valid_amount(amount_str):
        return create_response(400, False, "Field 'amount' should be int")

    amount = int(amount_str)
    abonent = User.query.get(abonent_id)

    if abonent is not None:
        if not abonent.is_opened:
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

    if not is_valid_abonent_id(abonent_id):
        return create_response(400, False, f"Invalid '{User.ABONENT_ID}':'{abonent_id}', should be uuid v4")

    abonent = User.query.get(abonent_id)

    if abonent is not None:
        return create_response(200, True, abonent.status, "Abonent status")
    return create_response(404, False, f"Abonent '{User.ABONENT_ID}':'{abonent_id}' not found")


@app.route('/api/add_user', methods=['POST'])
def add_user():
    """Добавить пользователя"""

    if User.ABONENT_ID not in request.json or not is_valid_abonent_id(request.json[User.ABONENT_ID]):
        return create_response(400, False, f"Error in field '{User.ABONENT_ID}'", '')

    if User.ABONENT_NAME not in request.json:
        return create_response(400, False, f"Error in field '{User.ABONENT_NAME}'", '')

    if User.BALANCE not in request.json or not is_valid_amount(request.json[User.BALANCE]):
        return create_response(400, False, f"Error in field '{User.BALANCE}'", '')

    if User.HOLDS not in request.json or not is_valid_amount(request.json[User.HOLDS]):
        return create_response(400, False, f"Error in field '{User.HOLDS}'", '')

    if User.ACCOUNT_STATUS not in request.json or not isinstance(request.json[User.ACCOUNT_STATUS], bool):
        return create_response(400, False, f"Error in field '{User.ACCOUNT_STATUS }'", '')

    account_id = request.json[User.ABONENT_ID]
    account_name = request.json[User.ABONENT_NAME]
    balance = request.json[User.BALANCE]
    holds = request.json[User.HOLDS]
    account_status = request.json[User.ACCOUNT_STATUS]

    user = User(account_id, account_name, balance, holds, account_status)
    if User.query.get(account_id) is None:
        # TODO: add retry system
        db_session.add(user)
        db_session.commit()
        return create_response(200, True, user.serialize, "Successfully added new user")
    return create_response(400, False, f"Duplicate key: {account_id}")


@app.route('/api/get_users', methods=['GET'])
def get_users():
    """Получить всех пользователей"""

    users = User.query.all()
    return jsonify([i.serialize for i in users])


if __name__ == '__main__':
    init_db()
    init_default_values()

    hold_updater = HoldUpdater(app.logger)
    hold_updater.start()

    app.run(host='0.0.0.0', debug=True)
