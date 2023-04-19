import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Gather the Data

data_url = "http://lib.stat.cmu.edu/datasets/boston"
raw_df = pd.read_csv(data_url, sep="\s+", skiprows=22, header=None)
data = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
target = raw_df.values[1::2, 2] 
data = pd.DataFrame(data, columns=['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO','B','LSTAT'])

boston_target = target
log_prices = np.log(target)
features = data.drop(['INDUS', 'AGE'], axis = 1)
target = pd.DataFrame(log_prices, columns=['PRICE'])

CRIM_IDX = 0
ZN_IDX = 1
CHAS_IDX = 2
RM_IDX = 4
PTRATIO_IDX = 8

zillow_median_price = 583.3
scale_factor = zillow_median_price / np.median(boston_target)

property_stats = features.mean().values.reshape(1, 11)

regr = LinearRegression().fit(features, target) 
fitted_vals = regr.predict(features)

# Calculate the MSE and RMSEv using sklearn

MSE = mean_squared_error(target, fitted_vals)
RMSE = np.sqrt(MSE)

def get_log_estimate(nr_rooms,
                    student_per_classroom,
                    next_to_river = False,
                    high_confidence = True):
    # Configure Property
    property_stats[0][RM_IDX] = nr_rooms
    property_stats[0][PTRATIO_IDX] = student_per_classroom
    
    if next_to_river:
        property_stats[0][CHAS_IDX] = 1
    else:
        property_stats[0][CHAS_IDX] = 0
        
    # Make Prediction
    log_estimate = regr.predict(property_stats)[0][0]
    
    # Calculation Range
    if high_confidence:
        upper_bound = log_estimate + 2*RMSE
        lowe_bound = log_estimate - 2*RMSE
        interval = 95
    else:
        upper_bound = log_estimate + RMSE
        lowe_bound = log_estimate - RMSE
        interval = 68
    return log_estimate, upper_bound, lowe_bound, interval


def get_dollar_estimate(rm, ptratio, chas = False, large_range = True):
    
    """ Estimate the property value in Boston.
    
    Keywords arguemnts :
    
    rm -- number of rooms
    ptratio -- students per classroom in school in the area
    chas -- True if the property next to the river, False otherwise
    large_range -- True for 95% prediction interval, False for 68% prediction interval
    
    
    
    """
    
    # Setting Condition
    if rm < 1 or ptratio < 1:
        print('This is unrealistic. Try again.')
        return
    
    log_est, upper, lower, conf = get_log_estimate(rm,
                                                   student_per_classroom = ptratio,
                                                   next_to_river = chas,
                                                   high_confidence = large_range)

    # Convert to today's price
    dollar_estimate = np.e**log_est * 1000 * scale_factor
    dollar_hi = np.e**upper * 1000 * scale_factor
    dollar_low = np.e**lower * 1000 * scale_factor

    # Round estimate 
    rounded_est = round(dollar_estimate, -3)
    rounded_hi = round(dollar_hi, -3)
    rounded_low = round(dollar_low, -3)

    print(f'The estimated property value is {rounded_est}')
    print(f'At {conf}% confidence the valuation range is')
    print(f'USD {rounded_low} at the lower end to USD {rounded_hi} at high end.')

















