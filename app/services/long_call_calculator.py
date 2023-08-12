import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\Desktop\\options-flask\\options-' \
                                               'flask\\app\\services\\polished-parser-390314-7be98befde9a.json'

# AAPL230804C00200000
# AAPL230804P00190000
# AAPL230804C00205000
# AAPL230804P00185000


def calculate_long_call_profit_and_loss(start_date, long_call_contract):

    # Get data from big query:
    client = bigquery.Client()

    long_call = get_value_from_big_query(client, long_call_contract)
    current_call_price = get_current_value_from_big_query(client, long_call_contract)

    stock_data = stock_info.get_live_price("AAPL")
    # stock_data = 209

    premium_received = calculate_premium_received(long_call["per_value_share"])

    maximum_profit = "Unlimited"

    current_profit_loss = calculate_profit_loss(stock_data, premium_received, long_call, current_call_price)

    break_even_point_call = calculate_break_even_point(premium_received, long_call)

    print("Ticker: ", "AAPL")
    print("Stock live price: ", round(stock_data, 2))
    print("Expiration date: ", "August 4, 2023")
    print("Long call: ", long_call)
    print("Current long call prices: ", current_call_price)
    print("Premium given: ", premium_received)
    print("Maximum profit: ", maximum_profit)
    print("Maximum loss: ", premium_received)
    print("Current profit/loss: ", round(current_profit_loss, 2))
    print("Break even point for call: ", break_even_point_call)

    result = {
        "Ticker": "AAPL",
        "Stock live price": round(stock_data, 2),
        "Expiration date": "August 4, 2023",
        "Long call": long_call,
        "Current long call prices: ": current_call_price,
        "Premium given": premium_received,
        "Maximum profit": maximum_profit,
        "Maximum loss ": premium_received,
        "Current profit/loss: ": round(current_profit_loss, 2),
        "Break even point": break_even_point_call
    }

    return result


def get_value_from_big_query(client, contract_name):
    table_id = "polished-parser-390314.options_data.options_data_real_time"
    query = """
        SELECT * 
        FROM `polished-parser-390314.options_data.options_data_real_time` 
        WHERE contract_name='{}' and timestamp='2023-07-19 19:12:44 UTC';
        """.format(contract_name)
    query_job = client.query(query)  # Make an API request.
    contract_dict = {}
    for row in query_job:
        # Row values can be accessed by field name or index.
        print("row: ", row)
        contract_dict["strike"] = row["strike"]
        contract_dict["per_value_share"] = row["last_price"]
    return contract_dict


def get_current_value_from_big_query(client, contract_name):
    table_id = "polished-parser-390314.options_data.options_data_real_time"
    query = """
            SELECT * 
            FROM `polished-parser-390314.options_data.options_data_real_time` 
            WHERE contract_name='{}' ORDER BY timestamp DESC LIMIT 1;
            """.format(contract_name)
    query_job = client.query(query)  # Make an API request.
    contract_dict = {}
    for row in query_job:
        # Row values can be accessed by field name or index.
        print("row: ", row)
        contract_dict["strike"] = row["strike"]
        contract_dict["per_value_share"] = row["last_price"]
    return contract_dict


def calculate_premium_received(long_call):
    premium = long_call
    return premium*100


def calculate_profit_loss(stock_price, premium, long_call, current_call_price):
    profit = None
    if stock_price >= long_call["strike"]:
        profit = ((stock_price - long_call["strike"]) * 100) - premium
    else:
        profit = (long_call["per_value_share"] - current_call_price["per_value_share"]) * 100
    return profit


def calculate_break_even_point(premium, long_call):
    return (premium/100) + long_call["strike"]
