import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\PycharmProjects\\project_dissertation' \
                                               '\\polished-parser-390314-7be98befde9a.json'

# AAPL230804C00200000
# AAPL230804P00190000
# AAPL230804C00205000
# AAPL230804P00185000


def calculate_iron_condor_profit_and_loss(start_date, short_call_contract, short_put_contract,
                                          long_call_contract, long_put_contract_name):

    # Get data from big query:
    client = bigquery.Client()

    short_call = get_value_from_big_query(client, short_call_contract, start_date)
    short_put = get_value_from_big_query(client, short_put_contract, start_date)
    long_call = get_value_from_big_query(client, long_call_contract, start_date)
    long_put = get_value_from_big_query(client, long_put_contract_name, start_date)

    stock_data = stock_info.get_live_price(short_call["ticker_symbol"])

    premium_received = calculate_premium_received(short_call["per_value_share"], short_put["per_value_share"],
                                                  long_call["per_value_share"], long_put["per_value_share"])

    maximum_profit = premium_received

    maximum_loss = ((long_call["strike"]-short_call["strike"]) + (long_put["strike"]-short_put["strike"]))*100\
                   - premium_received

    current_profit_loss = calculate_profit_loss(stock_data, premium_received, short_call, short_put,
                                                long_call, long_put)

    upper_break_even_point, lower_break_even_point = calculate_break_even_points(premium_received, short_call, short_put)

    result = {
        "ticker": long_call["ticker_symbol"],
        "stock_live_price": round(stock_data, 2),
        "expiration_date": long_call["expiration_date"].strftime("%b %d, %Y"),
        "premium": premium_received,
        "maximum_profit": maximum_profit,
        "maximum_loss": maximum_loss,
        "current_profit_loss": round(current_profit_loss, 2),
        "upper_break_even_point": upper_break_even_point,
        "lower_break_even_point": lower_break_even_point,
        "long_call_strike_price": long_call["strike"],
        "long_call_option_per_stock_value": long_call["per_value_share"],
        "short_call_strike_price": short_call["strike"],
        "short_call_option_per_stock_value": short_call["per_value_share"],
        "long_put_strike_price": long_put["strike"],
        "long_put_option_per_stock_value": long_put["per_value_share"],
        "short_put_strike_price": short_put["strike"],
        "short_put_option_per_stock_value": short_put["per_value_share"]
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

