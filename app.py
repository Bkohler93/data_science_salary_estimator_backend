from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from business_logic import SalaryBLL

app = Flask(__name__)

# allow cross-site requests (frontend application)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

salary_bll = SalaryBLL()


@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello from Flask!'


@app.route('/attribute_names', methods=["GET"])
def send_attribute_names():
    column_name = request.args.get('column_name', '')
    attribute_names = salary_bll.get_attribute_names(column_name)
    return jsonify(attribute_names)


@app.route('/avg_salary_data', methods=["GET"])
def send_avg_salary_data():
    job_title = request.args.get('job_title', '')
    attribute_name = request.args.get('field', '')
    result = salary_bll.get_avg_salary_data(job_title, attribute_name)
    return jsonify(result)


@app.route('/predict', methods=["GET"])
def predict_salary():
    experience_level = request.args.get('experience_level', '')
    employment_type = request.args.get('employment_type', '')
    job_title = request.args.get('job_title', '')
    company_location = request.args.get('company_location', '')
    employee_residence = request.args.get('employee_residence', '')
    company_size = request.args.get('company_size', '')
    work_year = request.args.get('work_year', '')

    result = salary_bll.predict_salary(experience_level, employment_type, job_title, company_location,
                                       employee_residence, company_size, work_year)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
