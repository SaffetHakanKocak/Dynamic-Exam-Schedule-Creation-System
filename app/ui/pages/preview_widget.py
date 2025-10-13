from PyQt5 import QtWidgets, QtGui, QtCore

class PreviewWidget(QtWidgets.QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

    def draw_preview(self, rows, cols, group):
        self.scene.clear()
        box_w, box_h = 35, 25
        spacing = 8
        for i in range(rows):
            for j in range(cols):
                for k in range(group):
                    rect = QtCore.QRectF(
                        j * (box_w * group + spacing) + k * box_w,
                        i * (box_h + spacing),
                        box_w - 2, box_h - 2
                    )
                    self.scene.addRect(rect, QtGui.QPen(QtCore.Qt.black),
                                       QtGui.QBrush(QtGui.QColor(173, 216, 230)))
        self.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
