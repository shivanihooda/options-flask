import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\PycharmProjects\\project_dissertation' \
                                               '\\polished-parser-390314-7be98befde9a.json'


def calculate_long_put_profit_and_loss(start_date, long_put_contract):

    # Get data from big query:
    client = bigquery.Client()

    long_put = get_value_from_big_query(client, long_put_contract, start_date)
    current_call_price = get_current_value_from_big_query(client, long_put_contract)

    stock_data = stock_info.get_live_price(long_put["ticker_symbol"])

    premium_received = calculate_premium_received(long_put["per_value_share"])

    maximum_profit = "Unlimited"

    current_profit_loss = calculate_profit_loss(stock_data, premium_received, long_put, current_call_price)

    break_even_point_call = calculate_break_even_point(premium_received, long_put)

    result = {
        "ticker": long_put["ticker_symbol"],
        "stock_live_price": round(stock_data, 2),
        "expiration_date": long_put["expiration_date"].strftime("%b %d, %Y"),
        "premium": round(premium_received,2),
        "maximum_profit": maximum_profit,
        "maximum_loss": round(premium_received,2),
        "current_profit_loss": round(current_profit_loss, 2),
        "break_even_point": break_even_point_call,
        "strike_price": long_put["strike"],
        "option_per_stock_value": long_put["per_value_share"],
        "option_current_strike": current_call_price["strike"],
        "option_current_per_stock_value": current_call_price["per_value_share"]
    }

    return result


def get_value_from_big_query(client, contract_name, start_date):
    query = """
        SELECT *
        FROM `polished-parser-390314.options_data.options_data_real_time`
        WHERE contract_name='{}' and FORMAT_TIMESTAMP('%Y%m%d', timestamp) = '{}'
        order by timestamp desc LIMIT 1;
        """.format(contract_name, start_date)
    query_job = client.query(query)  # Make an API request.
    contract_dict = {}
    for row in query_job:
        # Row values can be accessed by field name or index.
        contract_dict["ticker_symbol"] = row["ticker_symbol"]
        contract_dict["strike"] = row["strike"]
        contract_dict["expiration_date"] = row["expiration_date"]
        contract_dict["per_value_share"] = row["last_price"]
    return contract_dict


def get_current_value_from_big_query(client, contract_name):
    query = """
        SELECT * 
        FROM `polished-parser-390314.options_data.options_data_real_time` 
        WHERE contract_name='{}' ORDER BY timestamp DESC LIMIT 1;
        """.format(contract_name)
    query_job = client.query(query)  # Make an API request.
    contract_dict = {}
    for row in query_job:
        # Row values can be accessed by field name or index.
        contract_dict["strike"] = row["strike"]
        contract_dict["per_value_share"] = row["last_price"]
    return contract_dict


def calculate_premium_received(long_put):
    premium = long_put
    return premium*100


def calculate_profit_loss(stock_price, premium, long_put, current_call_price):
    if stock_price <= long_put["strike"]:
        profit = ((long_put["strike"] - stock_price) * 100) - premium
    else:
        profit = (long_put["per_value_share"] - current_call_price["per_value_share"]) * 100
    return profit


def calculate_break_even_point(premium, long_put):
    return long_put["strike"] - (premium / 100)
