from prophet import Prophet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta, datetime

def create_prophet_model(data):
    # 設定模型參數與成分
    model = Prophet(changepoint_prior_scale=0.3)
    model.add_seasonality(name = 'daily', period = 1, fourier_order = 3, prior_scale = 0.2)
    model.add_seasonality(name = 'weekly', period = 5, fourier_order = 3, prior_scale = 0.2)
    model.add_seasonality(name = 'monthly', period = 30.5, fourier_order = 2, prior_scale = 0.1)
    model.add_seasonality(name = 'yearly', period = 365, fourier_order = 2, prior_scale = 0.1)
    # 使用前三年的資料訓練
    training_data = data[data['ds'] > (max(data['ds'])-pd.DateOffset(years=3))]
    model.fit(training_data)
    return model

def remove_weekends(dataframe):       
    # Reset index to use ix
    dataframe = dataframe.reset_index(drop=True)
    
    weekends = []
    
    # Find all of the weekends
    for i, date in enumerate(dataframe['ds']):
        if (date.weekday() == 5 or date.weekday() == 6):
            weekends.append(i)
        
    # Drop the weekends
    dataframe = dataframe.drop(weekends, axis=0)
    
    return dataframe
