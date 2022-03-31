class SpiralTreeContext:

    def __init__(self, namestring="", lyr=None, expr=None, vol_flds=None, alpha=25, proj=None):
        self.namestring = namestring
        self.lyr = lyr
        self.expr = expr
        self.vol_flds = vol_flds
        self.alpha = alpha
        self.proj = proj
        self.styling_inactive = True
        self.saving_inactive = True
    
    def updateContext(self, namestring=None, lyr=None, expr=None, vol_flds=None, alpha=None, proj=None):
        self.namestring = namestring if namestring is not None else self.namestring
        self.lyr = lyr if lyr is not None else self.lyr
        self.expr = expr if expr is not None else self.expr
        self.vol_flds = vol_flds if vol_flds is not None else self.vol_flds
        self.alpha = alpha if alpha is not None else self.alpha
        self.proj = proj if proj is not None else self.proj

    def __repr__(self):
        return self.namestring