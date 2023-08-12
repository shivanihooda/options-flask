import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\PycharmProjects\\project_dissertation\\polished-parser' \
                                             '-390314-7be98befde9a.json'


def calculate_protective_put_profit_and_loss(start_date, short_put_contract):

    # Get data from big query:
    client = bigquery.Client()

    protective_put = get_value_from_big_query(client, short_put_contract)

    stock_data = stock_info.get_live_price("AAPL")
    stock_data = 197

    stock_value = stock_info.get_data("AAPL", start_date = "19/07/2023", end_date = "20/07/2023")
    print(stock_value["close"])

    premium_received = calculate_premium_received(protective_put["per_value_share"])

    maximum_loss = protective_put["strike"] - stock_value["close"] - premium_received

    current_profit_loss = calculate_profit_loss(stock_data, stock_value["close"], premium_received, protective_put)

    break_even_point_call = calculate_break_even_point(premium_received, stock_value["close"])

    result = {
        "Ticker": "AAPL",
        "Stock live price": round(stock_data, 2),
        "Expiration date": "August 4, 2023",
        "Short put": protective_put,
        "Premium given": premium_received,
        "Maximum profit": "Unlimited",
        "Maximum loss ": maximum_loss,
        "Current profit/loss: ": round(current_profit_loss, 2),
        "Break even point": break_even_point_call
    }

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


def calculate_premium_received(short_put):
    premium = short_put
    return premium*100


def calculate_profit_loss(stock_price, initial_stock_price, premium, short_put):
    profit = (stock_price - initial_stock_price)*100 + max(short_put["strike"] - stock_price, 0) - premium
    return profit


def calculate_break_even_point(premium, initial_price):
    return initial_price + (premium / 100)


calculate_protective_put_profit_and_loss("19/07/2023", "AAPL230804C00200000")

