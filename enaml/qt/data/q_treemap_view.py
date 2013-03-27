#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import numpy as np
from itertools import repeat
from collections import defaultdict, deque

from PyQt4.QtCore import Qt, QRect
from PyQt4.QtGui import QWidget, QPainter, QColor, QSizePolicy, QFontMetrics

from enaml.dataext import fast_layout

class QTreemapView(QWidget):

    #: Render the tree map in classic style
    ClassicStyle = 0

    #: Render the tree map in cluster style
    ClusterStyle = 1

    def __init__(self, parent=None):
        super(QTreemapView, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._engine = None
        self._rect_cache = defaultdict(list)
        self._render_depth = 0
        self._style = QTreemapView.ClusterStyle

        font = self.font()
        font.setPointSize(8)
        fm = QFontMetrics(font)
        small_spacing = fm.lineSpacing()
        self._line_heights = defaultdict(lambda: (font, small_spacing))

        font = self.font()
        font.setPointSize(9)
        fm = QFontMetrics(font)
        spacing = fm.lineSpacing()
        self._line_heights[0] = (font, spacing)
        self._line_heights[1] = (font, spacing)

        # XXX This is a hack
        from chaco.api import RdBu, DataRange1D

        self._cm = cm = RdBu(range=DataRange1D())
        cm.range.low = -0.1
        cm.range.high = 0.1

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def engine(self):
        """ Get the pivot engine used by the widget.

        Returns
        -------
        result : PivotEngine
            The tabular engine being viewed by the widget.

        """
        return self._engine

    def setEngine(self, engine):
        """ Set the engine being viewed by the widget.

        Parameters
        ----------
        engine : TabularModel
            The engine to be viewed by the widget.

        """
        self._engine = engine
        self._render_depth = engine.max_depth
        self._update_layout()

    def style(self):
        """ Get the style of the treemap.

        Returns
        -------
        result : int
            The current style of the treemap.

        """
        return self._style

    def setStyle(self, style):
        """ Set the style of the treemap.

        The default style is ClusterStyle.

        Parameters
        ----------
        style : int
            One of QTreemapView.ClassicStyle or QTreemapView.ClusterStyle.

        """
        valid = (QTreemapView.ClassicStyle, QTreemapView.ClusterStyle)
        assert style in valid
        self._style = style
        self._update_layout()

    def setDepth(self, depth):
        """ Set the currently rendered depth of the QTreemapView.

        Parameters
        ----------
        depth : int
            The depth to render the tree.

        """
        self._render_depth = depth
        self.update()

    def resizeEvent(self, event):
        """ Override the resize event to perform a layout at the new size.
        """
        super(QTreemapView, self).resizeEvent(event)
        self._update_layout()

    def paintEvent(self, event):
        """ Override the paint event to draw the treemap.

        """
        painter = QPainter(self)

        render_depth = self._render_depth

        _, top_level_height = self._line_heights[0]

        for depth in range(1, render_depth+1):
            font, spacing = self._line_heights[depth]
            fm = QFontMetrics(font)
            char_width = fm.averageCharWidth()*2

            #name, rect, color = self._rect_cache[depth][0]
            #max_area = float(rect[2]*rect[3])

            for name, rect, color in self._rect_cache[depth]:
                if (self._style == QTreemapView.ClusterStyle or
                        depth == render_depth):
                    rect = QRect(*rect)
                    cell = QColor(*color)
                    #alpha = ((rect.width()*rect.height())/max_area)*127+127
                    #cell.setAlpha(alpha)
                    painter.fillRect(rect, cell)

                    #top_border = cell.lighter(130)
                    #bottom_border = cell.darker(130)
                    #painter.setPen(bottom_border)
                    #painter.drawRect(rect)
                    #painter.drawPolyline(*[rect.bottomLeft(), rect.bottomRight(),
                    #                      rect.topRight()])
                    #painter.setPen(top_border)
                    #painter.drawPolyline(*[rect.topRight(), rect.topLeft(),
                    #                      rect.bottomLeft()])

                else:
                    text_pen = Qt.black
                    painter.setPen(text_pen)
                    painter.drawRect(rect)

                text_pen = Qt.black

                rect = rect.adjusted(3, 2, -5, 0)
                if (rect.width() > char_width and
                    (self._style == QTreemapView.ClusterStyle or
                     depth in (1, render_depth))):
                    if depth == 1:
                        painter.setPen(Qt.black)
                        painter.setFont(font)
                    else:
                        painter.setPen(text_pen)
                        painter.setFont(font)
                    text = str(name)
                    painter.drawText(rect, Qt.AlignLeft | Qt.AlignTop, text)

    def _update_layout(self):
        """ Recompute treemap squarify layout.

        """
        self._rect_cache = defaultdict(list)

        bounds = self.rect().adjusted(1, 1, -1, -1)
        x, y, w, h = bounds.x(), bounds.y(), bounds.width(), bounds.height()

        tree_iter = self._engine.walk_tree()
        _process_list = deque([((x, y, w, h), 1)])

        pl_len = _process_list.__len__
        pl_pop = _process_list.popleft
        pl_extend = _process_list.extend

        tn = tree_iter.next

        colormap = self._cm.map_screen

        layout = fast_layout

        while pl_len():
            (x, y, w, h), depth = pl_pop()

            is_leaf, (index, pt, pt2) = tn()

            rects = layout(pt, x, y, w, h)

            self._rect_cache[depth].extend(
                zip(index, rects, colormap(pt2)*255),
            )

            if not is_leaf:
                d = depth + 1
                if self._style == QTreemapView.ClusterStyle:
                    _, line_height = self._line_heights[depth]
                    height = line_height + 6
                    pl_extend((((x+5,y+height,w-10,h-height-5), d) for x, y, w, h, in rects))
                else:
                    pl_extend(((r, d) for r in rects))

        self.update()

    def _layout(self, pt, x, y, w, h):
        size = len(pt)
        if size == 0:
            return []
        elif (size < 2):
            return self._slice_layout(pt, x, y, w, h)

        factors = pt / pt.sum()
        f_accum = factors.cumsum()

        if (w < h):
            aspects = (h * f_accum) / (w * factors / f_accum)
            aspects[aspects < 1] = 1 / aspects
            mid = np.argmin(aspects)
            b = f_accum[mid]

            rects = self._slice_layout(pt[:mid + 1], x, y, w, round(h * b))
            return rects + self._layout(pt[mid + 1:], x, y + round(h * b),w,round(h * (1 - b)))
        else:
            aspects = (w * f_accum) / (h * factors / f_accum)
            aspects[aspects < 1] = 1 / aspects
            mid = np.argmin(aspects)
            b = f_accum[mid]

            rects = self._slice_layout(pt[:mid + 1], x, y, round(w * b), h)
            return rects + self._layout(pt[mid + 1:], x + round(w * b), y, round(w * (1 - b)),h)

    def _slice_layout(self, pt, x, y, width, height):
        factors = pt / pt.sum()

        if width <= height:
            heights = np.round(height * factors)
            accum = y + np.zeros(len(factors))
            accum[1:] += heights.cumsum()[:-1]
            # Account for rounding errors
            heights[-1] -= round(sum(heights - height * factors))
            rects = [(x, a, width, h) for a, h in zip(accum, heights)]
        else:
            widths = np.round(width * factors)
            accum = x + np.zeros(len(factors))
            accum[1:] += widths.cumsum()[:-1]
            # Account for rounding errors
            widths[-1] -= round(sum(widths - width * factors))
            rects = [(a, y, w, height) for a, w in zip(accum, widths)]

        return rects
