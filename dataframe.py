import pandas as pd
from config import DATASET_PATH

# This class stores the data from processed_dataset.csv into Pandas dataframe


class SalaryDataFrame:
    def __init__(self):
        salary_csv_path = DATASET_PATH
        self.df = pd.read_csv(salary_csv_path)

    def drop(self, columns):
        return self.df.drop(columns=columns)

    def to_sql(self, table_name, connection):
        self.df.to_sql(table_name, con=connection)
