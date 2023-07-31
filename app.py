
# This creates the model to predict Data Science Salaries and allows a frontend
# application to retrieve results from the model as well as the raw data
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pandas as pd
import decimal
import datetime
import json
import urllib.parse

from prediction_model import PredictionModel
from salary_repository import SalaryRepository

# initialize the linear regression model to predict salaries
model = PredictionModel()

# initialize repository to query database
salary_repository = SalaryRepository()

app = Flask(__name__)

# allow cross-site requests (frontend application)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)


@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello from Flask!'


@app.route('/attribute_names', methods=["GET"])
def send_attribute_names():
    attribute_names = salary_repository.get_unique_column_names()
    return json.dumps(attribute_names)


@app.route('/avg_salary_data', methods=["GET"])
def send_avg_salary_data():
    job_title = urllib.parse.unquote(request.args.get('job_title', ''))
    attribute_name = urllib.parse.unquote(request.args.get('field', ''))
    result = salary_repository._get_avg_salary_for_job_col(
        job_title, attribute_name)
    return json.dumps([r._asdict() for r in result], default=alchemyencoder)

# example URL /predict?experience_level=High&employment_type=Full-Time&job_title=Data-Scientist&
#               company_location=Australia&employee_residence=Australia&company_size=Medium&
#               work_year=2022


@app.route('/predict', methods=["GET"])
def predict_salary():

    experience_level = urllib.parse.unquote(
        request.args.get('experience_level', ''))
    employment_type = urllib.parse.unquote(
        request.args.get('employment_type', ''))
    job_title = urllib.parse.unquote(request.args.get('job_title', ''))
    company_location = urllib.parse.unquote(
        request.args.get('company_location', ''))
    employee_residence = urllib.parse.unquote(
        request.args.get('employee_residence', ''))
    company_size = urllib.parse.unquote(request.args.get('company_size', ''))
    work_year = urllib.parse.unquote(request.args.get('work_year', ''))

    if check_parameters(experience_level, employment_type, job_title, company_location,
                        employee_residence, company_size, work_year):
        return jsonify({
            'error': 'You are missing some parameters.',
        })

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
        result = model.predict(predict_data)
        res = {
            'result': result
        }
    except:
        return jsonify({
            'error': 'Invalid prediction. Something went wrong in the server.',
            'result': predict_data.to_string()
        })

    return jsonify(res)


def check_parameters(*args):
    if any(arg is None for arg in args):
        return True
    else:
        return False
