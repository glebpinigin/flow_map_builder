class SpiralTreeContext:

    def __init__(self, lyr=None, expr=None, vol_flds=None, alpha=25, proj=None):
        self.lyr = lyr
        self.expr = expr
        self.vol_flds = vol_flds
        self.alpha = alpha
        self.proj = proj
        self.styling_inactive = True
        self.saving_inactive = True
    
    def updateContext(self, data=None, expr=None, vol_flds=None, alpha=None, proj=None):
        self.data = data if data is not None else self.data
        self.expr = expr if expr is not None else self.expr
        self.vol_flds = vol_flds if vol_flds is not None else self.vol_flds
        self.alpha = alpha if alpha is not None else self.alpha
        self.proj = proj if proj is not None else self.proj
