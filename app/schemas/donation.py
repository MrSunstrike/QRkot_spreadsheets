from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt = Field(...)
    comment: Optional[str]


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationCreate):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationProcessorDB(DonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]
