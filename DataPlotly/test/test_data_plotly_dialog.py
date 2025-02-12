# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'matteo.ghetta@gmail.com'
__date__ = '2017-03-05'
__copyright__ = 'Copyright 2017, matteo ghetta'

import unittest
import tempfile
import os

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsProperty
)
from qgis.PyQt.QtCore import QCoreApplication

from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.gui.plot_settings_widget import DataPlotlyPanelWidget

from DataPlotly.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class DataPlotlyDialogTest(unittest.TestCase):
    """Test dialog works."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read_triggered = False

    def test_get_settings(self):
        """
        Test retrieving settings from the dialog
        """
        dialog = DataPlotlyPanelWidget(None, iface=IFACE)
        settings = dialog.get_settings()
        # default should be scatter plot
        self.assertEqual(settings.plot_type, 'scatter')

        dialog.set_plot_type('violin')
        settings = dialog.get_settings()
        # default should be scatter plot
        self.assertEqual(settings.plot_type, 'violin')

    def test_set_default_settings(self):
        """
        Test setting dialog to a newly constructed settings object
        """
        settings = PlotSettings()
        dialog = DataPlotlyPanelWidget(None, iface=IFACE)
        dialog.set_settings(settings)

        self.assertEqual(dialog.get_settings().plot_type, settings.plot_type)
        for k in settings.properties.keys():
            if k in ['x', 'y', 'z', 'additional_hover_text', 'featureIds', 'featureBox', 'custom', 'in_color',
                     'marker_size']:
                continue

            print(k)
            self.assertEqual(dialog.get_settings().properties[k], settings.properties[k])
        for k in settings.layout.keys():
            print(k)
            self.assertEqual(dialog.get_settings().layout[k], settings.layout[k])

    def test_settings_round_trip(self):  # pylint: disable=too-many-statements
        """
        Test setting and retrieving settings results in identical results
        """
        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.geojson')

        vl1 = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        vl2 = QgsVectorLayer(layer_path, 'test_layer1', 'ogr')
        vl3 = QgsVectorLayer(layer_path, 'test_layer2', 'ogr')
        QgsProject.instance().addMapLayers([vl1, vl2, vl3])

        dialog = DataPlotlyPanelWidget(None, iface=IFACE)
        settings = dialog.get_settings()
        # default should be scatter plot
        self.assertEqual(settings.plot_type, 'scatter')

        # customise settings
        settings.plot_type = 'violin'
        settings.properties['name'] = 'my legend title'
        settings.properties['hover_text'] = 'y'
        settings.properties['box_orientation'] = 'h'
        settings.properties['normalization'] = 'probability'
        settings.properties['box_stat'] = 'sd'
        settings.properties['box_outliers'] = 'suspectedoutliers'
        settings.properties['violin_side'] = 'negative'
        settings.properties['show_mean_line'] = True
        settings.properties['cumulative'] = True
        settings.properties['invert_hist'] = 'decreasing'
        settings.source_layer_id = vl3.id()
        settings.properties['x_name'] = 'so4'
        settings.properties['y_name'] = 'ca'
        settings.properties['z_name'] = 'mg'
        settings.properties['in_color_value'] = '100,150,180,50'
        settings.properties['in_color_property'] = QgsProperty.fromExpression('5+6').toVariant()
        settings.properties['size_property'] = QgsProperty.fromExpression('5+64').toVariant()
        settings.properties['color_scale'] = 'Earth'
        settings.properties['colorscale_in'] = 'Earth'

        # TODO: likely need to test other settings.properties values here!

        settings.layout['legend'] = False
        settings.layout['legend_orientation'] = 'h'
        settings.layout['title'] = 'my title'
        settings.layout['x_title'] = 'my x title'
        settings.layout['y_title'] = 'my y title'
        settings.layout['z_title'] = 'my z title'
        settings.layout['range_slider']['visible'] = True
        settings.layout['bar_mode'] = 'overlay'
        settings.layout['x_type'] = 'log'
        settings.layout['y_type'] = 'category'
        settings.layout['x_inv'] = 'reversed'
        settings.layout['y_inv'] = 'reversed'
        settings.layout['bargaps'] = 0.8
        settings.layout['additional_info_expression'] = '1+2'
        settings.layout['bins_check'] = True

        dialog2 = DataPlotlyPanelWidget(None, iface=IFACE)
        dialog2.set_settings(settings)

        self.assertEqual(dialog2.get_settings().plot_type, settings.plot_type)
        for k in settings.properties.keys():
            if k in ['x', 'y', 'z', 'additional_hover_text', 'featureIds', 'featureBox', 'custom', 'in_color',
                     'marker_size']:
                continue

            print(k)
            self.assertEqual(dialog2.get_settings().properties[k], settings.properties[k])
        for k in settings.layout.keys():
            print(k)
            self.assertEqual(dialog2.get_settings().layout[k], settings.layout[k])
        self.assertEqual(dialog2.get_settings().source_layer_id, vl3.id())

        settings = dialog.get_settings()
        dialog3 = DataPlotlyPanelWidget(None, iface=IFACE)
        dialog3.set_settings(settings)

        self.assertEqual(dialog3.get_settings().plot_type, settings.plot_type)
        for k in settings.properties.keys():
            print(k)
            self.assertEqual(dialog3.get_settings().properties[k], settings.properties[k])
        self.assertEqual(dialog3.get_settings().properties, settings.properties)
        for k in settings.layout.keys():
            print(k)
            self.assertEqual(dialog3.get_settings().layout[k], settings.layout[k])

        QgsProject.instance().clear()

    def test_read_write_project(self):
        """
        Test saving/restoring dialog state in project
        """
        p = QgsProject.instance()
        dialog = DataPlotlyPanelWidget(None, iface=IFACE)
        dialog.set_plot_type('violin')

        # first, disable saving to project
        dialog.read_from_project = False
        dialog.save_to_project = False

        path = os.path.join(tempfile.gettempdir(), 'test_dataplotly_project.qgs')
        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.geojson')

        # create QgsVectorLayer from path and test validity
        vl = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        self.assertTrue(vl.isValid())

        # print(dialog.layer_combo.currentLayer())

        self.assertTrue(p.write(path))

        res = PlotSettings()

        # def read(doc):
        #    self.assertTrue(res.read_from_project(doc))
        #    self.assertEqual(res.plot_type, 'violin')
        #    self.read_triggered = True

        p.clear()
        for _ in range(100):
            QCoreApplication.processEvents()

        self.assertTrue(p.read(path))
        self.assertEqual(res.plot_type, 'scatter')

        # TODO - enable when dialog can restore properties and avoid this fragile test
        # # enable saving to project
        # dialog.save_to_project = True
        # dialog.read_from_project = True
        # self.assertTrue(p.write(path))
        # for _ in range(100):
        #     QCoreApplication.processEvents()

        # p.clear()

        # p.readProject.connect(read)
        # self.assertTrue(p.read(path))
        # for _ in range(100):
        #     QCoreApplication.processEvents()

        # self.assertTrue(self.read_triggered)

        # todo - test that dialog can restore properties, but requires the missing set_settings method
        dialog.x_combo.setExpression('"Ca"')
        dialog.layer_combo.setLayer(vl)

        dialog.x_combo.currentText()

        self.assertTrue(dialog.x_combo.expression(), '"Ca"')


if __name__ == "__main__":
    suite = unittest.makeSuite(DataPlotlyDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
