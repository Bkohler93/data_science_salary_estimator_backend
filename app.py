
# This creates the model to predict Data Science Salaries and allows a frontend
# application to retrieve results from the model as well as the raw data
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pandas as pd
import pickle
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sqlalchemy import create_engine, text, select, MetaData, Table, func
from config import DB_DRIVER, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DATASET_PATH, MODEL_PATH
import decimal, datetime
import json
import urllib.parse

# load dataset for frontend to retrieve
salary_csv_path = DATASET_PATH
df = pd.read_csv(salary_csv_path)

# load model
lr_model_path = MODEL_PATH
model = pickle.load(open(lr_model_path, "rb"))

# initializer encoder for categorical features in model
ohe = OneHotEncoder(drop='first')
categorical_cols = ['job_title', 'employment_type', 'experience_level',
                    'company_location', 'employee_residence', 'company_size']
ct = ColumnTransformer(transformers=[('encoder', ohe, categorical_cols)], remainder='passthrough')

X = df.drop(columns=['salary'])

# fit the transform
ct.fit_transform(X)

# initialize db connection
db_config = {
	'engine': DB_DRIVER,
	'username': DB_USERNAME,
	'password': DB_PASSWORD,
	'host': DB_HOST,
	'port': DB_PORT,
	'database': DB_NAME,
}

# construct database config string
# 'mysql+pymysql://PASSWORD:PASSWORD@HOST:PORT$DATABASE'

db_config_str = f"{db_config['engine']}://{db_config['username']}:{db_config['password']}@{db_config['host']}{db_config['port']}/{db_config['database']}"
engine = create_engine(db_config_str, pool_recycle=280)

with engine.connect() as conn:
    tableList = conn.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name = 'salaries';")).fetchall();
    if len(tableList) == 0:
        # create and fill table
        df.to_sql('salaries', con=engine)

# create schema for sqlalchemy
metadata_obj = MetaData()
salary_table = Table("salaries", metadata_obj, autoload_with=engine)

app = Flask(__name__)

# allow cross-site requests (frontend application)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# if __name__ == '__main__':
#     # Set the default port to 5000
#     default_port = 5000
#     app.run(port=default_port)

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
    with engine.connect() as conn:


        # Prepared statements are not needed because SQL statements cannot be altered from outside the application
        exp_lvl_stmt = text("SELECT experience_level FROM ( SELECT experience_level, COUNT(*) AS field_count FROM salaries GROUP BY experience_level) AS counted_fields ORDER BY field_count DESC")
        emp_type_stmt = text("SELECT employment_type FROM ( SELECT employment_type, COUNT(*) AS field_count FROM salaries GROUP BY employment_type) AS counted_fields ORDER BY field_count DESC")
        job_title_stmt = text("SELECT job_title FROM ( SELECT job_title, COUNT(*) AS field_count FROM salaries GROUP BY job_title) AS counted_fields ORDER BY field_count DESC")
        emp_res_stmt = text("SELECT employee_residence FROM ( SELECT employee_residence, COUNT(*) AS field_count FROM salaries GROUP BY employee_residence) AS counted_fields ORDER BY field_count DESC")
        comp_loc_stmt = text("SELECT company_location FROM ( SELECT company_location, COUNT(*) AS field_count FROM salaries GROUP BY company_location) AS counted_fields ORDER BY field_count DESC")
        comp_size_stmt = text("SELECT company_size FROM ( SELECT company_size, COUNT(*) AS field_count FROM salaries GROUP BY company_size) AS counted_fields ORDER BY field_count DESC")

        exp_lvl_res = conn.execute(exp_lvl_stmt).all()
        emp_type_res = conn.execute(emp_type_stmt).all()
        job_title_res = conn.execute(job_title_stmt).all()
        emp_residence_res = conn.execute(emp_res_stmt).all()
        comp_loc_res = conn.execute(comp_loc_stmt).all()
        comp_size_res = conn.execute(comp_size_stmt).all()

    attribute_names = {
        'experience_level': [d._asdict()['experience_level'] for d in exp_lvl_res],
        'employment_type': [d._asdict()['employment_type'] for d in emp_type_res],
        'job_title': [d._asdict()['job_title'] for d in job_title_res],
        'employee_residence': [d._asdict()['employee_residence'] for d in emp_residence_res],
        'company_location': [d._asdict()['company_location'] for d in comp_loc_res],
        'company_size': [d._asdict()['company_size'] for d in comp_size_res],
        }

    return json.dumps(attribute_names)

@app.route('/avg_salary_data', methods=["GET"])
def send_avg_salary_data():
    job_title = urllib.parse.unquote(request.args.get('job_title', ''))
    field = urllib.parse.unquote(request.args.get('field', ''))

    with engine.connect() as conn:
        stmt = select(salary_table.c[field], func.avg(salary_table.c.salary).label('salary')).where(salary_table.c.job_title == job_title).group_by(salary_table.c[field]).limit(7)
        result = conn.execute(stmt).all()

    return json.dumps([r._asdict() for r in result], default=alchemyencoder)
    # return jsonify(data[0])

# example URL /predict?experience_level=High&employment_type=Full-Time&job_title=Data-Scientist&
#               company_location=Australia&employee_residence=Australia&company_size=Medium&
#               work_year=2022
@app.route('/predict', methods=["GET"])
def predict_salary():

    experience_level = urllib.parse.unquote(request.args.get('experience_level', ''))
    employment_type = urllib.parse.unquote(request.args.get('employment_type', ''))
    job_title = urllib.parse.unquote(request.args.get('job_title', ''))
    company_location = urllib.parse.unquote(request.args.get('company_location', ''))
    employee_residence = urllib.parse.unquote(request.args.get('employee_residence', ''))
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
        encoded_data = ct.transform(predict_data)
        result = model.predict(encoded_data)[0]
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
