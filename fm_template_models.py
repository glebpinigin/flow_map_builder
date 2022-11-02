from qgis.core import QgsMessageLog

class SpiralTreeContext:

    def __init__(
            self, namestring="", lyr=None, expr=None,
            vol_flds=None, alpha=25, proj=None, stop_dst=0):
        self.namestring = namestring
        self.lyr = lyr
        self.expr = expr
        self.vol_flds = vol_flds if vol_flds is not None else []
        self.alpha = alpha
        self.stop_dst = stop_dst
        self.geom_n = 4
        self.proj = proj
        self.created = False
        self.scaled = False
        self.styled = False
        self.saved = False

        self.display_flds = []
        self.use_total_flow = False
        self.use_scale_attr = True
        self.scale_attr = None
        self.min_flow = None
        self.max_flow = None
        self.min_width = None
        self.max_width = None
        self.soft_scale = False
        self.units = "millimeters"

        self.color = None
        self.spline_n = 21

    def updateCreateContext(
            self,
            namestring=None,
            lyr=None,
            expr=None,
            vol_flds=None,
            alpha=None,
            stop_dst=None,
            geom_n=None,
            proj=None):
        self.namestring = namestring if namestring is not None else self.namestring
        self.lyr = lyr if lyr is not None else self.lyr
        self.expr = expr if expr is not None else self.expr
        self.vol_flds = vol_flds if vol_flds is not None else self.vol_flds
        self.alpha = alpha if alpha is not None else self.alpha
        self.stop_dst = stop_dst if stop_dst is not None else self.stop_dst
        self.geom_n = geom_n if geom_n is not None else self.geom_n
        self.proj = proj if proj is not None else self.proj

    def updateStyleContext(
            self,
            display_flds=None,
            use_total_flow=None,
            use_scale_attr=None,
            scale_attr=None,
            min_flow=None,
            max_flow=None,
            min_width=None,
            max_width=None,
            soft_scale=None,
            spline_n=None,
            color=None,
            units=None):
        self.display_flds = display_flds if display_flds is not None else self.display_flds
        self.use_total_flow = use_total_flow if use_total_flow is not None else self.use_total_flow
        self.use_scale_attr = use_scale_attr if use_scale_attr is not None else self.use_scale_attr

        self.scale_attr = scale_attr if scale_attr is not None else self.scale_attr
        self.min_flow = min_flow if min_flow is not None else self.min_flow
        self.max_flow = max_flow if max_flow is not None else self.max_flow
        self.min_width = min_width if min_width is not None else self.min_width
        self.max_width = max_width if max_width is not None else self.max_width
        self.soft_scale = soft_scale if soft_scale is not None else self.soft_scale

        self.color = color if color is not None else self.color
        self.spline_n = spline_n if spline_n is not None else self.spline_n
        self.units = units if units is not None else self.units

    def updateSaveContext(self):
        pass
    
    def getCreationKwargs(self):
        return {
            "namestring": self.namestring,
            "lyr": self.lyr,
            "expr": self.expr,
            "vol_flds": self.vol_flds.copy(),
            "alpha": self.alpha,
            "stop_dst": self.stop_dst,
            "geom_n": self.geom_n,
            "proj": self.proj
        }
    
    def getScaleKwargs(self):
        return {
            "out_lyr": self.out_lyr,
            "display_flds": self.display_flds,
            "min_flow": self.min_flow,
            "max_flow": self.max_flow,
            "min_width": self.min_width,
            "max_width": self.max_width,
            "soft_scale": self.soft_scale
        }

    def getStyleKwargs(self):
        return {
            "out_lyr": self.out_lyr,
            "spline_n": self.spline_n,
            "display_fld": self.display_flds[0],
            "units": self.units,
            "color": self.color
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