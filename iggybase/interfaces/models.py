from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, relation, backref
from iggybase.interfaces.connections import SpinalBase


class ExpenseCodesExpensecode(SpinalBase):
    __tablename__ = "expense_codes_expensecode"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    active = Column(Boolean)
    start_date = Column(DateTime)
    expiration_date = Column(DateTime)
    tub = Column(String(3))
    org = Column(String(5))
    exp_object = Column(String(4))
    fund = Column(String(6))
    activity = Column(String(6))
    sub_activity = Column(String(4))
    root = Column(String(5))
    root_detail_id = Column(Integer)
    fullcode = Column(String(39))
