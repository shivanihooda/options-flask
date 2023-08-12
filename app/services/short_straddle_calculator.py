import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\PycharmProjects\\project_dissertation\\polished-parser' \
                                             '-390314-7be98befde9a.json'

# AAPL230804C00200000
# AAPL230804P00190000
# AAPL230804C00205000
# AAPL230804P00185000


def calculate_short_straddle_profit_and_loss(start_date, short_put_contract, short_call_contract):

    # Get data from big query:
    client = bigquery.Client()

    short_put = get_value_from_big_query(client, short_put_contract)
    short_call = get_value_from_big_query(client, short_call_contract)

    stock_data = stock_info.get_live_price("AAPL")
    stock_data = 205

    premium_received = calculate_premium_received(short_put["per_value_share"], short_call["per_value_share"])

    maximum_profit = premium_received

    current_profit_loss = calculate_profit_loss(stock_data, premium_received, short_put, short_call)

    lower_break_even_point, upper_break_even_price = calculate_break_even_points(premium_received, short_put, short_call)

    result = {
        "Ticker": "AAPL",
        "Stock live price": stock_data,
        "Expiration date": "August 4, 2023",
        "Short call": short_put,
        "Long call": short_call,
        "Premium received": premium_received,
        "Maximum profit": maximum_profit,
        "Maximum Loss": "Unlimited",
        "Current profit": current_profit_loss,
        "Lower Break even point": lower_break_even_point,
        "Upper Break Even Price": upper_break_even_price
    }
    # print("Ticker: ", "AAPL")
    # print("Stock live price: ", stock_data)
    # print("Expiration date: ", "August 4, 2023")
    # print("Short call: ", short_put)
    # print("Short put: ", short_put)
    # print("Long call: ", short_call)
    # print("Long put: ", short_put)
    # print("Premium received: ", premium_received)
    # print("Maximum profit: ", maximum_profit)
    # print("Current profit: ", current_profit_loss)
    # print("Upper Break even point: ", upper_break_even_point)
    # print("Lower Break even point: ", lower_break_even_point)

    print(result)
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


def calculate_premium_received(short_put, short_call):
    premium = short_put + short_call
    return premium*100


def calculate_profit_loss(stock_price, premium, short_put, short_call):
    profit = None
    if stock_price >= short_call["strike"]:
        profit = premium - (stock_price - short_call["strike"]) * 100
    elif stock_price <= short_put["strike"]:
        profit = premium - (short_put["strike"] - stock_price) * 100
    else:
        profit = premium
    return profit


def calculate_break_even_points(premium, short_put, short_call):
    return short_put["strike"] - premium / 100, short_call["strike"] + premium / 100


calculate_short_straddle_profit_and_loss("19/07/2023", "AAPL230804C00205000", "AAPL230804C00205000")
