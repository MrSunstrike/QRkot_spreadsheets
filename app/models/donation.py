from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.abstract import InvestBase


class Donation(InvestBase):
    """Donation model."""
    user_id: int = Column(Integer, ForeignKey("user.id"))
    comment: str = Column(Text)
