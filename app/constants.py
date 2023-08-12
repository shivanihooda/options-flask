
class StrategyTypes:
    IronCondor = "IronCondor"
    LongCall = "LongCall"
    ShortCall = "ShortCall"


date_query = "SELECT * FROM `polished-parser-390314.options_data.options_data_real_time` where contract_name='AAPL230804C00200000' and FORMAT_TIMESTAMP('%Y%m%d', timestamp) = '20230801' order by timestamp desc LIMIT 1000"