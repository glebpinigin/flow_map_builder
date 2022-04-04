from qgis.core import QgsMessageLog

class SpiralTreeContext:

    def __init__(self, namestring="", lyr=None, expr=None, vol_flds=None, alpha=25, proj=None):
        self.namestring = namestring
        self.lyr = lyr
        self.expr = expr
        self.vol_flds = vol_flds
        self.alpha = alpha
        self.proj = proj
        self.created = False
        self.styled = False
        self.saved = False
    
    def updateCreateContext(self, namestring=None, lyr=None, expr=None, vol_flds=None, alpha=None, proj=None):
        self.namestring = namestring if namestring is not None else self.namestring
        self.lyr = lyr if lyr is not None else self.lyr
        self.expr = expr if expr is not None else self.expr
        self.vol_flds = vol_flds if vol_flds is not None else self.vol_flds
        self.alpha = alpha if alpha is not None else self.alpha
        self.proj = proj if proj is not None else self.proj

    def updateStyleContext(self):
        pass

    def updateSaveContext(self):
        pass
    
    def getCreationKwargs(self):
        return {
            "namestring": self.namestring,
            "lyr": self.lyr,
            "expr": self.expr,
            "vol_flds": self.vol_flds,
            "alpha":self.alpha,
            "proj": self.proj
        }
    
    def isCreated(self):
        return self.created

    def setOutLyr(self, out_lyr):
        self.created = True
        self.out_lyr = out_lyr

    def log(self):
        QgsMessageLog.logMessage(f'namestring {self.namestring}\nlyr {self.lyr}\nexpr {self.expr}\nvol_flds {self.vol_flds}\nalpha {self.alpha}\nproj {self.proj}')

    def __repr__(self):
        return self.namestring