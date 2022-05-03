"""
PDGA ratings estimator

Asks for tournament ratings inputs for values not included in current
PDGA rating. Then calculates the estimated new ratings

TODO:
    Include function to remove ratings that fall below the standard deviation
"""

from requests_html import HTMLSession

import pandas as pd
import numpy as np
from typing import List


pdga_number = 51790
details_url = f'https://www.pdga.com/player/{pdga_number}/details'

s = HTMLSession()
r = s.get(details_url)

table = r.html.find('table', first=True)

table_df = pd.read_html(table.html)
df = table_df[0]

df_eval = df.copy()
df_eval['Evaluated'] = df_eval['Evaluated'].map({'Yes': True, 'No': False})

df_include = df_eval.copy()
df_include['Included'] = df_include['Included'].map({'Yes': True, 'No': False})

df_dates = df_include.copy()
df_dates['Date'] = df_dates['Date'].str.split('to').str[-1].str.strip()
df_dates['Date'] = pd.to_datetime(df_dates['Date'], format='%d-%b-%Y')

df_results = df_dates.copy()
df_results = df_results.loc[df_results['Included'] == True]


# Standard deviation plus 2.5 pdga threashold
def std_calc(ratings: List):
    return np.std(ratings) * 2.5


def dbl_weight_calc(ratings: List):
    return int(np.floor(len(ratings) * 0.25))


def double_scores(ratings: List):
    dbl_w = int(dbl_weight_calc(ratings))
    return sum(ratings[:dbl_w])


def total_score(ratings: List):
    # Need to account for new ratings below standard deviation
    double_total = double_scores(ratings)
    ratings_total = sum(ratings) + double_total
    num_tournaments = len(ratings) + dbl_weight_calc(ratings)
    total = ratings_total / num_tournaments
    return int(np.ceil(total))

current_rating = total_score(df_results['Rating'])
print(f'Current Rating: {current_rating}')

# Manually input new ratings to calculate
# Modify to pull from tournaments not submitted to pdga
new_ratings = []

while True:
    rating_input = input('Add tournament rating: ')
    if rating_input:
        new_ratings.append(int(rating_input))
    else:
        break

ratings_list = list(df_results['Rating'])
combined_ratings = new_ratings + ratings_list

est_rating = total_score(combined_ratings)
print(f'Estimated New Rating: {est_rating}')
