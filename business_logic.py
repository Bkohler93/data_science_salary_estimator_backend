import pandas as pd
from prediction_model import PredictionModel
from salary_repository import SalaryRepository


class SalaryBLL:
    def __init__(self):
        self.model = PredictionModel()
        self.salary_repository = SalaryRepository()

    def get_attribute_names(self):
        attribute_names = self.salary_repository.get_unique_column_names()
        return attribute_names

    def get_avg_salary_data(self, job_title, attribute_name):
        result = self.salary_repository._get_avg_salary_for_job_col(
            job_title, attribute_name)
        return [r._asdict() for r in result]

    def predict_salary(self, experience_level, employment_type, job_title, company_location,
                       employee_residence, company_size, work_year):
        if self.check_parameters(experience_level, employment_type, job_title, company_location,
                                 employee_residence, company_size, work_year):
            return {'error': 'You are missing some parameters.'}

        predict_data = pd.DataFrame({
            'year': [work_year],
            'experience_level': [experience_level],
            'employment_type': [employment_type],
            'job_title': [job_title],
            'employee_residence': [employee_residence],
            'company_location': [company_location],
            'company_size': [company_size],
        })

        try:
            result = self.model.predict(predict_data)
            res = {'result': result}
        except Exception as e:
            return {
                'error': 'Invalid prediction. Something went wrong in the server.',
                'result': predict_data,
            }

        return res

    @staticmethod
    def check_parameters(*args):
        return any(arg is None for arg in args)
