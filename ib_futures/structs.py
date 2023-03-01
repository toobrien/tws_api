from enum import IntEnum


class instrument():

    def __init__(self, id):
    
        self.id         = id
        self.symbol     = id[0]
        self.exchange   = id[1]
        self.type       = id[2]
        self.legs       = id[3:]
        self.contract   = None


month_codes = {
    1:  "F",
    2:  "G",
    3:  "H",
    4:  "J",
    5:  "K",
    6:  "M",
    7:  "N",
    8:  "Q",
    9:  "U",
    10: "V",
    11: "X",
    12: "Z"
}
