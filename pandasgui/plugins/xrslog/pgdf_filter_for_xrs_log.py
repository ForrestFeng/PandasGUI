import os
import pandas as pd


class XrsLogFilter:

    def ErrorLog(umdf: pd.DataFrame):
        return umdf['level'].str.startswith('Error')

    def WarnLog(umdf: pd.DataFrame):
        return umdf['level'].str.startswith('Warn')

    def InfoLog(umdf: pd.DataFrame):
        return umdf['level'].str.startswith('Info')
