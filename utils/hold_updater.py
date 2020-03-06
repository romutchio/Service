from threading import Timer
from multiprocessing.dummy import Pool
from database.database import db_session
from database.models import User


class HoldUpdater:
    def __init__(self, logger, interval=10 * 60):
        self.logger = logger
        self.interval = interval
        self.demon_thread = None
        self.pool = Pool(4)

    def start(self):
        self._run()

    def _run(self) -> None:
        self.logger.info('Starting update holds')
        self.update_balances()
        Timer(self.interval, self._run).start()

    def update_balances(self) -> None:
        abonent_ids = [user.abonent_id for user in User.query.all()]
        self.pool.map(self.process_user, abonent_ids)

    def process_user(self, abonent_id):
        user = User.query.get(abonent_id)
        holds = user.holds
        user.balance -= holds
        user.holds = 0
        db_session.commit()
