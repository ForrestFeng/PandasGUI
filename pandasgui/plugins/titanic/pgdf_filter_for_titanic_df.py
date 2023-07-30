import os
import pandas as pd

class TitanicFilter:

    def FirstClass(umdf: pd.DataFrame):
        return umdf['class'].str.startswith('First')

    def SecondClass(umdf: pd.DataFrame):
        return umdf['class'].str.startswith('Second')

    def ThirdClass(umdf: pd.DataFrame):
        return umdf['class'].str.startswith('Third')

    def Male(umdf: pd.DataFrame):
        return umdf.sex.str.startswith('male')

    def Female(umdf: pd.DataFrame):
        return umdf.sex.str.startswith('female')

    def Children(umdf: pd.DataFrame):
        return umdf.age <= 10.0
