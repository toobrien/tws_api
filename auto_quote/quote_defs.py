

QUOTE_DEFS = [
    {
        "instrument_id":    ( "RB", "NYMEX", "single", "K23" ),
        "max_fills":        1,
        "qty":              1,
        "duration":         5,
        "action":           "BUY",
        "time_in_force":    "GTD",
        "entry":            -0.0050,
        "enabled":          True,
        "max_worsening":    0.0025,
        "profit_taker_amt": 0.0040,
        "stop_loss_amt":    -0.080,
        "time_zone":        "US/Eastern"
    },
    {
        "instrument_id":    ( "RB", "NYMEX", "single", "K23" ),
        "max_fills":        1,
        "qty":              1,
        "duration":         5,
        "action":           "SELL",
        "time_in_force":    "GTD",
        "entry":            0.0050,
        "enabled":          False,
        "max_worsening":    -0.0025,
        "profit_taker_amt": -0.0040,
        "stop_loss_amt":    0.0080,
        "time_zone":        "US/Eastern"
    },
]
