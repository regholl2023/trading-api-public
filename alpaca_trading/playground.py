from datetime import datetime
import pytz
import requests

# url = 'https://robin-test.herokuapp.com/alpaca-trading/close-trades/'
# requests.post(url)


now = datetime.now(pytz.timezone('US/Eastern'))
current_time_hour = now.hour
print(current_time_hour)
