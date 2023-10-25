from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import requests
import time
from datetime import datetime
import pytz


def place_order_for_strategy(trade_side, symbol, cmd, multiplier, api_key, secret_key, strategy_name, close_over_night=False):
    print(f"Start of Try/Except block | Strategy: {strategy_name}")
    if not close_over_night:
        try:
            create_order(trade_side, symbol, cmd,
                         multiplier, api_key, secret_key)
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(
            f"Placing orders for the {strategy_name} close-over-night strategy.")
        time.sleep(1.5)
        now = datetime.now(pytz.timezone('US/Eastern'))
        current_time_hour = now.hour

        if cmd == 'open':
            if current_time_hour < 13:
                try:
                    create_order(trade_side, symbol, cmd,
                                 multiplier, api_key, secret_key)
                except Exception as e:
                    print(e)
        if cmd == 'close':
            try:
                create_order(trade_side, symbol, cmd,
                             multiplier, api_key, secret_key)
            except Exception as e:
                print(e)

    print(f"End of try/except block | Strategy: {strategy_name}\n")


def create_order(trade_side, symbol, cmd, multiplier, api_key, secret_key):
    trading_client = TradingClient(api_key, secret_key, paper=True)
    account = trading_client.get_account()

    equity = get_equity(account)
    latest_bar = get_latest_bar(symbol)

    # print(f"Latest bar: {latest_bar}")

    if cmd == 'open':
        amount = int(float(equity) / float(latest_bar) * multiplier)
        print(f"Amount to trade: {amount}")
        print(
            f"Creating spot order for {symbol}, {trade_side}, {cmd}.")
        res = market_order(trading_client, trade_side, symbol, amount)
    elif cmd == 'close':
        res = close_trade(trading_client, symbol)
    return res


def get_equity(account):
    equity = float(account.portfolio_value)  # type: ignore
    print(f"{round(equity, 0)}")
    return equity


def get_latest_bar(symbol):
    res = requests.get(
        f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey=6QHJ1AURZN6QDAUY")
    json_data = res.json()
    last_refreshed = json_data['Meta Data']['3. Last Refreshed']
    last_close = res.json()['Time Series (1min)'][last_refreshed]["4. close"]
    return last_close


def close_all_trades():
    API_KEY_CLOSE_OVER_NIGHT = "PKV7FLPEIBQ7UVAY8WBX"
    SECRET_KEY_CLOSE_OVER_NIGHT = "uaSVz6Vdz96FB5FFEAubKhIrIkVZy3tBFGsfrsIg"
    trading_client = TradingClient(
        API_KEY_CLOSE_OVER_NIGHT, SECRET_KEY_CLOSE_OVER_NIGHT, paper=True)
    print("CLOSING ALL TRADES MESSAGE START.")
    res = trading_client.close_all_positions(cancel_orders=True)
    print(res)
    print("CLOSING ALL TRADES MESSAGE END.")


def close_trade(trading_client, symbol):
    print(f"CLOSING TRADE FOR {symbol} MESSAGE START.")
    res = trading_client.close_position(symbol)
    print(res)
    print(f"CLOSING TRADE FOR {symbol} MESSAGE END.")


def market_order(trading_client, side, symbol, quantity):
    if side == 'buy':
        side = OrderSide.BUY
    elif side == 'sell':
        side = OrderSide.SELL

    # preparing market order
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=quantity,
        side=side,
        time_in_force=TimeInForce.DAY
    )

    # Market order
    market_order = trading_client.submit_order(
        order_data=market_order_data
    )
    print(f"Market order for {symbol} is: {market_order}.\n")
