from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
import datetime

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(String, primary_key=True, index=True)
    nome = Column(String, index=True)
    cnpj = Column(String, index=True)
    banco = Column(String)
    ag = Column(String)
    conta = Column(String)
    grupo = Column(String)
    resp = Column(String)
    omie_app_key = Column(String, nullable=True)
    omie_app_secret = Column(String, nullable=True)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    text = Column(String)
    done = Column(Boolean, default=False)
    status = Column(String, default="todo") # todo, doing, done
    prio = Column(String, default="normal")
    due = Column(String, nullable=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
