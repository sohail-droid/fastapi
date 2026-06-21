from database import Base
from sqlalchemy import Column, Integer, String, Boolean


class Todos(Base):
    __tablename__ = 'todos'   # This is the name of the table in the database 

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    Description = Column(String)
    Priority = Column(Integer)
    complete = Column(Boolean, default=False)



