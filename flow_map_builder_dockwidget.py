# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FlowMapBuilderDockWidget
                                 A QGIS plugin
 This plugin builds flow maps
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-03-23
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Gleb Pinigin
        email                : pinigin1514@live.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import itertools

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal, QVariant, pyqtSlot

from qgis.utils import iface
from qgis.core import QgsProject, QgsGeometryGeneratorSymbolLayer, QgsLineSymbol, QgsSingleSymbolRenderer
from qgis.core import QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, QgsFieldProxyModel
from qgis.core.additions.edit import edit
from qgis.core import QgsField, QgsProperty, QgsUnitTypes

from .fm_template_models import SpiralTreeContext

from flowmapper import flowTreeBuildAction

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'flow_map_builder_dockwidget_base.ui'))


class FlowMapBuilderDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    _proproot = "fmp/"
    def __init__(self, parent=None):
        """Constructor."""
        print('construction')
        super(FlowMapBuilderDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.tab_style.setEnabled(False)
        self.tab_save.setEnabled(False)
        # header connections
        self.add_tree.clicked.connect(self.addTree)
        self.add_tree.setIcon(QtGui.QIcon(':/images/themes/default/symbologyAdd.svg'))
        self.context_hub.currentIndexChanged[int].connect(self.currentContextChanged)
        self.remove_tree.clicked.connect(self.removeTree)
        self.remove_tree.setIcon(QtGui.QIcon(':/images/themes/default/symbologyRemove.svg'))
        self.store_btn.toggled.connect(self.saveStateChanged)
        self.store_btn.setCheckable(True)
        self.store_btn.setIcon(QtGui.QIcon(':/images/themes/default/mActionFileSave.svg'))

        # first tab connections
        self.layer_combobox.layerChanged.connect(self.layerChanged)
        self.expression_field.fieldChanged[str, bool].connect(self.expressionChanged)
        self.fields_combobox.checkedItemsChanged.connect(self.fieldChanged)
        self.alpha_spin_box.valueChanged.connect(self.alphaChanged)
        self.stop_dst_spin_box.valueChanged.connect(self.stop_dstChanged)
        self.geom_n.valueChanged.connect(self.geomNChanged)
        self.mQgsProjectionSelectionWidget.crsChanged.connect(self.crsChanged)
        self.build_button.clicked.connect(self.buildTree)

        # second tab connections
        self.display_fields_combobox.checkedItemsChanged.connect(self.displayFieldChanged)
        self.use_total_flow.toggled.connect(self.useTotalFlow)
        self.use_scale_attr.toggled.connect(self.useAttr)
        self.scale_attr.setFilters(QgsFieldProxyModel.Numeric)
        self.scale_attr.fieldChanged.connect(self.scaleAttrChanged)
        self.min_flow.valueChanged.connect(self.minFlowChanged)
        self.max_flow.valueChanged.connect(self.maxFlowChanged)
        self.min_width.valueChanged.connect(self.minWidthChanged)
        self.max_width.valueChanged.connect(self.maxWidthChanged)
        self.retrieve_button.clicked.connect(self.updateMinMax)
        self.soft_scale.stateChanged.connect(self.softScaleChanged)
        self.spline_n.valueChanged.connect(self.splineNChanged)
        self.unit_selector.addItems(["mm", "points", "inch", "meters", "mapunits"])
        self.unit_selector.currentTextChanged.connect(self.unitsChanged)
        self.color_selector.colorChanged.connect(self.colorChanged)
        self.style_button.clicked.connect(self.symbolizeLayer)

        # attributes
        self.contexts = []

        QgsProject.instance().cleared.connect(self.onProjectReset)
    
    # ---------------------------- header connections ---------------------------- #

    def buildTree(self):
        if not self.currentContext.isCreated():
            kwargs = self.currentContext.getCreationKwargs()
            out_lyr = flowTreeBuildAction(**kwargs)
            self.currentContext.setOutLyr(out_lyr)
            QgsProject.instance().addMapLayer(out_lyr)
            self.currentContext.updateStyleContext(color=out_lyr.renderer().symbol().color())
        else:
            try:
                QgsProject.instance().removeMapLayer(self.currentContext.out_lyr)
            except RuntimeError:
                pass
            kwargs = self.currentContext.getCreationKwargs()
            out_lyr = flowTreeBuildAction(**kwargs)
            self.currentContext.setOutLyr(out_lyr)
            QgsProject.instance().addMapLayer(out_lyr)
            #out_lyr.updatedFields.connect. # TODO: connect with field drop checklists
        # field comboboxes connection:
        self.display_fields_combobox.clear()
        for name in self.currentContext.vol_flds:
            self.display_fields_combobox.addItemWithCheckState(name, False)
        self.display_fields_combobox.setCheckedItems(self.currentContext.display_flds)
        self.scale_attr.setLayer(self.currentContext.out_lyr)
        self.scale_attr.setField(self.currentContext.scale_attr)
        if not self.currentContext.isStyled():
            out_lyr.renderer().symbol().setColor(self.currentContext.color)
            self.color_selector.setColor(self.currentContext.color)
            out_lyr.triggerRepaint()
        else:
            out_lyr.setRenderer(QgsSingleSymbolRenderer(self.currentContext.symbol))
            out_lyr.triggerRepaint()
        self.tab_style.setEnabled(True)
        self.tab_save.setEnabled(True)
        # TODO: do something if styled


    @pyqtSlot()
    def addTree(self):
        dlg = AddDialogWidget(parent=self, dock=self)
        if dlg.exec():
            self.tab_widget.setEnabled(True)
            if dlg.state:
                lyr = dlg.layer
                props = lyr.customProperties() # type: ignore
                kwargs = {}
                for key in props.keys():
                    kwarg = key[len(self._proproot):]
                    val = props.value(key)
                    kwargs[kwarg] = val
                
                self.currentContext = SpiralTreeContext.fromSaveKwargs(**kwargs)
            else:
                self.currentContext = SpiralTreeContext(namestring=dlg.namestring, proj=iface.mapCanvas().mapSettings().destinationCrs())
            self.contexts.append(self.currentContext)
            self.context_hub.addItem(str(self.currentContext))
            self.context_hub.setCurrentIndex(len(self.contexts)-1)
        else:
            pass
        
        del dlg
    
    @pyqtSlot()
    def removeTree(self):
        print('попытка удаления')
        if len(self.contexts) > 1:
            del self.currentContext
            self.currentContext = self.contexts[-1]
        elif len(self.contexts) == 0:
            pass
        else:
            pass

    @pyqtSlot()
    def saveStateChanged(self, key):
        if key:
            QgsProject.instance().writeProject.connect(self.addLayerProperties)
        else:
            QgsProject.instance().writeProject.disconnect(self.addLayerProperties)

    @pyqtSlot()
    def currentContextChanged(self, index):
        self.currentContext = self.contexts[index]
        # first tab independent values
        self.store_btn.setChecked(self.currentContext.store_checkstate)
        self.layer_combobox.setLayer(self.currentContext.lyr)
        self.expression_field.setField(self.currentContext.expr)
        vol_flds = self.currentContext.vol_flds
        self.fields_combobox.deselectAllOptions()
        self.fields_combobox.setCheckedItems(vol_flds)
        self.alpha_spin_box.setValue(self.currentContext.alpha)
        self.stop_dst_spin_box.setValue(self.currentContext.stop_dst)
        self.geom_n.setValue(self.currentContext.geom_n)
        self.mQgsProjectionSelectionWidget.setCrs(self.currentContext.proj)
        self.currentContext.log()

        # second tab independent values
        if self.currentContext.isCreated():
            display_flds = self.currentContext.display_flds
            self.display_fields_combobox.clear()
            for name in self.currentContext.vol_flds:
                self.display_fields_combobox.addItemWithCheckState(name, False)
            self.display_fields_combobox.setCheckedItems(display_flds)
            self.scale_attr.setLayer(self.currentContext.out_lyr)
            self.scale_attr.setField(self.currentContext.scale_attr)
            self.color_selector.setColor(self.currentContext.color)
        self.min_flow.setValue(self.currentContext.min_flow)
        self.max_flow.setValue(self.currentContext.max_flow)
        self.min_width.setValue(self.currentContext.min_width)
        self.max_width.setValue(self.currentContext.max_width)
        self.soft_scale.setChecked(self.currentContext.soft_scale)
        self.spline_n.setValue(self.currentContext.spline_n)
        self.unit_selector.setCurrentText(self.currentContext.units)
        self.tab_save.setEnabled(self.currentContext.isCreated())
        self.tab_style.setEnabled(self.currentContext.isCreated())

    # --------------------------- first tab connections -------------------------- #

    @pyqtSlot()
    def layerChanged(self, lyr):
        self.currentContext.updateCreateContext(lyr=lyr)
        self.expression_field.setLayer(lyr)
        self.fields_combobox.clear()
        if lyr is None:
            return
        for field in lyr.fields():
            self.fields_combobox.addItemWithCheckState(field.name(), False)
        self.fields_combobox.setCheckedItems(self.currentContext.vol_flds)

    @pyqtSlot()
    def alphaChanged(self, alpha):
        self.currentContext.updateCreateContext(alpha=alpha)
    
    @pyqtSlot()
    def stop_dstChanged(self, stop_dst):
        self.currentContext.updateCreateContext(stop_dst=stop_dst)
    
    @pyqtSlot()
    def geomNChanged(self, geom_n):
        self.currentContext.updateCreateContext(geom_n=geom_n)
    
    @pyqtSlot()
    def expressionChanged(self, expr, valid=False):
        if valid:
            self.currentContext.updateCreateContext(expr=expr)
        else:
            pass
    
    @pyqtSlot()
    def fieldChanged(self, fieldlist):
        self.currentContext.updateCreateContext(vol_flds=fieldlist)
    
    @pyqtSlot()
    def crsChanged(self, crs):
        self.currentContext.updateCreateContext(proj=crs)

    # -------------------------- second tab connections -------------------------- #

    @pyqtSlot()
    def displayFieldChanged(self, display_flds):
        self.currentContext.updateStyleContext(display_flds=display_flds)
    
    @pyqtSlot()
    def useTotalFlow(self, state):
        self.currentContext.updateStyleContext(use_total_flow=state)
        self.scale_attr.setEnabled(False)

    @pyqtSlot()
    def useAttr(self, state):
        self.currentContext.updateStyleContext(use_scale_attr=state)
        self.scale_attr.setEnabled(True)

    @pyqtSlot()
    def scaleAttrChanged(self, scale_attr):
        self.currentContext.updateStyleContext(scale_attr=scale_attr)

    @pyqtSlot()
    def minFlowChanged(self, min_flow):
        self.currentContext.updateStyleContext(min_flow=min_flow)

    @pyqtSlot()
    def maxFlowChanged(self, max_flow):
        self.currentContext.updateStyleContext(max_flow=max_flow)

    @pyqtSlot()
    def updateMinMax(self):
        attrname = self.currentContext.scale_attr
        out_lyr = self.currentContext.out_lyr
        idx = out_lyr.fields().indexFromName(attrname)
        min, max = out_lyr.minimumAndMaximumValue(idx)
        self.min_flow.setValue(min)
        self.max_flow.setValue(max)

    @pyqtSlot()
    def minWidthChanged(self, min_width):
        self.currentContext.updateStyleContext(min_width=min_width)

    @pyqtSlot()
    def maxWidthChanged(self, max_width):
        self.currentContext.updateStyleContext(max_width=max_width)

    @pyqtSlot()
    def softScaleChanged(self, state):
        state = True if state == 2 else False
        self.currentContext.updateStyleContext(soft_scale=state)

    @pyqtSlot()
    def splineNChanged(self, spline_n):
        self.currentContext.updateStyleContext(spline_n=spline_n)

    @pyqtSlot()
    def colorChanged(self, color):
        self.currentContext.updateStyleContext(color=color)

    @pyqtSlot()
    def unitsChanged(self, unit):
        self.currentContext.updateStyleContext(units=unit)

    @staticmethod
    def _calculateWidthAttributes(out_lyr, display_flds, min_flow, max_flow,
                                  min_width, max_width, soft_scale):
        if soft_scale:
            fun = "soft_scale_linear"
        else:
            fun = "scale_linear"
        
        pv = out_lyr.dataProvider()
        
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(out_lyr))
        for name in display_flds:
            pv.addAttributes([QgsField(f"{name}_width", QVariant.Double)])
            expr_string = f"{fun}({name}, {min_flow}, {max_flow}, {min_width}, {max_width})"
            expression = QgsExpression(expr_string)
            with edit(out_lyr):
                for fet in out_lyr.getFeatures():
                    context.setFeature(fet)
                    fet[f"{name}_width"] = expression.evaluate(context)
                    out_lyr.updateFeature(fet)

    def calculateWidthAttributes(self):
        kwargs = self.currentContext.getScaleKwargs()
        self._calculateWidthAttributes(**kwargs)

    @staticmethod
    def _symbolizeLayer(out_lyr, spline_n, display_fld, units, color):
        expression = f"drawTree( {spline_n}, get_feature( @layer, 'target', \"source\"), array('{display_fld}'), '{units}')"
        generator = QgsGeometryGeneratorSymbolLayer.create({"SymbolType":"Line",
                                                            "capstyle": "round"})
        generator.setGeometryExpression(expression)
        symbol = QgsLineSymbol()
        symbol.changeSymbolLayer(0, generator)
        symbol.setColor(color)
        #symbol.symbolLayers()[0].subSymbol().symbolLayers()[0].setStrokeStyle(0)
        # Iterating is for 
        # volsstr = ""
        # for name in display_fld:
        #     volsstr = volsstr + f"{name},"
        expression = f"\"{display_fld}_width\""
        symbol.symbolLayers()[0].subSymbol().setDataDefinedWidth(QgsProperty.fromExpression(expression))
        unit = QgsUnitTypes().decodeRenderUnit(units)[0]
        symbol.symbolLayers()[0].subSymbol().setWidthUnit(unit)
        out_lyr.setRenderer(QgsSingleSymbolRenderer(symbol))
        out_lyr.triggerRepaint()

    @pyqtSlot()
    def symbolizeLayer(self):
        self.calculateWidthAttributes()
        kwargs = self.currentContext.getStyleKwargs()
        self._symbolizeLayer(**kwargs)
        # self.currentContext.setSymbol(symbol)

    # --------------------------- third tab connections -------------------------- #
    
    @pyqtSlot()
    def addLayerProperties(self, *args, **kwargs):
        for context in self.contexts:
            props = context.getSaveKwargs()
            for key, value in props.items():
                context.out_lyr.setCustomProperty(self._proproot + key, value)

    @pyqtSlot()
    def onProjectReset(self):
        try:
            QgsProject.instance().writeProject.disconnect(self.addLayerProperties)
        except TypeError as err:
            print(f'disconnect write: {err}')
        self.deleteLater()
    
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

FORM_CLASS2, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'add_dialog_widget.ui'))

class AddDialogWidget(QtWidgets.QDialog, FORM_CLASS2):

    def __init__(self, parent=None, dock=None):
        super(AddDialogWidget, self).__init__(parent)
        self.dock = dock
        self.setupUi(self)
        self.layer = None
        self.namestring = ""
        self.state = False
        self.name_area.textChanged[str].connect(self.setName)
        self.unpack_state.stateChanged.connect(self.setState)
        self.layer_check.layerChanged.connect(self.setLayer)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def __del__(self):
        # TODO: find correct deconstructor
        del self.unpack_state
        del self.layer_check
        del self.buttonBox
        del self.name_area

    def setName(self, name):
        self.namestring=name
    
    def setState(self, state):
        state = True if state == 2 else False
        self.state = state
        self.layer_check.setEnabled(state)
        self.name_area.setEnabled(not state)

    def setLayer(self, layer):
        self.layer = layer
        self.setName(self.layer.name())