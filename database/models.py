from database.database import Base
from sqlalchemy import Column, String, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class Abonent(Base):
    """User Model"""

    __tablename__ = 'Abonents'

    ABONENT_ID = "abonent_id"
    ABONENT_NAME = "abonent_name"
    BALANCE = "balance"
    HOLDS = "holds"
    ACCOUNT_STATUS = "account_status"

    abonent_id = Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid4)
    abonent_name = Column(String(200))
    balance = Column(BigInteger)
    holds = Column(BigInteger)
    is_opened = Column(Boolean)

    def __init__(self, abonent_id: str, abonent_name: str, balance: int, holds: int, is_opened: bool):
        self.abonent_id = abonent_id
        self.abonent_name = abonent_name
        self.balance = balance
        self.holds = holds
        self.is_opened = is_opened

    @property
    def serialize(self):
        return {
            Abonent.ABONENT_ID: self.abonent_id,
            Abonent.ABONENT_NAME: self.abonent_name,
            Abonent.BALANCE: self.balance,
            Abonent.HOLDS: self.holds,
            Abonent.ACCOUNT_STATUS: 'Открыт' if self.is_opened else 'Закрыт'
        }

    @property
    def status(self):
        return {
            Abonent.BALANCE: self.balance,
            Abonent.HOLDS: self.holds,
            Abonent.ACCOUNT_STATUS: 'Открыт' if self.is_opened else 'Закрыт'
        }

