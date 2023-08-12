import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\PycharmProjects\\project_dissertation\\polished-parser' \
                                             '-390314-7be98befde9a.json'


def calculate_short_put_profit_and_loss(start_date, short_put_contract):

    # Get data from big query:
    client = bigquery.Client()

    short_put = get_value_from_big_query(client, short_put_contract)

    stock_data = stock_info.get_live_price("AAPL")
    stock_data = 202

    premium_received = calculate_premium_received(short_put["per_value_share"])

    maximum_profit = premium_received

    current_profit_loss = calculate_profit_loss(stock_data, premium_received, short_put)

    break_even_point_call = calculate_break_even_point(premium_received, short_put)

    result = {
        "Ticker": "AAPL",
        "Stock live price": round(stock_data, 2),
        "Expiration date": "August 4, 2023",
        "Short put": short_put,
        "Premium given": premium_received,
        "Maximum profit": maximum_profit,
        "Maximum loss ": "Unlimited",
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


def calculate_premium_received(short_put):
    premium = short_put
    return premium*100


def calculate_profit_loss(stock_price, premium, short_put):
    profit = premium - (max(0, short_put["strike"] - stock_price)) * 100
    return profit


def calculate_break_even_point(premium, short_put):
    return short_put["strike"] - (premium / 100)

