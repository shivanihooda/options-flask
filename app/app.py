from flask import Flask
from views import GetStrategyDetails

app = Flask(__name__)

app.add_url_rule(
    "/api/<version>/options/strategy",
    view_func=GetStrategyDetails.as_view('strategy'),
    methods=["GET"]
)
