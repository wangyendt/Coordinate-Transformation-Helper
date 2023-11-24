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
from PyQt5.QtWebEngineWidgets import QWebEngineView
from ui.coordinate_transformation_helper import Ui_MainWindow


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

        # 创建 CoordinateWidget 实例作为 wFrameSrc 的子控件
        self.coordinateWidget = {
            'source': CoordinateWidget(self.wFrameSrc),
            'target': CoordinateWidget(self.wFrameTar)
        }
        self.wFrame = {
            'source': self.wFrameSrc,
            'target': self.wFrameTar
        }
        self.labelHandness = {
            'source': self.lSrcHandness,
            'target': self.lTarHandness
        }
        for k, v in self.coordinateWidget.items():
            v.setGeometry(0, 0, self.wFrame[k].width(), self.wFrame[k].height())

        self.formulaWidget = LatexWidget(self.wFormula)
        self.formulaWidget.setGeometry(0, 0, self.wFormula.width(), self.wFormula.height())

        self.formulaWidget.add_latex_line(r'When \(a \ne 0\), there are two solutions to \(ax^2 + bx + c = 0\) and they are')
        self.formulaWidget.add_latex_line(r'\[x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}.\]')
        self.formulaWidget.show_latex()

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

    def _transform(self):
        src_axes = self.coordinateWidget['source'].axes
        tar_axes = self.coordinateWidget['target'].axes
        coord_tar = {
            tar_axes.right_left.axis: ('rl', tar_axes.right_left.sign),
            tar_axes.up_down.axis: ('ud', tar_axes.up_down.sign),
            tar_axes.back_front.axis: ('bf', tar_axes.back_front.sign),
        }
        map_dict = dict()
        for axis, (direction, sign) in coord_tar.items():
            # print(axis, direction, sign)
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
        self._show_log(f'{map_dict=}')
        axis_to_vec = {
            'X': [1, 0, 0],
            'Y': [0, 1, 0],
            'Z': [0, 0, 1]
        }
        R_row_1 = np.array(axis_to_vec[map_dict['X']['axis']]) * map_dict['X']['sign']
        R_row_2 = np.array(axis_to_vec[map_dict['Y']['axis']]) * map_dict['Y']['sign']
        R_row_3 = np.array(axis_to_vec[map_dict['Z']['axis']]) * map_dict['Z']['sign']
        R = np.r_[R_row_1, R_row_2, R_row_3].reshape((3, 3))
        q_mat = np.eye(4, dtype=int)
        q_mat[1:, 1:] = R
        if self.coordinateWidget['source'].handness != self.coordinateWidget['target'].handness:
            q_mat[1:, 1:] *= -1
        quaternion_str_new = matrix_times_quaternion_str(q_mat, r'q_w,q_x,q_y,q_z')
        self._show_log(f'R=\n{R}', 'info')
        self._show_log(f'quaternion_transformation=\n{q_mat}', 'info')
        self._show_formula(R, q_mat, 'q_w,q_x,q_y,q_z', quaternion_str_new)

    def _show_formula(self, R: np.ndarray, q_mat: np.ndarray, quaternion_str_src: str, quaternion_str_tar: str):
        self.formulaWidget.clear()
        self.formulaWidget.add_latex_line(r'\[\begin{pmatrix}x^\prime\\y^\prime\\z^\prime\end{pmatrix}=' +
                                          r'\begin{pmatrix}' +
                                          str(R[0, 0]) + '&' + str(R[0, 1]) + '&' + str(R[0, 2]) + r'\\' +
                                          str(R[1, 0]) + '&' + str(R[1, 1]) + '&' + str(R[1, 2]) + r'\\' +
                                          str(R[2, 0]) + '&' + str(R[2, 1]) + '&' + str(R[2, 2]) +
                                          r'\end{pmatrix}' +
                                          r'\begin{pmatrix}' +
                                          r'x\\y\\z' +
                                          r'\end{pmatrix}' +
                                          r'\]')
        self.formulaWidget.add_latex_line(r'\[\textbf{R}^\prime=' +
                                          r'\begin{pmatrix}' +
                                          str(R[0, 0]) + '&' + str(R[0, 1]) + '&' + str(R[0, 2]) + r'\\' +
                                          str(R[1, 0]) + '&' + str(R[1, 1]) + '&' + str(R[1, 2]) + r'\\' +
                                          str(R[2, 0]) + '&' + str(R[2, 1]) + '&' + str(R[2, 2]) +
                                          r'\end{pmatrix}' +
                                          r'\textbf{R}' +
                                          r'\begin{pmatrix}' +
                                          str(R[0, 0]) + '&' + str(R[0, 1]) + '&' + str(R[0, 2]) + r'\\' +
                                          str(R[1, 0]) + '&' + str(R[1, 1]) + '&' + str(R[1, 2]) + r'\\' +
                                          str(R[2, 0]) + '&' + str(R[2, 1]) + '&' + str(R[2, 2]) +
                                          r'\end{pmatrix}^T' +
                                          r'\]')
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
        self.teLog.moveCursor(QTextCursor.End)
        QApplication.processEvents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
