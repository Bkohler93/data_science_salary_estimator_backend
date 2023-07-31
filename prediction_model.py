import pickle
from sklearn.compose import ColumnTransformer

from sklearn.preprocessing import OneHotEncoder
from config import MODEL_PATH
from dataframe import SalaryDataFrame


class PredictionModel:
    def __init__(self):
        # initialize encoder to encode incoming prediction categorical values to one hot encoded values
        ohe = OneHotEncoder(drop='first')
        categorical_cols = ['job_title', 'employment_type', 'experience_level',
                            'company_location', 'employee_residence', 'company_size']
        self.ct = ColumnTransformer(
            transformers=[('encoder', ohe, categorical_cols)], remainder='passthrough')

        df = SalaryDataFrame()
        X = df.drop(columns=['salary'])
        self.ct.fit_transform(X)

        model_path = MODEL_PATH
        self.model = pickle.load(open(model_path, "rb"))

    def predict(self, predict_data):
        encoded_data = self.ct.transform(predict_data)
        return self.model.predict(encoded_data)[0]
