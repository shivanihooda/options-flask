import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\PycharmProjects\\project_dissertation' \
                                               '\\polished-parser-390314-7be98befde9a.json'


def calculate_short_straddle_profit_and_loss(start_date, short_put_contract, short_call_contract):

    # Get data from big query:
    client = bigquery.Client()

    short_put = get_value_from_big_query(client, short_put_contract, start_date)
    short_call = get_value_from_big_query(client, short_call_contract, start_date)

    stock_data = stock_info.get_live_price(short_put["ticker_symbol"])

    premium_received = calculate_premium_received(short_put["per_value_share"], short_call["per_value_share"])

    maximum_profit = premium_received

    current_profit_loss = calculate_profit_loss(stock_data, premium_received, short_put, short_call)

    lower_break_even_point, upper_break_even_price = calculate_break_even_points(premium_received, short_put, short_call)

    result = {
        "ticker": short_put["ticker_symbol"],
        "stock_live_price": round(stock_data, 2),
        "expiration_date": short_put["expiration_date"].strftime("%b %d, %Y"),
        "premium": premium_received,
        "maximum_profit": maximum_profit,
        "maximum_loss": "Unlimited",
        "current_profit_loss": round(current_profit_loss, 2),
        "upper_break_even_point": upper_break_even_price,
        "lower_break_even_point": lower_break_even_point,
        "short_call_strike_price": short_call["strike"],
        "short_call_option_per_stock_value": short_call["per_value_share"],
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


# calculate_short_straddle_profit_and_loss("19/07/2023", "AAPL230804C00205000", "AAPL230804C00205000")
