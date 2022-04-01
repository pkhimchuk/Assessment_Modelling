import datetime as dt
import pandas as pd
import numpy as np
import os

class IndexModel:
    #------------------------- init finction -------------------------
    def __init__(self, 
                 prices_file: str = './data_sources/stock_prices.csv', 
                 wgt: list[float] = [0.5,0.25,0.25], 
                 start_value: int = 100) -> None:
            
        self.index_results = None
        self.prices_file = prices_file
        self.wgt = wgt
        self.start_value = start_value       
        
    #------------------------- index level calculations  -------------------------
    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> None:
        
        # weight inputs
        weights_inputs = pd.DataFrame({'Rank'   :range(1,len(self.wgt)+1), 
                                       'Weight' :self.wgt})
        
        # import stock prices + stocks list
        prices_data = pd.read_csv(self.prices_file, sep = ',')
        stocks = prices_data.columns[1:]

        # data check
        if prices_data.isna().sum().sum() != 0: print('NAs in input data')

        # sort prices_data according to date (in case not sorted properly)
        prices_data['Date'] = pd.to_datetime(prices_data['Date'], dayfirst = True)
        prices_data = prices_data.sort_values('Date')
        
        # filter according to inputs
        dates = list(pd.to_datetime(prices_data['Date'].unique(), yearfirst = True))
        good_dates = dates[(dates.index(pd.Timestamp(start_date))-1):dates.index(pd.Timestamp(end_date))+1]
        prices_data[prices_data['Date'].isin(good_dates)]
        
        # copy dataframe
        index_data = prices_data.copy()

        # adding rebalancing dates
        index_data['Is_Rebal_Date'] = (index_data.Date.dt.month !=  index_data.Date.shift(1).dt.month) & (index_data.Date.shift(1).notnull())

        # adding date of the latest rebalancing date
        index_data['Last_Rebal_Date'] = np.NaN

        for i in range(1, len(index_data['Date'])):
            if index_data.loc[i-1, 'Is_Rebal_Date']: 
                index_data.loc[i, 'Last_Rebal_Date'] = index_data.loc[i-1, 'Date']
            else: 
                index_data.loc[i, 'Last_Rebal_Date'] = index_data.loc[i-1, 'Last_Rebal_Date']

        # reshape date to long format
        index_data_long = pd.melt(index_data, \
                                  id_vars = ['Date','Last_Rebal_Date'], \
                                  value_vars = stocks, \
                                  var_name = 'Sec', \
                                  value_name = 'Price') 

        # calculating stock weights
        weights = prices_data.copy()
        weights.columns = weights.columns
        weights.loc[:,weights.columns !=  'Date'] = weights.rank(1, ascending = False, method = 'first')
        weights['Date'] = weights['Date'].shift(-1)
        
        # reshape weights to long format, some formatting
        weights_long = pd.melt(weights, id_vars = 'Date', value_vars = stocks, var_name = 'Sec', value_name = 'Rank')
        weights_long = pd.merge(weights_long, weights_inputs, on = 'Rank')
        weights_long = weights_long.rename(columns = {'Date':'Last_Rebal_Date'})
        weights_long = weights_long.drop('Rank', axis = 1)

        # merging index data to get rebalancing prices, weights
        index_date_rebal =  index_data_long[['Date','Sec','Price']]
        index_date_rebal.columns = ['Last_Rebal_Date','Sec','Rebal_Price']
        index_data_merged = pd.merge(index_data_long, index_date_rebal, how = 'inner', on = ['Last_Rebal_Date','Sec'])
        index_data_merged = pd.merge(index_data_merged, weights_long, on = ['Last_Rebal_Date','Sec'])

        #last data check
        if (index_data_merged.Weight.sum() !=  sum(index_data.Last_Rebal_Date.notna())): print("Weights aren't 100% on all dates")

        # calculation of daily MTD returns
        index_data_merged['MTD_Return_Weighted'] = index_data_merged['Weight'] * (index_data_merged['Price']/index_data_merged['Rebal_Price']-1)
        index_returns = index_data_merged.groupby('Date')['MTD_Return_Weighted'].sum()
        index_returns = pd.DataFrame({'Daily_Returns':index_returns})

        # creating final table with MTD returns
        index_final = pd.merge(index_returns, index_data[['Date','Is_Rebal_Date']], how = 'left', left_index = True, right_on = 'Date')
        index_final['Index_Level'] = 0

        # adding first value
        index_final.loc[-1] = [0, start_date, True, self.start_value]
        index_final['Date'] = pd.to_datetime(index_final['Date'], yearfirst = True)
        index_final = index_final.sort_values('Date')
        index_final.index = range(0, len(index_final.index))

        # calculation of index levels
        for i in range(1,len(index_final['Date'])):

            start_val = index_final.loc[i-1,'Index_Level']
            mtd_return = (index_final.loc[i,'Daily_Returns'])
            mtd_return_prev = (index_final.loc[i-1,'Daily_Returns'])
            rebal_adj = not((index_final.loc[i-1,'Is_Rebal_Date']))

            index_final.loc[i,'Index_Level'] = start_val*(1+mtd_return)/(1+mtd_return_prev*rebal_adj)

        # fune tuning
        index_final = index_final[['Date','Index_Level']]
        
        self.index_results = index_final        
    
    #------------------------- data export  -------------------------    
    def export_values(self, file_name: str) -> None:
        
        self.index_results.to_csv(file_name, sep = ',', index = False)
    
        