import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\Desktop\\options-flask\\options-' \
                                               'flask\\app\\services\\polished-parser-390314-7be98befde9a.json'

# AAPL230804C00200000
# AAPL230804P00190000
# AAPL230804C00205000
# AAPL230804P00185000


def calculate_iron_condor_profit_and_loss(start_date, short_call_contract, short_put_contract,
                                          long_call_contract, long_put_contract_name):

    # short_call_contract = input("Enter short call contract name: ")
    # short_put_contract = input("Enter short put contract name: ")
    # long_call_contract = input("Enter long call contract name: ")
    # long_put_contract_name = input("Enter long put contract name: ")

    # Get data from big query:
    client = bigquery.Client()

    short_call = get_value_from_big_query(client, short_call_contract)
    short_put = get_value_from_big_query(client, short_put_contract)
    long_call = get_value_from_big_query(client, long_call_contract)
    long_put = get_value_from_big_query(client, long_put_contract_name)

    stock_data = stock_info.get_live_price("AAPL")
    # stock_data = 209

    premium_received = calculate_premium_received(short_call["per_value_share"], short_put["per_value_share"],
                                                  long_call["per_value_share"], long_put["per_value_share"])

    maximum_profit = premium_received

    current_profit_loss = calculate_profit_loss(stock_data, premium_received, short_call, short_put,
                                                long_call, long_put)

    upper_break_even_point, lower_break_even_point = calculate_break_even_points(premium_received, short_call, short_put)

    result = {
        "Ticker": "AAPL",
        "Stock live price": stock_data,
        "Expiration date": "August 4, 2023",
        "Short call": short_call,
        "Short put": short_put,
        "Long call": long_call,
        "Long put": long_put,
        "Premium received": premium_received,
        "Maximum profit": maximum_profit,
        "Current profit": current_profit_loss,
        "Upper Break even point": upper_break_even_point,
        "Lower Break even point": lower_break_even_point
    }
    # print("Ticker: ", "AAPL")
    # print("Stock live price: ", stock_data)
    # print("Expiration date: ", "August 4, 2023")
    # print("Short call: ", short_call)
    # print("Short put: ", short_put)
    # print("Long call: ", long_call)
    # print("Long put: ", long_put)
    # print("Premium received: ", premium_received)
    # print("Maximum profit: ", maximum_profit)
    # print("Current profit: ", current_profit_loss)
    # print("Upper Break even point: ", upper_break_even_point)
    # print("Lower Break even point: ", lower_break_even_point)

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


def calculate_premium_received(short_call, short_put, long_call, long_put):
    premium = (short_call + short_put) - (long_call + long_put)
    return premium*100


def calculate_profit_loss(stock_price, premium, short_call, short_put, long_call, long_put):
    profit = None
    if short_call["strike"] <= stock_price <= long_call["strike"]:
        profit = premium - (stock_price-short_call["strike"])
    elif stock_price >= long_call["strike"]:
        profit = premium - (long_call["strike"] - short_call["strike"])
    elif short_put["strike"] <= stock_price <= long_put["strike"]:
        profit = premium - (short_put["strike"] - stock_price)
    elif stock_price <= long_put["strike"]:
        profit = premium - (short_put["strike"] - long_put["strike"])
    elif short_put["strike"] <= stock_price <= short_call["strike"]:
        profit = premium
    return profit


def calculate_break_even_points(premium, short_call, short_put):
    return (short_call["strike"] + premium/100), (short_put["strike"] - premium/100)

