import os
import yahoo_fin.stock_info as stock_info
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'C:\\Users\\MNC\\PycharmProjects\\project_dissertation' \
                                               '\\polished-parser-390314-7be98befde9a.json'


def calculate_protective_put_profit_and_loss(start_date, short_put_contract):

    # Get data from big query:
    client = bigquery.Client()

    protective_put = get_value_from_big_query(client, short_put_contract, start_date)

    stock_data = stock_info.get_live_price(protective_put["ticker_symbol"])

    stock_value = stock_info.get_data(protective_put["ticker_symbol"],
                                      start_date=f'{start_date[6:8]}/{start_date[4:6]}/{start_date[0:4]}',
                                      end_date=protective_put["expiration_date"].strftime("%d/%m/%Y"))

    premium_received = calculate_premium_received(protective_put["per_value_share"])

    maximum_loss = protective_put["strike"] - stock_value["close"] - premium_received

    current_profit_loss = calculate_profit_loss(stock_data, stock_value["close"], premium_received, protective_put)

    break_even_point_call = calculate_break_even_point(premium_received, stock_value["close"])

    result = {
        "ticker": protective_put["ticker_symbol"],
        "stock_live_price": round(stock_data, 2),
        "expiration_date": protective_put["expiration_date"].strftime("%b %d, %Y"),
        "premium": premium_received,
        "maximum_profit": "Unlimited",
        "maximum_loss": maximum_loss,
        "current_profit_loss": round(current_profit_loss, 2),
        "break_even_point": break_even_point_call,
        "stock_price_at_purchase": stock_value["close"],
        "short_put_strike_price": protective_put["strike"],
        "short_put_option_per_stock_value": protective_put["per_value_share"]
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


def calculate_premium_received(short_put):
    premium = short_put
    return premium*100


def calculate_profit_loss(stock_price, initial_stock_price, premium, short_put):
    profit = (stock_price - initial_stock_price)*100 + max(short_put["strike"] - stock_price, 0) - premium
    return profit


def calculate_break_even_point(premium, initial_price):
    return initial_price + (premium / 100)


# calculate_protective_put_profit_and_loss("19/07/2023", "AAPL230804C00200000")

