INSTRUMENTS = [
    ( "CL", "NYMEX", "single", "J23"),
    ( "HO", "NYMEX", "single", "J23" ),
    ( "RB", "NYMEX", "single", "J23" ),
    ( "RB.HO", "NYMEX", "inter", "+1:J23", "-1:J23"),
    ( "HO", "NYMEX", "rcal", "M23", "Z23" ),
    ( "HO", "NYMEX", "rcal", "M23", "U23" ),
    ( "HO", "NYMEX", "rcal", "U23", "Z23" ),
    ( "HO", "NYMEX", "fly",  "M23", "U23", "Z23" ),
    ( "NG", "NYMEX", "single", "J23" ),
    ( "NG", "NYMEX", "fly",  "V23", "X23", "Z23" ),
    ( "NG", "NYMEX", "rcal",  "M23", "Z23" ),
    ( "NG", "NYMEX", "rcal",  "X23", "H24" ),
    ( "ZT", "CBOT", "rcal", "M23", "U23" ),
    ( "ZB", "CBOT", "rcal", "M23", "U23" ),
    ( "ZN", "CBOT", "rcal", "M23", "U23" ),
    ( "ZS", "CBOT", "custom", "-1:N23", "+1:Q23", "+1:U23", "-1:X23" )
]
