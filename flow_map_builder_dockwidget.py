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

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal

from qgis.utils import iface
from qgis.core import QgsProject, QgsGeometryGeneratorSymbolLayer, QgsLineSymbol, QgsSingleSymbolRenderer

from .fm_template_models import SpiralTreeContext

from flowmapper import flowTreeBuildAction

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'flow_map_builder_dockwidget_base.ui'))


class FlowMapBuilderDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(FlowMapBuilderDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        # header connections
        self.add_tree.clicked.connect(self.addTree)
        self.context_hub.currentIndexChanged[int].connect(self.currentContextChanged)
        
        # first tab connections
        self.layer_combobox.layerChanged.connect(self.layerChanged)
        self.expression_field.fieldChanged[str, bool].connect(self.expressionChanged)
        self.fields_combobox.checkedItemsChanged.connect(self.fieldChanged)
        self.alpha_spin_box.valueChanged.connect(self.alphaChanged)
        self.stop_dst_spin_box.valueChanged.connect(self.stop_dstChanged)
        self.mQgsProjectionSelectionWidget.crsChanged.connect(self.crsChanged)
        self.build_button.clicked.connect(self.buildTree)

        # second tab connections
        self.display_field_combobox.checkedItemsChanged.connect(self.displayFieldChanged)
        self.color_selector.colorChanged.connect(self.colorChanged)
        self.buffer_coef.valueChanged.connect(self.bufferCoefChanged)
        self.unit_selector.changed.connect(self.unitTypeChanged)
        # self.unit_selector.setUnits TODO: В эту функцию надо подать список из QgsUnitTypes
        self.style_button.clicked.connect(self.symbolizeLayer)

        # attributes
        self.contexts = []

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
        self.display_field_combobox.setLayer(out_lyr)
        if not self.currentContext.isStyled():
            out_lyr.renderer().symbol().setColor(self.currentContext.color)
            self.color_selector.setColor(self.currentContext.color)
            out_lyr.triggerRepaint()
        else:
            out_lyr.setRenderer(QgsSingleSymbolRenderer(self.currentContext.symbol))
            out_lyr.triggerRepaint()



    def addTree(self):
        dlg = AddDialogWidget(dock=self)
        if dlg.exec():
            self.tab_widget.setEnabled(True)
            self.currentContext = SpiralTreeContext(namestring=dlg.namestring, proj=iface.mapCanvas().mapSettings().destinationCrs())
            self.contexts.append(self.currentContext)
            self.context_hub.addItem(str(self.currentContext))
            self.context_hub.setCurrentIndex(len(self.contexts)-1)
        else:
            pass
    
    def currentContextChanged(self, index):
        self.currentContext = self.contexts[index]
        self.layer_combobox.setLayer(self.currentContext.lyr)
        self.expression_field.setField(self.currentContext.expr)
        vol_flds = self.currentContext.vol_flds
        self.fields_combobox.deselectAllOptions()
        self.fields_combobox.setCheckedItems(vol_flds)
        self.alpha_spin_box.setValue(self.currentContext.alpha)
        self.stop_dst_spin_box.setValue(self.currentContext.stop_dst)
        self.mQgsProjectionSelectionWidget.setCrs(self.currentContext.proj)
        self.currentContext.log()

        if self.currentContext.isCreated():
            self.display_field.setLayer(self.currentContext.out_lyr)
            self.color_selector.setColor(self.currentContext.color)
        self.buffer_coef.setValue(self.currentContext.coef)
    
    def layerChanged(self, lyr):
        self.currentContext.updateCreateContext(lyr=lyr)
        self.expression_field.setLayer(lyr)
        self.fields_combobox.clear()
        if lyr is None:
            return
        for field in lyr.fields():
            self.fields_combobox.addItemWithCheckState(field.name(), False)
        self.fields_combobox.setCheckedItems(self.currentContext.vol_flds)


    def alphaChanged(self, alpha):
        self.currentContext.updateCreateContext(alpha=alpha)
    
    def stop_dstChanged(self, stop_dst):
        self.currentContext.updateCreateContext(stop_dst=stop_dst)

    def expressionChanged(self, expr, valid=False):
        if valid:
            self.currentContext.updateCreateContext(expr=expr)
        else:
            pass
    
    def fieldChanged(self, fieldlist):
        self.currentContext.updateCreateContext(vol_flds=fieldlist)
    
    def crsChanged(self, crs):
        self.currentContext.updateCreateContext(proj=crs)

    def displayFieldChanged(self, fieldlist):
        self.currentContext.updateStyleContext(display_fld=fieldlist)
    
    def colorChanged(self, color):
        self.currentContext.updateStyleContext(color=color)
    
    def bufferCoefChanged(self, coef):
        self.currentContext.updateStyleContext(coef=coef)

    def unitTypeChanged(self, unit):
        self.currentContext.updateStyleContext(units=unit)

    def symbolizeLayer(self):
        fld = self.currentContext.display_fld
        coef = self.currentContext.coef
        expression = f"drawSpiralTree(20)"
        generator = QgsGeometryGeneratorSymbolLayer.create({})
        generator.setGeometryExpression(expression)
        symbol = QgsLineSymbol()
        symbol.changeSymbolLayer(0, generator)
        symbol.setColor(self.currentContext.color)
        symbol.symbolLayers()[0].subSymbol().symbolLayers()[0].setStrokeStyle(0)
        self.currentContext.setSymbol(symbol)

        self.currentContext.out_lyr.setRenderer(QgsSingleSymbolRenderer(symbol))
        self.currentContext.out_lyr.triggerRepaint()

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
        self.name_area.textChanged[str].connect(self.setName)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def setName(self, name):
        self.namestring=name