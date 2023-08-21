from flask import Flask
from views import GetStrategyDetails
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.add_url_rule(
    "/api/<version>/options/strategy",
    view_func=GetStrategyDetails.as_view('strategy'),
    methods=["GET"]
)
