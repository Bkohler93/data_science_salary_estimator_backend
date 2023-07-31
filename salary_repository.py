from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from config import DB_DRIVER, DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USERNAME
from dataframe import SalaryDataFrame

from model import Base, Salary


class SalaryRepository:
    def __init__(self):
        # initialize db connection
        db_config = {
            'engine': DB_DRIVER,
            'username': DB_USERNAME,
            'password': DB_PASSWORD,
            'host': DB_HOST,
            'port': DB_PORT,
            'database': DB_NAME,
        }

        db_url = f"{db_config['engine']}://{db_config['username']}:{db_config['password']}@{db_config['host']}{db_config['port']}/{db_config['database']}"

        # pool recycle 280 is required for PythonAnywhere sql db to function correctly
        engine = create_engine(db_url, pool_recycle=280)

        # fill database if empty
        with engine.connect() as conn:
            tableList = conn.execute(text(
                "SELECT 1 FROM information_schema.tables WHERE table_name = 'salaries';")).fetchall()
            if len(tableList) == 0:
                # create and fill table
                df = SalaryDataFrame()
                df.to_sql('salaries', connection=engine)

        Base.metadata.create_all(engine)

        # create session
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def _get_avg_salary_for_job_col(self, job_title, attribute_name):
        stmt = (
            self.session.query(getattr(Salary, attribute_name), func.avg(
                Salary.salary).label('salary'))
            .filter(Salary.job_title == job_title)
            .group_by(getattr(Salary, attribute_name))
            .limit(7)
        )

        return stmt.all()

    def get_unique_column_names(self):

        comp_size_res = self._execute_unique_column_values_query(
            Salary.company_size)
        comp_loc_res = self._execute_unique_column_values_query(
            Salary.company_location)
        emp_residence_res = self._execute_unique_column_values_query(
            Salary.employee_residence)
        job_title_res = self._execute_unique_column_values_query(
            Salary.job_title)
        emp_type_res = self._execute_unique_column_values_query(
            Salary.employment_type)
        exp_lvl_res = self._execute_unique_column_values_query(
            Salary.experience_level)

        return {
            'experience_level': [d._asdict()['experience_level'] for d in exp_lvl_res],
            'employment_type': [d._asdict()['employment_type'] for d in emp_type_res],
            'job_title': [d._asdict()['job_title'] for d in job_title_res],
            'employee_residence': [d._asdict()['employee_residence'] for d in emp_residence_res],
            'company_location': [d._asdict()['company_location'] for d in comp_loc_res],
            'company_size': [d._asdict()['company_size'] for d in comp_size_res],
        }

    def _execute_unique_column_values_query(self, column_name):
        return (
            self.session.query(column_name)
            .group_by(column_name)
            .order_by(func.count().desc())
            .all()
        )
