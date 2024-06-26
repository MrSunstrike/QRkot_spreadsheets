from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer

from app.core.db import Base


class InvestBase(Base):
    __abstract__ = True

    full_amount: int = Column('full_amount', Integer, nullable=False)
    invested_amount: int = Column('invested_amount', Integer, default=0)
    fully_invested: bool = Column('fully_invested', Boolean, default=False)
    create_date: datetime = Column('create_date', DateTime,
                                   default=datetime.now)
    close_date: datetime = Column('close_date', DateTime)
