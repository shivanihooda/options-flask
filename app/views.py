from decorators import to_json
from exceptions import BadRequest


# third party imports
from flask import request, current_app, make_response
from flask.views import MethodView

# code imports
from services.iron_condor_calculator import calculate_iron_condor_profit_and_loss
from services.long_call_calculator import calculate_long_call_profit_and_loss
from services.short_call_calculator import calculate_short_call_profit_and_loss
from constants import StrategyTypes


class GetStrategyDetails(MethodView):

    @to_json(200)
    def get(self, version):
        try:
            strategy = str(request.args.get("strategy"))
            start_date = request.args.get("start_date")

            if strategy == StrategyTypes.IronCondor:
                short_call = str(request.args.get("short_call"))
                short_put = str(request.args.get("short_put"))
                long_call = str(request.args.get("long_call"))
                long_put = str(request.args.get("long_put"))
                return calculate_iron_condor_profit_and_loss(start_date, short_call, short_put, long_call, long_put)
            elif strategy == StrategyTypes.LongCall:
                long_call = str(request.args.get("long_call"))
                return calculate_long_call_profit_and_loss(start_date, long_call)
            elif strategy == StrategyTypes.ShortCall:
                short_call = str(request.args.get("short_call"))
                return calculate_short_call_profit_and_loss(start_date, short_call)
        except Exception as exc:
            raise BadRequest(f'something went wrong: {exc}', 400)
