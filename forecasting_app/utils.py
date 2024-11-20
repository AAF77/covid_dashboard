import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import os

def generate_forecasts(data, target_variables, steps=3650):
    """
    Generates ARIMA forecasts for multiple target variables.

    Args:
        data (pd.DataFrame): Time-series data with a datetime index.
        target_variables (list): List of variables to forecast (e.g., 'deaths', 'active', 'recovered').
        steps (int): Number of steps to forecast (default: 10 years, assuming daily data).

    Returns:
        dict: Dictionary of forecast DataFrames for each target variable.
    """
    forecasts = {}
    forecast_dates = pd.date_range(start=data.index[-1], periods=steps + 1, freq='D')[1:]  # Generate future dates

    for variable in target_variables:
        model = ARIMA(data[variable], order=(5, 1, 0))  # ARIMA (p, d, q)
        model_fit = model.fit()

        # Forecast for the given number of steps
        forecast = model_fit.forecast(steps=steps)
        forecast_df = pd.DataFrame({
            'date': forecast_dates,  # Include the date column
            f'{variable}_forecast': forecast.round().astype(int)  # Round and convert to integer
        })

        forecasts[variable] = forecast_df

    return forecasts



def save_forecasts_to_csv(forecasts, filename_prefix):
    """
    Saves multiple forecast results to a single CSV file.

    Args:
        forecasts (dict): Dictionary of forecast DataFrames.
        filename_prefix (str): Prefix for the CSV file name.

    Returns:
        str: Path to the saved CSV file.
    """
    combined_df = pd.concat(forecasts.values(), axis=1)
    combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]  # Remove duplicate date columns
    combined_df['date'] = forecasts[list(forecasts.keys())[0]]['date']  # Ensure a single date column
    file_path = os.path.join('forecasting_app/forecasts', f'{filename_prefix}_forecast.csv')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    combined_df.to_csv(file_path, index=False)
    return file_path
