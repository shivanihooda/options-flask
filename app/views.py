from decorators import to_json
from exceptions import BadRequest


# third party imports
from flask import request, current_app, make_response
from flask.views import MethodView

# code imports
from services.long_call_calculator import calculate_long_call_profit_and_loss
from services.short_call_calculator import calculate_short_call_profit_and_loss
from services.long_put_calculator import calculate_long_put_profit_and_loss
from services.short_put_calculator import calculate_short_put_profit_and_loss
from services.long_straddle_calculator import calculate_long_straddle_profit_and_loss
from services.short_straddle_calculator import calculate_short_straddle_profit_and_loss
from services.bear_call_calculator import calculate_bear_call_profit_and_loss
from services.bull_call_calculator import calculate_bull_call_profit_and_loss
from services.protective_put_calculator import calculate_protective_put_profit_and_loss
from services.iron_condor_calculator import calculate_iron_condor_profit_and_loss

from constants import StrategyTypes


class GetStrategyDetails(MethodView):

    @to_json(200)
    def get(self, version):
        try:
            strategy = str(request.args.get("strategy"))
            start_date = request.args.get("start_date")

            if strategy == StrategyTypes.LongCall:
                long_call = str(request.args.get("long_call"))
                return calculate_long_call_profit_and_loss(start_date, long_call)
            elif strategy == StrategyTypes.ShortCall:
                short_call = str(request.args.get("short_call"))
                return calculate_short_call_profit_and_loss(start_date, short_call)
            elif strategy == StrategyTypes.LongPut:
                long_put = str(request.args.get("long_put"))
                return calculate_long_put_profit_and_loss(start_date, long_put)
            elif strategy == StrategyTypes.ShortPut:
                short_put = str(request.args.get("short_put"))
                return calculate_short_put_profit_and_loss(start_date, short_put)
            elif strategy == StrategyTypes.LongStraddle:
                long_call = str(request.args.get("long_call"))
                long_put = str(request.args.get("long_put"))
                return calculate_long_straddle_profit_and_loss(start_date, long_put, long_call)
            elif strategy == StrategyTypes.ShortStraddle:
                short_call = str(request.args.get("short_call"))
                short_put = str(request.args.get("short_put"))
                return calculate_short_straddle_profit_and_loss(start_date, short_put, short_call)
            elif strategy == StrategyTypes.BearCall:
                long_call = str(request.args.get("long_call"))
                short_call = str(request.args.get("short_call"))
                return calculate_bear_call_profit_and_loss(start_date, short_call, long_call)
            elif strategy == StrategyTypes.BullCall:
                long_call = str(request.args.get("long_call"))
                short_call = str(request.args.get("short_call"))
                return calculate_bull_call_profit_and_loss(start_date, short_call, long_call)
            elif strategy == StrategyTypes.ProtectivePut:
                short_put = str(request.args.get("short_put"))
                return calculate_protective_put_profit_and_loss(start_date, short_put)
            elif strategy == StrategyTypes.IronCondor:
                short_call = str(request.args.get("short_call"))
                short_put = str(request.args.get("short_put"))
                long_call = str(request.args.get("long_call"))
                long_put = str(request.args.get("long_put"))
                return calculate_iron_condor_profit_and_loss(start_date, short_call, short_put, long_call, long_put)
        except Exception as exc:
            raise BadRequest(f'something went wrong: {exc}', 400)
