# PDGA ratings estimator

Grabs the ratings detail page from given players PDGA number. Asks for tournament ratings inputs for values not included in current
PDGA rating. Then calculates the estimated new ratings.

## TODO

- Automatically grab tournament rating values from player statistics tab under tournament results
  - Complete, needs to be improved to get tournament data such as date, time, rounds, etc. All it grabs right now is ratings for player
- Drop tournament ratings that are 12 months or older from last rated round (current uses - next ratings update date)
- Add forecasting
  - Example: given next (x amount) of tournaments what would I need to average to reach 930 rating?
