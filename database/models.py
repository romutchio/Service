from database.database import Base
from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    """User Model"""

    __tablename__ = 'Users'

    ABONENT_ID = "abonent_id"
    ABONENT_NAME = "abonent_name"
    BALANCE = "balance"
    HOLDS = "holds"
    ACCOUNT_STATUS = "account_status"

    abonent_id = Column(UUID(as_uuid=True), unique=True, primary_key=True)
    abonent_name = Column(String(80))
    balance = Column(Integer)
    holds = Column(BigInteger)
    account_status = Column(Boolean)

    def __init__(self, abonent_id=None, abonent_name=None, balance=0, holds=0, account_status=None):
        self.abonent_id = abonent_id
        self.abonent_name = abonent_name
        self.balance = balance
        self.holds = holds
        self.account_status = account_status

    @property
    def serialize(self):
        return {
            User.ABONENT_ID: self.abonent_id,
            User.ABONENT_NAME: self.abonent_name,
            User.BALANCE: self.balance,
            User.HOLDS: self.holds,
            User.ACCOUNT_STATUS: self.account_status
        }
