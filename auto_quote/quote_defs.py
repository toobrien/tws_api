

QUOTE_DEFS = [
    {
        "instrument_id":    ( "RB", "NYMEX", "single", "K23" ),
        "max_fills":        2,
        "qty":              1,
        "update_interval":  5,
        "duration":         10,
        "action":           "BUY",
        "time_in_force":    "DAY",
        "entry":            -0.0240,
        "enabled":          True,
        "max_worsening":    0.0020,
        "profit_taker_amt": 0.0030,
        "stop_loss_amt":    -0.080,
        "inactive_hours":   [ ( "05:30:00", "13:00:00" ) ]
    },
    {
        "instrument_id":    ( "RB", "NYMEX", "single", "K23" ),
        "max_fills":        2,
        "qty":              1,
        "update_interval":  5,
        "duration":         10,
        "action":           "SELL",
        "time_in_force":    "DAY",
        "entry":            0.0050,
        "enabled":          False,
        "max_worsening":    -0.0025,
        "profit_taker_amt": -0.0040,
        "stop_loss_amt":    0.0080,
        "inactive_hours":   [ ( "05:30:00", "13:00:00" ) ]
    },
]
