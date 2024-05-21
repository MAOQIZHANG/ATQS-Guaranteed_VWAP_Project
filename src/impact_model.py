import numpy as np
import pandas as pd
import json

class ImpactModel:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = pd.DataFrame()
        self.eta = 0.142
        self.beta = 0.5

    @staticmethod
    def read_pkl(path):
        with open(path, 'rb') as f:
            df = pd.read_pickle(f)
        return df

    @staticmethod
    def melt_df(df, var_name):
        melted_df = pd.melt(df.reset_index(), id_vars='index', value_vars=df.columns, var_name='Day',
                            value_name=var_name).rename(columns={'index': 'Stock'})
        return melted_df[var_name]

    def read_data(self):
        json_file_path = f"{self.filepath}/high_vol_days.json"

        with open(json_file_path, 'r') as file:
            high_vol_days = json.load(file)

        stocks = list(high_vol_days.keys())  # Or however you have your stocks defined
        days = range(65)  # Adjust based on your actual days

        # high_vol_df = pd.DataFrame(True, index=stocks, columns=days)
        # for stock, high_vol_days_list in high_vol_days.items():
        #     for day_idx in high_vol_days_list:
        #         if day_idx in high_vol_df.columns:
        #             high_vol_df.at[stock, day_idx] = False

        value_imbalance = self.read_pkl(f"{self.filepath}/value_imbalance.pkl")
        volatility = self.read_pkl(f"{self.filepath}/Volatility.pkl")
        # volatility = volatility[high_vol_df]
        daily_value = self.read_pkl(f"{self.filepath}/daily_values.pkl")

        value_imbalance = value_imbalance.apply(pd.to_numeric, errors='ignore')
        volatility = volatility.apply(pd.to_numeric, errors='ignore')
        daily_value = daily_value.apply(pd.to_numeric, errors='ignore')
        value_imbalance = value_imbalance.interpolate(axis=1)
        volatility = volatility.interpolate(axis=1)
        daily_value = daily_value.interpolate(axis=1)

        self.df_h = volatility * self.eta * np.abs(1 / daily_value / (0.5/6.5)).pow(self.beta)
    
    def cal_temp_impact(self, stock, date, value_imbalance):

        h = self.df_h.loc[stock, self.df_h.columns[date]] * np.sign(value_imbalance) * np.abs(value_imbalance) ** (self.beta)
        
        return h



# Usage
# Create an instance of the model and call methods
impact_model = ImpactModel('Impact-Model-Matrix')
impact_model.read_data()
print(impact_model.cal_temp_impact('JAVA', 0, 10))
