from utils.api_helper import is_valid_amount, is_valid_abonent_id, create_response
from utils.hold_updater import HoldUpdater
from flask import Flask, jsonify, request
from database.database import db_session, init_db, init_default_values
from database.models import Abonent

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

    if Abonent.ABONENT_ID not in request.json:
        return False, create_response(400, False, f"Missing '{Abonent.ABONENT_ID}'")

    abonent_id = request.json[Abonent.ABONENT_ID]

    if not is_valid_abonent_id(abonent_id):
        return create_response(400, False, f"Invalid '{Abonent.ABONENT_ID}':'{abonent_id}', should be uuid v4")

    if 'amount' not in request.json:
        return False, create_response(400, False, "Missing 'amount'")

    amount_str = request.json['amount']

    if not is_valid_amount(amount_str):
        return create_response(400, False, "Field 'amount' should be int")

    amount = int(amount_str)
    abonent = Abonent.query.get(abonent_id)

    if abonent is not None:
        if not abonent.is_opened:
            return create_response(403, False, "Account is closed")
        abonent.balance += amount
        db_session.commit()
        return create_response(200, True, f"Successfully changed balance to '{abonent_id}'")

    return create_response(404, False, f"Abonent with {Abonent.ABONENT_ID}:{abonent_id} not found")


@app.route('/api/substract', methods=['PUT'])
def substract_balance():
    """Уменьшение баланса"""

    if Abonent.ABONENT_ID not in request.json:
        return False, create_response(400, False, f"Missing '{Abonent.ABONENT_ID}'")

    abonent_id = request.json[Abonent.ABONENT_ID]

    if not is_valid_abonent_id(abonent_id):
        return create_response(400, False, f"Invalid '{Abonent.ABONENT_ID}':'{abonent_id}', should be uuid v4")

    if 'amount' not in request.json:
        return False, create_response(400, False, "Missing 'amount'")

    amount_str = request.json['amount']

    if not is_valid_amount(amount_str):
        return create_response(400, False, "Field 'amount' should be int")

    amount = int(amount_str)
    abonent = Abonent.query.get(abonent_id)

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

    return create_response(404, False, f"Abonent with '{Abonent.ABONENT_ID}':'{abonent_id}' not found")


@app.route('/api/status', methods=['GET'])
def get_status():
    """Статус по счету: остаток по балансу, открыт/закрыт счет"""

    if Abonent.ABONENT_ID not in request.args:
        return create_response(400, False, 'Missing "{}"'.format(Abonent.ABONENT_ID))

    abonent_id = request.args.get(Abonent.ABONENT_ID)

    if not is_valid_abonent_id(abonent_id):
        return create_response(400, False, f"Invalid '{Abonent.ABONENT_ID}':'{abonent_id}', should be uuid v4")

    abonent = Abonent.query.get(abonent_id)

    if abonent is not None:
        return create_response(200, True, abonent.status, "Abonent status")
    return create_response(404, False, f"Abonent '{Abonent.ABONENT_ID}':'{abonent_id}' not found")


@app.route('/api/add_abonent', methods=['POST'])
def add_abonent():
    """Добавить пользователя"""

    if Abonent.ABONENT_ID not in request.json or not is_valid_abonent_id(request.json[Abonent.ABONENT_ID]):
        return create_response(400, False, f"Error in field '{Abonent.ABONENT_ID}'", '')

    if Abonent.ABONENT_NAME not in request.json:
        return create_response(400, False, f"Error in field '{Abonent.ABONENT_NAME}'", '')

    if Abonent.BALANCE not in request.json or not is_valid_amount(request.json[Abonent.BALANCE]):
        return create_response(400, False, f"Error in field '{Abonent.BALANCE}'", '')

    if Abonent.HOLDS not in request.json or not is_valid_amount(request.json[Abonent.HOLDS]):
        return create_response(400, False, f"Error in field '{Abonent.HOLDS}'", '')

    if Abonent.ACCOUNT_STATUS not in request.json or not isinstance(request.json[Abonent.ACCOUNT_STATUS], bool):
        return create_response(400, False, f"Error in field '{Abonent.ACCOUNT_STATUS }'", '')

    account_id = request.json[Abonent.ABONENT_ID]
    account_name = request.json[Abonent.ABONENT_NAME]
    balance = request.json[Abonent.BALANCE]
    holds = request.json[Abonent.HOLDS]
    account_status = request.json[Abonent.ACCOUNT_STATUS]

    abonent = Abonent(account_id, account_name, balance, holds, account_status)
    if Abonent.query.get(account_id) is None:
        # TODO: add retry system
        db_session.add(abonent)
        db_session.commit()
        return create_response(200, True, abonent.serialize, "Successfully added new abonent")
    return create_response(400, False, f"Duplicate key: {account_id}")


@app.route('/api/get_abonents', methods=['GET'])
def get_abonents():
    """Получить всех пользователей"""

    abonents = Abonent.query.all()
    return jsonify([i.serialize for i in abonents])


if __name__ == '__main__':
    init_db()
    init_default_values()

    hold_updater = HoldUpdater(app.logger)
    hold_updater.start()

    app.run(host='0.0.0.0', debug=True)
