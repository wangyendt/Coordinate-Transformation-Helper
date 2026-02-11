# author: wangye(Wayne)
# license: Apache Licence
# file: coordinate_helper_gui.py
# time: 2023-11-23-13:57:02
# contact: wang121ye@hotmail.com
# site:  wangyendt@github.com
# software: PyCharm
# code is far away from bugs.


import numpy as np
from typing import *
from dataclasses import dataclass
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from coordinate_transformation_helper import Ui_MainWindow


def count_inversions(sequence):
    inversions = 0
    for i in range(len(sequence)):
        for j in range(i + 1, len(sequence)):
            if sequence[i] > sequence[j]:
                inversions += 1
    return inversions


def matrix_times_quaternion_str(quaternion_matrix, quaternion_str):
    elements = quaternion_str.split(r',')
    result = []
    for row in quaternion_matrix:
        row_string = ""
        for i, element in enumerate(elements):
            if row[i] == -1:
                row_string += "-" + element
            elif row[i] == 1:
                row_string += element
        result.append(row_string)
    result_string = r','.join(result)
    return result_string


@dataclass
class Direction:
    axis: str
    sign: int
    color: QColor


@dataclass
class Axis:
    right_left: Direction
    up_down: Direction
    back_front: Direction


QT_COLOR = {
    'X': Qt.red,
    'Y': Qt.green,
    'Z': Qt.blue
}


WEAR_MODE_CHOICES = [
    ('left_crown_right', '左手-表冠右(基准)', 'L-CR'),
    ('left_crown_left', '左手-表冠左', 'L-CL'),
    ('right_crown_right', '右手-表冠右', 'R-CR'),
    ('right_crown_left', '右手-表冠左', 'R-CL'),
]


class CoordinateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.axes = Axis(
            Direction('X', 1, Qt.red),
            Direction('Y', 1, Qt.green),
            Direction('Z', 1, Qt.blue)
        )

    @property
    def handness(self):
        inversions = count_inversions([self.axes.right_left.axis, self.axes.up_down.axis, self.axes.back_front.axis])
        return (-1 if inversions & 1 else 1) * self.axes.right_left.sign * self.axes.up_down.sign * self.axes.back_front.sign

    @property
    def handness_str(self):
        return f'{"右" if self.handness == 1 else "左" if self.handness == -1 else "无"}手'

    def paintEvent(self, event, **kwargs):
        painter = QPainter(self)
        center = QPoint(self.width() // 2, self.height() // 2)

        lengthX = int(self.width() // 2 * self.axes.right_left.sign * 0.6)
        lengthY = int(self.height() // 2 * self.axes.up_down.sign * 0.6)
        lengthZ = int((min(self.width(), self.height()) // 4 * self.axes.back_front.sign) * 0.6)

        # 左右
        endX = QPoint(center.x() + lengthX, center.y())
        painter.setPen(QPen(self.axes.right_left.color, 2))
        painter.drawLine(center, endX)
        painter.drawText(endX + self.axes.right_left.sign * QPoint(8, 0) + QPoint(-5, 4), self.axes.right_left.axis)  # X轴标签的位置

        # 上下
        endY = QPoint(center.x(), center.y() - lengthY)
        painter.setPen(QPen(self.axes.up_down.color, 2))
        painter.drawLine(center, endY)
        painter.drawText(endY + self.axes.up_down.sign * QPoint(0, -10) + QPoint(-4, 4), self.axes.up_down.axis)  # Y轴标签的位置

        # 前后
        endZ = QPoint(center.x() - lengthZ, center.y() + lengthZ)
        painter.setPen(QPen(self.axes.back_front.color, 2))
        painter.drawLine(center, endZ)
        painter.drawText(endZ + self.axes.back_front.sign * QPoint(-8, 8) + QPoint(-5, 5), self.axes.back_front.axis)  # Z轴标签的位置

    def set_direction(self, axes: Axis):
        self.axes = axes
        self.update()


class LatexWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = QWebEngineView()
        self.browser.settings().setAttribute(QWebEngineSettings.ShowScrollBars, True)
        self.paragraph = []

        # 设置初始布局
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.browser)

    def clear(self):
        self.paragraph.clear()

    def add_latex_line(self, latex_line_str):
        self.paragraph.append(f'<p>{latex_line_str}</p>')

    def show_latex(self):
        wrap = '\n'
        content = r'''<html>
        <head>
        <title>MathJax TeX Test Page</title>
        <style>
          html, body {
            height: 100%;
            margin: 0;
            padding: 0;
            overflow-x: scroll;
            overflow-y: scroll;
            background: #ffffff;
          }
          body {
            box-sizing: border-box;
            padding: 10px 14px 14px 14px;
          }
          p {
            margin: 0 0 10px 0;
            white-space: nowrap;
          }
        </style>
        <script type="text/javascript" async
          src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
        </script>
        <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
          TeX: { 
            extensions: ["color.js"] 
          }
        });
        </script>
        </head>''' + fr'''
        <body>
        {wrap.join(self.paragraph)}
        </body>
        </html>'''

        self.browser.setHtml(content)

    def show_mathjax(self, mathjax: str):
        self.browser.setHtml(mathjax)


class DirectionWidget(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setMinimumSize(1040, 820)
        self.resize(1120, 860)

        # 创建 CoordinateWidget 实例作为 wFrameSrc 的子控件
        self.coordinateWidget = {
            'source': CoordinateWidget(self.wFrameSrc),
            'target': CoordinateWidget(self.wFrameTar)
        }
        self.wFrame = {
            'source': self.wFrameSrc,
            'target': self.wFrameTar
        }
        self.gb = {
            'source': self.gbSrc,
            'target': self.gbTar
        }
        self.labelHandness = {
            'source': self.lSrcHandness,
            'target': self.lTarHandness
        }
        for k, v in self.coordinateWidget.items():
            v.setGeometry(0, 0, self.wFrame[k].width(), self.wFrame[k].height())
        handness_font = QFont(self.font())
        handness_font.setPointSize(max(10, handness_font.pointSize() - 1))
        for lb in self.labelHandness.values():
            lb.setFont(handness_font)
            lb.setAlignment(Qt.AlignCenter)

        self.formulaWidget = LatexWidget(self.wFormula)
        self.formulaWidget.setGeometry(0, 0, self.wFormula.width(), self.wFormula.height())

        self.formulaWidget.add_latex_line(r'When \(a \ne 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are')
        self.formulaWidget.add_latex_line(r'\[x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}.\]')
        self.formulaWidget.show_latex()
        self.teLog.setLineWrapMode(QTextEdit.NoWrap)
        self.teLog.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.teLog.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # 连接按钮的信号
        self.pbSrcOpenCV.clicked.connect(lambda: self._update_direction_ui('source', {'X': '右', 'Y': '下', 'Z': '前'}, 'opencv'))
        self.pbSrcOpenGL.clicked.connect(lambda: self._update_direction_ui('source', {'X': '右', 'Y': '上', 'Z': '后'}, 'opengl'))
        self.pbSrcIMU.clicked.connect(lambda: self._update_direction_ui('source', {'X': '右', 'Y': '上', 'Z': '后'}, 'imu'))
        self.pbSrcUnity.clicked.connect(lambda: self._update_direction_ui('source', {'X': '右', 'Y': '上', 'Z': '前'}, 'unity'))

        self.pbTarOpenCV.clicked.connect(lambda: self._update_direction_ui('target', {'X': '右', 'Y': '下', 'Z': '前'}, 'opencv'))
        self.pbTarOpenGL.clicked.connect(lambda: self._update_direction_ui('target', {'X': '右', 'Y': '上', 'Z': '后'}, 'opengl'))
        self.pbTarIMU.clicked.connect(lambda: self._update_direction_ui('target', {'X': '右', 'Y': '上', 'Z': '后'}, 'imu'))
        self.pbTarUnity.clicked.connect(lambda: self._update_direction_ui('target', {'X': '右', 'Y': '上', 'Z': '前'}, 'unity'))

        self.pbTransform.clicked.connect(self._transform)

        self.cbX = {
            'source': self.cbSrcX, 'target': self.cbTarX
        }
        self.cbY = {
            'source': self.cbSrcY, 'target': self.cbTarY
        }
        self.cbZ = {
            'source': self.cbSrcZ, 'target': self.cbTarZ
        }

        self.cbX['source'].addItems(list('上下左右前后'))
        self.cbY['source'].addItems(list('左右前后'))
        self.cbZ['source'].addItems(list('前后'))
        self.cbX['source'].currentTextChanged.connect(lambda: self._update_combo_boxes('source', 'x'))
        self.cbY['source'].currentTextChanged.connect(lambda: self._update_combo_boxes('source', 'y'))
        self.cbZ['source'].currentTextChanged.connect(lambda: self._update_combo_boxes('source', 'z'))
        self.cbX['source'].setCurrentText('右')
        self.cbY['source'].setCurrentText('上')
        self.cbZ['source'].setCurrentText('后')

        self.cbX['target'].addItems(list('上下左右前后'))
        self.cbY['target'].addItems(list('左右前后'))
        self.cbZ['target'].addItems(list('前后'))
        self.cbX['target'].currentTextChanged.connect(lambda: self._update_combo_boxes('target', 'x'))
        self.cbY['target'].currentTextChanged.connect(lambda: self._update_combo_boxes('target', 'y'))
        self.cbZ['target'].currentTextChanged.connect(lambda: self._update_combo_boxes('target', 'z'))
        self.cbX['target'].setCurrentText('右')
        self.cbY['target'].setCurrentText('上')
        self.cbZ['target'].setCurrentText('后')

        self.rdbXYZW = {
            'source': self.rdbSrcXYZW,
            'target': self.rdbTarXYZW
        }
        self.rdbWXYZ = {
            'source': self.rdbSrcWXYZ,
            'target': self.rdbTarWXYZ
        }
        self.axisSelectorPanel = {
            'source': self.widget,
            'target': self.layoutWidget_4
        }
        self.orderSelectorPanel = {
            'source': self.layoutWidget1,
            'target': self.layoutWidget_3
        }
        self.presetButtonPanel = {
            'source': self.layoutWidget,
            'target': self.layoutWidget_2
        }
        self.axisComboBoxes = [
            self.cbSrcX, self.cbSrcY, self.cbSrcZ,
            self.cbTarX, self.cbTarY, self.cbTarZ
        ]
        for cb in self.axisComboBoxes:
            cb.setMaxVisibleItems(8)
            cb.setMinimumWidth(72)
            cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            popup_view = QListView()
            popup_view.setUniformItemSizes(True)
            cb.setView(popup_view)
            cb.view().setMinimumWidth(94)
            cb.view().setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.wear_label_to_key = {label: key for key, label, _ in WEAR_MODE_CHOICES}
        self.wear_short_name = {key: short_name for key, _, short_name in WEAR_MODE_CHOICES}
        self._setup_tab_ui()
        self._setup_wear_ui()
        self._refresh_dynamic_geometry()
        self._apply_ui_theme()
        self.setWindowTitle('Coordinate Transformation Helper')

    def _setup_tab_ui(self):
        self.tabControls = QTabWidget(self.centralwidget)
        self.tabControls.setGeometry(QRect(20, 10, 760, 280))
        self.tabControls.setDocumentMode(True)
        self.tabControls.setUsesScrollButtons(False)
        self.tabFrame = QWidget()
        self.tabFrame.setObjectName('tabFramePage')
        self.tabWear = QWidget()
        self.tabWear.setObjectName('tabWearPage')
        self.tabControls.addTab(self.tabFrame, '坐标系变换')
        self.tabControls.addTab(self.tabWear, '佩戴模式')

        self.gbSrc.setParent(self.tabFrame)
        self.gbTar.setParent(self.tabFrame)
        self.gbSrc.setGeometry(QRect(20, 8, 331, 261))
        self.gbTar.setGeometry(QRect(410, 8, 331, 261))

        self.teLog.setGeometry(QRect(30, 300, 341, 231))
        self.wFormula.setGeometry(QRect(400, 320, 341, 211))
        self.pbTransform.setGeometry(QRect(630, 540, 113, 32))

    def _setup_wear_ui(self):
        self.gbWear = QGroupBox('手表佩戴模式映射', self.tabWear)
        self.gbWear.setGeometry(QRect(40, 20, 680, 100))
        self.lbWearSource = QLabel('源模式', self.gbWear)
        self.lbWearSource.setGeometry(QRect(30, 44, 52, 20))
        self.cbWearSource = QComboBox(self.gbWear)
        self.cbWearSource.setGeometry(QRect(90, 42, 240, 24))
        self.lbWearTarget = QLabel('目标模式', self.gbWear)
        self.lbWearTarget.setGeometry(QRect(360, 44, 52, 20))
        self.cbWearTarget = QComboBox(self.gbWear)
        self.cbWearTarget.setGeometry(QRect(420, 42, 240, 24))

        for _, label, _ in WEAR_MODE_CHOICES:
            self.cbWearSource.addItem(label)
            self.cbWearTarget.addItem(label)
        self.cbWearSource.setCurrentIndex(0)
        self.cbWearTarget.setCurrentIndex(0)

        self.lbWearHint = QLabel(
            '说明: 本页只负责左右手/左右表冠映射；最终结果在下方公式区与坐标系变换自动合成。',
            self.tabWear
        )
        self.lbWearHint.setGeometry(QRect(40, 136, 680, 24))
        self.lbWearHint.setWordWrap(True)

    def _refresh_dynamic_geometry(self):
        margin = 20
        gap = 20
        top_margin = 10
        width = self.centralwidget.width()
        height = self.centralwidget.height()
        button_height = 34
        button_gap = 10
        bottom_margin = 16
        content_min_height = 190
        top_to_bottom_gap = 14
        top_height_soft = int(height * 0.50)
        top_height_hard_max = height - top_margin - top_to_bottom_gap - content_min_height - button_height - button_gap - bottom_margin
        top_height = min(max(320, top_height_soft), top_height_hard_max)
        top_height = max(280, top_height)

        self.tabControls.setGeometry(margin, top_margin, width - 2 * margin, top_height)
        page_width = self.tabControls.width()
        group_gap = 24
        group_width = max(331, (page_width - group_gap * 3) // 2)
        group_height = top_height - 22
        self.gbSrc.setGeometry(group_gap, 8, group_width, group_height)
        self.gbTar.setGeometry(group_gap * 2 + group_width, 8, group_width, group_height)
        self._refresh_group_content_geometry('source')
        self._refresh_group_content_geometry('target')

        bottom_y = top_margin + top_height + top_to_bottom_gap
        content_height = height - bottom_y - button_height - button_gap - bottom_margin
        content_height = max(content_min_height, content_height)
        left_width = (width - 2 * margin - gap) // 2
        self.teLog.setGeometry(margin, bottom_y, left_width, content_height)
        self.wFormula.setGeometry(margin + left_width + gap, bottom_y, width - 2 * margin - left_width - gap, content_height)
        button_y = bottom_y + content_height + button_gap
        self.pbTransform.setGeometry(width - margin - 150, button_y, 150, button_height)

        if hasattr(self, 'gbWear'):
            wear_margin = 30
            self.gbWear.setGeometry(wear_margin, 20, page_width - 2 * wear_margin, 118)
            wear_width = self.gbWear.width()
            label_width = 56
            spacing = 20
            combo_width = (wear_width - label_width * 2 - spacing * 5) // 2
            source_label_x = spacing
            self.lbWearSource.setGeometry(source_label_x, 48, label_width, 24)
            self.cbWearSource.setGeometry(source_label_x + label_width + 8, 46, combo_width, 28)
            target_label_x = source_label_x + label_width + 8 + combo_width + spacing
            self.lbWearTarget.setGeometry(target_label_x, 48, label_width, 24)
            self.cbWearTarget.setGeometry(target_label_x + label_width + 8, 46, combo_width, 28)
            self.lbWearHint.setGeometry(wear_margin, 152, page_width - 2 * wear_margin, 40)

    def _refresh_group_content_geometry(self, which: str):
        group = self.gb[which]
        axis_panel = self.axisSelectorPanel[which]
        order_panel = self.orderSelectorPanel[which]
        preset_panel = self.presetButtonPanel[which]
        hand_label = self.labelHandness[which]
        frame = self.wFrame[which]

        group_width = group.width()
        group_height = group.height()
        left_x = 14
        left_width = max(130, min(162, int(group_width * 0.38)))
        axis_height = 90
        order_height = 56
        axis_y = 30
        order_y = axis_y + axis_height + 8
        label_width = 104
        label_height = 30
        label_bottom_gap = 16
        hand_label_y = group_height - label_height - label_bottom_gap
        preset_height = 34
        preset_gap_to_label = 12
        preset_y = hand_label_y - preset_height - preset_gap_to_label
        min_preset_y = order_y + order_height + 8
        if preset_y < min_preset_y:
            preset_y = min_preset_y

        axis_panel.setGeometry(left_x, axis_y, left_width, axis_height)
        order_panel.setGeometry(left_x, order_y, left_width, order_height)
        preset_panel.setGeometry(10, preset_y, group_width - 20, preset_height)

        hand_label.setGeometry((group_width - label_width) // 2, hand_label_y, label_width, label_height)

        frame_size = min(150, max(122, preset_y - 42))
        frame_x = group_width - frame_size - 22
        frame_y = max(30, (preset_y - frame_size) // 2)
        frame.setGeometry(frame_x, frame_y, frame_size, frame_size)
        self.coordinateWidget[which].setGeometry(0, 0, frame.width(), frame.height())

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if hasattr(self, 'tabControls'):
            self._refresh_dynamic_geometry()

    def _apply_ui_theme(self):
        self.setStyleSheet("""
        QMainWindow {
            background: #edf2f8;
        }
        QWidget {
            font-family: "PingFang SC", "Helvetica Neue", "Arial";
            color: #223042;
        }
        QTabWidget::pane {
            border: 1px solid #cfd8e6;
            border-radius: 10px;
            background: #f7f9fc;
            top: -1px;
        }
        QTabBar::tab {
            background: #dbe3ef;
            color: #3c495b;
            border: 1px solid #c7d2e3;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 6px 16px;
            margin-right: 4px;
            min-width: 88px;
            font-weight: 600;
        }
        QTabBar::tab:selected {
            background: #2f6fed;
            color: #ffffff;
            border-color: #2f6fed;
        }
        QTabBar::tab:hover:!selected {
            background: #cfd9ea;
            color: #1f2d3d;
        }
        QGroupBox {
            border: 1px solid #cfd8e6;
            border-radius: 10px;
            margin-top: 12px;
            background: #ffffff;
            font-weight: 600;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 6px;
            color: #2d3b4e;
        }
        QLabel {
            color: #2d3b4e;
        }
        QLabel#lSrcHandness, QLabel#lTarHandness {
            font-size: 14px;
            font-weight: 600;
            color: #1f2d3d;
            padding-bottom: 2px;
        }
        QComboBox {
            border: 1px solid #c6d1e0;
            border-radius: 6px;
            padding: 4px 8px;
            background: #ffffff;
            min-height: 20px;
        }
        QComboBox:focus {
            border: 1px solid #2f6fed;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #c6d1e0;
            background: #ffffff;
            selection-background-color: #2f6fed;
            selection-color: #ffffff;
            outline: 0px;
            padding: 4px 0px;
        }
        QComboBox QAbstractItemView::item {
            min-height: 22px;
            padding-left: 8px;
        }
        QRadioButton {
            spacing: 6px;
        }
        QRadioButton::indicator {
            width: 14px;
            height: 14px;
        }
        QPushButton {
            border: 1px solid #b9c7dc;
            border-radius: 8px;
            background: #f7f9fc;
            color: #223042;
            padding: 4px 10px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #eef3fb;
            border-color: #9db2d4;
        }
        QPushButton:pressed {
            background: #dfe8f7;
        }
        QPushButton#pbTransform {
            background: #2f6fed;
            color: #ffffff;
            border: 1px solid #2558be;
            min-height: 26px;
            min-width: 120px;
        }
        QPushButton#pbTransform:hover {
            background: #245dd0;
        }
        QTextEdit {
            border: 1px solid #cfd8e6;
            border-radius: 10px;
            background: #ffffff;
            padding: 8px;
            selection-background-color: #bfd3fb;
        }
        QScrollBar:horizontal {
            height: 12px;
            background: #e7edf7;
            margin: 2px 14px 2px 14px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background: #95a8c8;
            min-width: 30px;
            border-radius: 6px;
        }
        QScrollBar:vertical {
            width: 12px;
            background: #e7edf7;
            margin: 14px 2px 14px 2px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #95a8c8;
            min-height: 30px;
            border-radius: 6px;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            width: 0px;
            height: 0px;
        }
        QWidget#wFormula {
            border: 1px solid #cfd8e6;
            border-radius: 10px;
            background: #ffffff;
        }
        QStatusBar {
            background: #edf2f8;
        }
        """)

    @staticmethod
    def _matrix_to_latex(matrix: np.ndarray) -> str:
        rows = [r'&'.join(str(int(v)) for v in row) for row in matrix]
        return r'\begin{pmatrix}' + r'\\'.join(rows) + r'\end{pmatrix}'

    @staticmethod
    def _wear_mode_to_baseline_matrix(mode_key: str) -> np.ndarray:
        mirror_yz = np.diag([-1, 1, 1]).astype(int)
        crown_flip = np.diag([-1, -1, 1]).astype(int)
        transform = np.eye(3, dtype=int)
        if mode_key in ('right_crown_right', 'right_crown_left'):
            transform = mirror_yz @ transform
        if mode_key in ('left_crown_left', 'right_crown_left'):
            transform = crown_flip @ transform
        return transform.astype(int)

    def _get_wear_transform(self) -> Tuple[np.ndarray, str, str, bool]:
        src_key = self.wear_label_to_key[self.cbWearSource.currentText()]
        tar_key = self.wear_label_to_key[self.cbWearTarget.currentText()]
        src_to_base = self._wear_mode_to_baseline_matrix(src_key)
        tar_to_base = self._wear_mode_to_baseline_matrix(tar_key)
        wear_transform = (tar_to_base.T @ src_to_base).astype(int)
        src_is_right = src_key in ('right_crown_right', 'right_crown_left')
        tar_is_right = tar_key in ('right_crown_right', 'right_crown_left')
        gesture_swap = src_is_right != tar_is_right
        return wear_transform, self.wear_short_name[src_key], self.wear_short_name[tar_key], gesture_swap

    def _get_frame_transform(self) -> Tuple[np.ndarray, Dict[str, Dict[str, Union[str, int]]]]:
        src_axes = self.coordinateWidget['source'].axes
        tar_axes = self.coordinateWidget['target'].axes
        coord_tar = {
            tar_axes.right_left.axis: ('rl', tar_axes.right_left.sign),
            tar_axes.up_down.axis: ('ud', tar_axes.up_down.sign),
            tar_axes.back_front.axis: ('bf', tar_axes.back_front.sign),
        }
        map_dict = dict()
        for axis, (direction, sign) in coord_tar.items():
            if direction == 'rl':
                map_dict[axis] = {
                    'axis': src_axes.right_left.axis,
                    'sign': sign * src_axes.right_left.sign
                }
            elif direction == 'ud':
                map_dict[axis] = {
                    'axis': src_axes.up_down.axis,
                    'sign': sign * src_axes.up_down.sign
                }
            elif direction == 'bf':
                map_dict[axis] = {
                    'axis': src_axes.back_front.axis,
                    'sign': sign * src_axes.back_front.sign
                }
        axis_to_vec = {
            'X': [1, 0, 0],
            'Y': [0, 1, 0],
            'Z': [0, 0, 1]
        }
        row_1 = np.array(axis_to_vec[map_dict['X']['axis']]) * map_dict['X']['sign']
        row_2 = np.array(axis_to_vec[map_dict['Y']['axis']]) * map_dict['Y']['sign']
        row_3 = np.array(axis_to_vec[map_dict['Z']['axis']]) * map_dict['Z']['sign']
        return np.r_[row_1, row_2, row_3].reshape((3, 3)).astype(int), map_dict

    def _transform(self):
        R_frame, map_dict = self._get_frame_transform()
        R_wear, wear_src, wear_tar, gesture_swap = self._get_wear_transform()
        R_vector = (R_frame @ R_wear).astype(int)
        R_pseudo = (int(round(np.linalg.det(R_vector))) * R_vector).astype(int)

        q_mat = np.eye(4, dtype=int)
        q_mat[1:, 1:] = R_pseudo
        quaternion_str_new = matrix_times_quaternion_str(q_mat, r'q_w,q_x,q_y,q_z')
        self._show_log(f'{map_dict=}')
        self._show_log(f'wear(source->target): {wear_src} -> {wear_tar}', 'debug')
        self._show_log(f'R_frame=\n{R_frame}', 'info')
        self._show_log(f'R_wear(vector)=\n{R_wear}', 'info')
        self._show_log(f'R_total(vector/acc)=\n{R_vector}', 'info')
        self._show_log(f'R_total(pseudo/gyro)=\n{R_pseudo}', 'info')
        if gesture_swap:
            self._show_log('gesture label swap: left-swing <-> right-swing', 'warning')
        self._show_log(f'quaternion_transformation=\n{q_mat}', 'info')
        self._show_formula(
            R_frame,
            R_wear,
            R_vector,
            R_pseudo,
            q_mat,
            'q_w,q_x,q_y,q_z',
            quaternion_str_new,
            wear_src,
            wear_tar,
            gesture_swap
        )

    def _show_formula(self,
                      R_frame: np.ndarray,
                      R_wear: np.ndarray,
                      R_vector: np.ndarray,
                      R_pseudo: np.ndarray,
                      q_mat: np.ndarray,
                      quaternion_str_src: str,
                      quaternion_str_tar: str,
                      wear_src: str,
                      wear_tar: str,
                      gesture_swap: bool):
        self.formulaWidget.clear()
        frame_latex = self._matrix_to_latex(R_frame)
        wear_latex = self._matrix_to_latex(R_wear)
        vector_latex = self._matrix_to_latex(R_vector)
        pseudo_latex = self._matrix_to_latex(R_pseudo)
        self.formulaWidget.add_latex_line(
            r'Wear mode: \(\textcolor{green}{' + wear_src + r'} \rightarrow \textcolor{green}{' + wear_tar + r'}\), '
            r'gesture swap: \(\textcolor{red}{' + ('Yes' if gesture_swap else 'No') + r'}\).'
        )
        self.formulaWidget.add_latex_line(
            r'\[\textcolor{blue}{\mathbf{R}_{frame}}=' + frame_latex +
            r',\ \textcolor{green}{\mathbf{R}_{wear}^{vec}}=' + wear_latex + r'\]'
        )
        self.formulaWidget.add_latex_line(
            r'\[\mathbf{R}_{total}^{vec}='
            r'\textcolor{blue}{\mathbf{R}_{frame}}\cdot'
            r'\textcolor{green}{\mathbf{R}_{wear}^{vec}}=' +
            vector_latex + r'\]'
        )
        self.formulaWidget.add_latex_line(
            r'\[\mathbf{R}_{total}^{pseudo}=\det(\mathbf{R}_{total}^{vec})\mathbf{R}_{total}^{vec}=' +
            pseudo_latex + r'\]'
        )
        self.formulaWidget.add_latex_line(
            r'\[\begin{pmatrix}a_x^\prime\\a_y^\prime\\a_z^\prime\end{pmatrix}=' +
            vector_latex +
            r'\begin{pmatrix}a_x\\a_y\\a_z\end{pmatrix}\]'
        )
        self.formulaWidget.add_latex_line(
            r'\[\begin{pmatrix}g_x^\prime\\g_y^\prime\\g_z^\prime\end{pmatrix}=' +
            pseudo_latex +
            r'\begin{pmatrix}g_x\\g_y\\g_z\end{pmatrix}\]'
        )
        self.formulaWidget.add_latex_line(r'\[' +
                                          r'\begin{pmatrix}' +
                                          r'q_w^\prime\\q_x^\prime\\q_y^\prime\\q_z^\prime' +
                                          r'\end{pmatrix}=' +
                                          r'\begin{pmatrix}' +
                                          '&'.join(map(str, q_mat[0])) + r'\\' +
                                          '&'.join(map(str, q_mat[1])) + r'\\' +
                                          '&'.join(map(str, q_mat[2])) + r'\\' +
                                          '&'.join(map(str, q_mat[3])) +
                                          r'\end{pmatrix}' +
                                          r'\begin{pmatrix}' +
                                          r'q_w\\q_x\\q_y\\q_z' +
                                          r'\end{pmatrix}' +
                                          r'\]')
        self.formulaWidget.add_latex_line(r'A rotation represented as \((' + quaternion_str_src + r')\) in the source coordinate system is expressed as \(\textcolor{blue}{(' + quaternion_str_tar + r')}\) in the target coordinate system.')
        self.formulaWidget.add_latex_line(r'from \(\textcolor{red}{(' + (r'q_w,q_x,q_y,q_z' if self.rdbSrcWXYZ.isChecked() else r'q_x,q_y,q_z,q_w') + r')}\)')
        self.formulaWidget.add_latex_line(r'to \(\textcolor{green}{(' + (quaternion_str_tar if self.rdbTarWXYZ.isChecked() else ','.join([quaternion_str_tar.split(',')[i] for i in [1, 2, 3, 0]])) + r')}\)')
        self.formulaWidget.show_latex()

    def _update_combo_boxes(self, which: str, axis: str):
        all_groups = {0, 1, 2}
        candidates = ['上下', '左右', '前后']
        group_map = {vv: k for k, v in enumerate(candidates) for vv in v}  # { '上': 0, '下': 0, '左': 1, ... }
        x_prev = self.cbX[which].currentText()
        y_prev = self.cbY[which].currentText()
        z_prev = self.cbZ[which].currentText()
        x_prev_group = group_map[x_prev]
        y_prev_group = group_map[y_prev]
        z_prev_group = group_map[z_prev]
        if axis == 'x':
            y_group = all_groups - {x_prev_group}
            self.cbY[which].blockSignals(True)
            self.cbY[which].clear()
            self.cbY[which].addItems([opt for y in y_group for opt in candidates[y]])
            self.cbY[which].blockSignals(False)
            y_cur_group = group_map[self.cbY[which].currentText()]
            z_group = all_groups - {x_prev_group} - {y_cur_group}
            self.cbZ[which].blockSignals(True)
            self.cbZ[which].clear()
            self.cbZ[which].addItems([opt for z in z_group for opt in candidates[z]])
            self.cbZ[which].blockSignals(False)
        elif axis == 'y':
            z_group = all_groups - {x_prev_group} - {y_prev_group}
            self.cbZ[which].blockSignals(True)
            self.cbZ[which].clear()
            self.cbZ[which].addItems([opt for z in z_group for opt in candidates[z]])
            self.cbZ[which].blockSignals(False)
        elif axis == 'z':
            pass
        else:
            self._show_log(f'{axis}轴不支持', level='error')
            return

        axis_direction = {
            'X': self.cbX[which].currentText(),
            'Y': self.cbY[which].currentText(),
            'Z': self.cbZ[which].currentText(),
        }
        rl, ud, bf = dict(), dict(), dict()
        for k, v in axis_direction.items():
            # 'X': '左', 'Y': '上', 'Z': '后'
            if v in '左右':
                rl['axis'] = k
                rl['sign'] = 1 if v == '右' else -1
                rl['color'] = QT_COLOR[k]
            elif v in '上下':
                ud['axis'] = k
                ud['sign'] = 1 if v == '上' else -1
                ud['color'] = QT_COLOR[k]
            elif v in '前后':
                bf['axis'] = k
                bf['sign'] = 1 if v == '后' else -1
                bf['color'] = QT_COLOR[k]
            else:
                self._show_log(f'不支持当前方向: {k=}, {v=}', level='error')
                return
        self.coordinateWidget[which].set_direction(Axis(
            right_left=Direction(rl['axis'], rl['sign'], rl['color']),
            up_down=Direction(ud['axis'], ud['sign'], ud['color']),
            back_front=Direction(bf['axis'], bf['sign'], bf['color'])
        ))
        self._show_current_direction(which)

    def _update_direction_ui(self, which: str, axis_direction: Dict[str, str], frame=''):
        if frame:
            self._show_log(f'{which}坐标系当前选择了: ' + frame, level='debug')
            if frame == 'unity':
                self.rdbXYZW[which].setChecked(True)
            else:
                self.rdbWXYZ[which].setChecked(True)
        self.cbX[which].setCurrentText(axis_direction['X'])
        self.cbY[which].setCurrentText(axis_direction['Y'])
        self.cbZ[which].setCurrentText(axis_direction['Z'])

    def _show_current_direction(self, which):
        handness_str = self.coordinateWidget[which].handness_str
        self.labelHandness[which].setText(handness_str)
        self._show_log(f'{which}为{handness_str}坐标系')
        # self._show_log(f'{which}为{handness_str}坐标系，x轴向{"左右"[(self.coordinateWidget[which].flipX + 1) // 2]}, y轴向{"下上"[(self.coordinateWidget[which].flipY + 1) // 2]}, z轴向{"前后"[(self.coordinateWidget[which].flipZ + 1) // 2]}')

    def _show_log(self, log_str: str, level='debug'):
        log_str = str(log_str)
        h_scrollbar = self.teLog.horizontalScrollBar()
        v_scrollbar = self.teLog.verticalScrollBar()
        h_value = h_scrollbar.value()
        was_at_bottom = v_scrollbar.value() >= (v_scrollbar.maximum() - 2)
        if level == 'info':
            self.teLog.setTextColor(QColor(30, 144, 255))
        elif level == 'warning':
            self.teLog.setTextColor(QColor(255, 165, 0))
        elif level == 'debug':
            self.teLog.setTextColor(QColor(34, 139, 34))
        elif level == 'error':
            self.teLog.setTextColor(QColor(220, 20, 60))
        else:
            self.teLog.setTextColor(Qt.black)
        self.teLog.append(f">>> " + log_str)
        self.teLog.setTextColor(Qt.black)
        if was_at_bottom:
            v_scrollbar.setValue(v_scrollbar.maximum())
        h_scrollbar.setValue(min(h_value, h_scrollbar.maximum()))
        QApplication.processEvents()
        h_scrollbar.setValue(min(h_value, h_scrollbar.maximum()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
