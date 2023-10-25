from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .trading_functions_alpaca import close_all_trades, place_order_for_strategy
from alpaca.trading.client import TradingClient
from decouple import config

MULTIPLIER_HOLD_OVER_NIGHT = 1/3
MULTIPLIER_CLOSE_OVER_NIGHT = 1.3

api_key_deadzone_strategy = config('api_key_deadzone_strategy')
secret_key_deadzone_strategy = config('secret_key_deadzone_strategy')

api_key_deadzone_strategy_close_over_night = config(
    'api_key_deadzone_strategy_close_over_night')
secret_key_deadzone_strategy_close_over_night = config(
    'secret_key_deadzone_strategy_close_over_night')

api_key_vumanuchi_strategy = config('api_key_vumanuchi_strategy')
secret_key_vumanuchi_strategy = config('secret_key_vumanuchi_strategy')

api_key_strategy_0038_30min = config('api_key_strategy_0038_30min')
secret_key_strategy_0038_30min = config('secret_key_strategy_0038_30min')


class Strategy:
    # Constructor method (called when creating an instance)
    def __init__(self, API_KEY, SECRET_KEY, strategy_name):
        self.API_KEY = API_KEY  # Instance attribute
        self.SECRET_KEY = SECRET_KEY  # Instance attribute
        self.strategy_name = strategy_name  # Instance attribute


deadzone_strategy = Strategy(API_KEY=api_key_deadzone_strategy,
                             SECRET_KEY=secret_key_deadzone_strategy,
                             strategy_name="deadzone")

deadzone_strategy_close_over_night = Strategy(
    API_KEY=api_key_deadzone_strategy_close_over_night,
    SECRET_KEY=secret_key_deadzone_strategy_close_over_night,
    strategy_name="deadzone_close_over_night")

vumanuchi_strategy = Strategy(API_KEY=api_key_vumanuchi_strategy,
                              SECRET_KEY=secret_key_vumanuchi_strategy,
                              strategy_name="vumanuchi")

strategy_0038_30min = Strategy(API_KEY=api_key_strategy_0038_30min,
                               SECRET_KEY=secret_key_strategy_0038_30min,
                               strategy_name="strategy_0038_30min")

all_strategies = [deadzone_strategy,
                  deadzone_strategy_close_over_night, vumanuchi_strategy, strategy_0038_30min]


@csrf_exempt
def place_order(request):
    if request.method == 'POST':
        json_payload = json.loads(request.body)
        print('START OF THIS LOG MESSAGE')
        print('Receiving webhook with the following data:')
        trade_side = str(json_payload['side'])
        print(f'The trade side is: {trade_side}')
        cmd = str(json_payload['cmd'])
        print(f'The command is: {cmd}')
        symbol = str(json_payload['symbol'])
        print(f'The symbol is: {symbol}')

        try:
            str(json_payload['strategy'])
            strategy = str(json_payload['strategy'])
            print(f'The strategy is: {strategy}\n')
        except Exception as e:
            print('The strategy is not defined.\n')
            strategy = 'deadzone'

        if strategy == 'vumanuchi':
            place_order_for_strategy(trade_side=trade_side, symbol=symbol, cmd=cmd, multiplier=MULTIPLIER_HOLD_OVER_NIGHT,
                                     api_key=vumanuchi_strategy.API_KEY, secret_key=vumanuchi_strategy.SECRET_KEY,
                                     strategy_name=vumanuchi_strategy.strategy_name, close_over_night=False)
        elif strategy == 'strategy_0038_30min':
            place_order_for_strategy(trade_side=trade_side, symbol=symbol, cmd=cmd, multiplier=MULTIPLIER_HOLD_OVER_NIGHT,
                                     api_key=strategy_0038_30min.API_KEY, secret_key=strategy_0038_30min.SECRET_KEY,
                                     strategy_name=strategy_0038_30min.strategy_name, close_over_night=False)
        elif strategy == 'deadzone':
            # Entering orders for the hold over night strategy.
            place_order_for_strategy(trade_side=trade_side, symbol=symbol, cmd=cmd, multiplier=MULTIPLIER_HOLD_OVER_NIGHT,
                                     api_key=deadzone_strategy.API_KEY, secret_key=deadzone_strategy.SECRET_KEY,
                                     strategy_name=deadzone_strategy.strategy_name, close_over_night=False)
            # Entering orders for the close-over-night strategy.
            place_order_for_strategy(trade_side=trade_side, symbol=symbol, cmd=cmd, multiplier=MULTIPLIER_CLOSE_OVER_NIGHT,
                                     api_key=deadzone_strategy_close_over_night.API_KEY, secret_key=deadzone_strategy_close_over_night.SECRET_KEY,
                                     strategy_name=deadzone_strategy_close_over_night.strategy_name, close_over_night=True)

    print('END OF THIS LOG MESSAGE\n')
    return HttpResponse('Success!')


@csrf_exempt
def close_trades(request):
    if request.method == 'POST':
        try:
            close_all_trades()
        except Exception as e:
            print("Exception occurred in close_all_trades() function.")
            print(e)

    return HttpResponse('Success!')


@csrf_exempt
def get_balances(request):
    if request.method == 'GET':
        equity_list = []
        for strategy in all_strategies:
            trading_client = TradingClient(
                strategy.API_KEY, strategy.SECRET_KEY, paper=True)
            account = trading_client.get_account()
            equity = float(account.portfolio_value)  # type: ignore
            equity_list.append(
                {strategy.strategy_name + " balance": round(equity, 0)})
            equity_list_json = json.dumps(equity_list)
        return HttpResponse(equity_list_json)
