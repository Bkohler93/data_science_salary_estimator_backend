from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine

Base = declarative_base()


class Salary(Base):
    __tablename__ = 'salaries'
    id = Column(Integer, primary_key=True)
    job_title = Column(String)
    employment_type = Column(String)
    experience_level = Column(String)
    company_location = Column(String)
    salary = Column(Integer)
    employee_residence = Column(String)
    company_size = Column(String)
    year = Column(Integer)
