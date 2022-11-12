class VentValve():

    def __init__(self, _closed_setting, _open_setting):
        self.closed_setting = _closed_setting
        self.open_setting = _open_setting

    def set_percent(self, val):
        if (val > 1.0):
            val = 1.0
        
        if (val < 0.0):
            val = 0.0

        rawval = ((self.open_setting - self.closed_setting) * val) + self.closed_setting
        return rawval

    def set_open_closed(self, open_setting, closed_setting):
        self.open_setting = open_setting
        self.closed_setting = closed_setting