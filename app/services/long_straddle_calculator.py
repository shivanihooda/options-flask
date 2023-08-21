import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\PycharmProjects\\project_dissertation' \
                                               '\\polished-parser-390314-7be98befde9a.json'


def calculate_long_straddle_profit_and_loss(start_date, long_put_contract, long_call_contract):

    # Get data from big query:
    client = bigquery.Client()

    long_put = get_value_from_big_query(client, long_put_contract, start_date)
    long_call = get_value_from_big_query(client, long_call_contract, start_date)

    stock_data = stock_info.get_live_price(long_call["ticker_symbol"])

    premium_received = calculate_premium_received(long_put["per_value_share"], long_call["per_value_share"])

    maximum_loss = premium_received

    current_profit_loss = calculate_profit_loss(stock_data, premium_received, long_put, long_call)

    lower_break_even_point, upper_break_even_price = calculate_break_even_points(premium_received, long_put, long_call)

    result = {
        "ticker": long_put["ticker_symbol"],
        "stock_live_price": round(stock_data, 2),
        "expiration_date": long_put["expiration_date"].strftime("%b %d, %Y"),
        "premium": premium_received,
        "maximum_profit": "Unlimited",
        "maximum_loss": maximum_loss,
        "current_profit_loss": round(current_profit_loss, 2),
        "upper_break_even_point": upper_break_even_price,
        "lower_break_even_point": lower_break_even_point,
        "long_call_strike_price": long_call["strike"],
        "long_call_option_per_stock_value": long_call["per_value_share"],
        "long_put_strike_price": long_put["strike"],
        "long_put_option_per_stock_value": long_put["per_value_share"]
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


def calculate_premium_received(long_put, long_call):
    premium = long_put + long_call
    return premium*100


def calculate_profit_loss(stock_price, premium, long_put, long_call):
    profit = None
    if stock_price >= long_call["strike"]:
        profit = (stock_price - long_call["strike"])*100 - premium
    elif stock_price <= long_put["strike"]:
        profit = (long_put["strike"] - stock_price)*100 - premium
    else:
        profit = - premium
    return profit


def calculate_break_even_points(premium, long_put, long_call):
    return long_put["strike"] - premium/100, long_call["strike"] + premium/100


# calculate_long_straddle_profit_and_loss("19/07/2023", "AAPL230804C00205000", "AAPL230804C00205000")
