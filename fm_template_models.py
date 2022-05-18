from qgis.core import QgsMessageLog

class SpiralTreeContext:

    def __init__(self, namestring="", lyr=None, expr=None, vol_flds=None, alpha=25, proj=None, stop_dst=0):
        self.namestring = namestring
        self.lyr = lyr
        self.expr = expr
        self.vol_flds = vol_flds if vol_flds is not None else []
        self.alpha = alpha
        self.stop_dst = stop_dst
        self.proj = proj
        self.created = False
        self.styled = False
        self.saved = False

        self.display_fld = None
        self.color = None
        self.coef = 0.5
        self.units = None
    
    def updateCreateContext(self, namestring=None, lyr=None, expr=None, vol_flds=None, alpha=None, stop_dst=None, proj=None):
        self.namestring = namestring if namestring is not None else self.namestring
        self.lyr = lyr if lyr is not None else self.lyr
        self.expr = expr if expr is not None else self.expr
        self.vol_flds = vol_flds if vol_flds is not None else self.vol_flds
        self.alpha = alpha if alpha is not None else self.alpha
        self.stop_dst = stop_dst if stop_dst is not None else self.stop_dst
        self.proj = proj if proj is not None else self.proj

    def updateStyleContext(self, display_fld=None, color=None, coef=None, units=None):
        self.display_fld = display_fld if display_fld is not None else self.display_fld
        self.color = color if color is not None else self.color
        self.coef = coef if coef is not None else self.coef
        self.units = units if units is not None else self.units

    def updateSaveContext(self):
        pass
    
    def getCreationKwargs(self):
        return {
            "namestring": self.namestring,
            "lyr": self.lyr,
            "expr": self.expr,
            "vol_flds": self.vol_flds,
            "alpha":self.alpha,
            "stop_dst":self.stop_dst,
            "proj": self.proj
        }
    
    def isCreated(self):
        return self.created
    
    def isStyled(self):
        return self.styled

    def setOutLyr(self, out_lyr):
        self.created = True
        self.out_lyr = out_lyr

    def setSymbol(self, symbol):
        self.styled = True
        self.symbol = symbol

    def log(self):
        QgsMessageLog.logMessage(f'namestring {self.namestring}\nlyr {self.lyr}\nexpr {self.expr}\nvol_flds {self.vol_flds}\nalpha {self.alpha}\nproj {self.proj}')

    def __repr__(self):
        return self.namestring