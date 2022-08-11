from webscrape import fetch_month
import pandas as pd
import datetime
from tqdm import tqdm
import numpy as np


start_date = datetime.date(2011,7,1)
end_date = datetime.datetime.now()



date_range = pd.date_range(start_date, end_date)
date_range = date_range[date_range.day == 1]


b = []
for day in tqdm(date_range):
    b += fetch_month(day.month, day.year)
df = pd.DataFrame(b)
df['Duration'] = df['End Time'] - df['Start Time']
df['Minutes'] = df['Duration']/np.timedelta64(1, 'm')
df.to_pickle('./out.pkl')

