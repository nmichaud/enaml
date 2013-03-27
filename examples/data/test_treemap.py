import numpy as np
import pandas

from enaml.qt.data.q_treemap_view import QTreemapView

from PyQt4.QtCore import QRect
from PyQt4.QtGui import QApplication, QWidget, QHBoxLayout


from treemap import pandas_pivot


def main():
    app = QApplication([])

    colname = '1 Day Change % (USD)'

    frame = pandas.read_csv('StocksStatic.csv')
    engine = pandas_pivot.PandasEngine.from_frame(
        frame,
        aggregates=[('Mcap(USD)', 'sum'), (colname, 'mean')],
        row_pivots=['Industry', 'Supersector', 'Name'],
        col_pivots=[],
        row_margins='before',
        col_margins='before',
    )

    tm = QTreemapView()
    tm.setEngine(engine)

    win = QWidget()
    layout = QHBoxLayout()
    layout.addWidget(tm)
    win.setLayout(layout)
    win.setGeometry(QRect(400, 200, 870, 705))
    win.show()
    app.exec_()

if __name__ == '__main__':
    main()
