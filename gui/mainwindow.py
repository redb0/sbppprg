from PyQt5 import QtCore
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QDockWidget)

from spp.ph import packaging
from spp.support import items_by_index, area

from .graph import CanvasCuttingChart


class UiMainWindow:
    def __init__(self):
        self.draw_btn = None
        self.h_box_cutting_chart = None

        self.sheet_area = None
        self.min_area = None
        self.filled_area = None
        self.ratio = None
        self.count = None
        self.free_strip = None
    
    def setup_ui(self, main_window):
        central_wdg = QWidget()
        main_window.setCentralWidget(central_wdg)
        main_window.setObjectName("MainWindow")
        main_window.resize(450, 550)

        main_v_box = QVBoxLayout()
        
        # кнопка
        self.draw_btn = QPushButton()
        h_box_button = QHBoxLayout()
        h_box_button.addWidget(self.draw_btn)
        h_box_button.addStretch(1)
        main_v_box.addLayout(h_box_button)

        # текстовы поля
        self.sheet_area = QLabel()
        self.min_area = QLabel()
        self.filled_area = QLabel()
        self.ratio = QLabel()
        self.count = QLabel()
        self.free_strip = QLabel()

        v_box_label = QVBoxLayout()
        v_box_label.addWidget(self.count)
        v_box_label.addWidget(self.sheet_area)
        v_box_label.addWidget(self.min_area)
        v_box_label.addWidget(self.filled_area)
        v_box_label.addWidget(self.ratio)
        v_box_label.addWidget(self.free_strip)
        v_box_label.addStretch(1)

        main_v_box.addLayout(v_box_label)
        central_wdg.setLayout(main_v_box)

        self.retranslate_ui(main_window)
    
    def retranslate_ui(self, main_window):
        main_window.setWindowTitle(self.translate("MainWindow", "Карта раскроя"))
        self.draw_btn.setText(self.translate("MainWindow", "Построить график"))
    
    def translate(self, text, text_1):
        return QtCore.QCoreApplication.translate(text, text_1)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiMainWindow()
        self.ui.setup_ui(self)

        self.cutting_charts = []

        self.ui.draw_btn.clicked.connect(self.draw)

        self.dockers = []
        
    
    def draw(self):
        self.cutting_charts = []
        if self.dockers:
            for dock in self.dockers:
                # dock[0].show()
                dock[0].setParent(None)
        self.dockers = []

        length_marking, groups = self.example(25, 55)

        for h, group in groups.items():
            graph = CanvasCuttingChart(width=25, height=length_marking[h])
            self.cutting_charts.append(graph)
            self.create_dock_with_graph(graph, 25, length_marking[h], h, group,
                                        xlabel='$x$', ylabel='$y$', 
                                        title=f'Карта раскроя ({h:.1f} мм)')
            

    def example(self, width, length):
        rect = {
            3.0: {  # ширина w, длина l
                1: [(5, 3), (5, 3), (5, 5), (10, 10), (20, 14)],
                2: [(30, 8), (20, 10), (1, 10), (6, 6)],
                3: [(2, 4), (5, 5), (10, 5), (8, 4)],
                4: [(10, 20), (6, 4)],
            },
            2.0: {
                1: [(6, 3), (5, 3), (1, 5), (10, 10), (20, 14)],
                2: [(5, 8), (15, 10), (3, 10), (6, 7), (4, 2)], 
                3: [(2, 4), (5, 7), (9, 5), (6, 4)],
                4: [],
            },
            1.0: {
                1: [(7, 7), (4, 5), (3, 3)],
                2: [(10, 8), (9, 3), (5, 4), (6, 7), (5, 3)], 
                3: [(10, 10), (12, 6), (8, 7)],
            },
        }

        count = 0
        for h, group in rect.items():
            for p, list_r in group.items():
                count += len(list_r)

        res, unplaced_idx, len_m, unused_l = packaging(width, length, rect, 
                                                       rounding_func=lambda x: round(x, 1), 
                                                       sorting="width")
        
        unplaced = items_by_index(rect, unplaced_idx)

        s = area(res, as_nt=True)
        required_s = area(rect)

        count_res = 0
        for h, group in res.items():
            for p, list_r in group.items():
                count_res += len(list_r)

        self.ui.sheet_area.setText(f'Площадь листа: {width * length}')
        self.ui.min_area.setText(f'Минимально возможная площадь (по толщинам): {required_s}')
        self.ui.filled_area.setText(f'Заполненная площадь (по толщинам): {s}')

        ratio = {k: round(v / (len_m[k]*width), 2) for k, v in s.items()}
        self.ui.ratio.setText(f'Отношение покрытой площади к общей (по выделенной длине): {ratio}')
        self.ui.count.setText(f'Размещено {count_res} прямоугольников из {count}')
        self.ui.free_strip.setText(f'Осталась полоса длиной {unused_l:.2f}')

        return len_m, res


    def create_dock_with_graph(self, graph_obj, width, length, h, group,
                               xlabel='$x$', ylabel='$y$', title="", label_on_rect=False):
        
        docker, v_box = self.add_docker(title, f'{h:.1f} мм')

        graph_obj.setMinimumSize(200, 300)
        # graph_obj.resize(400, 500)
        v_box.addWidget(graph_obj)
        
        toolbar = graph_obj.get_toolbar()
        # toolbar.resize(400, 500)
        v_box.addWidget(toolbar)
        # layout.addLayout(v_box)
        graph_obj.create_graph(width, length, h, group, label_on_rect=label_on_rect)
        graph_obj.set_labels(xlabel=xlabel, ylabel=ylabel, title=title)


    def add_docker(self, title, tab_title):
        docker = QDockWidget()
        docker.setWindowTitle(title)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, docker)
        docker.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea)

        central_wdg_docker = QWidget()
        docker.setWidget(central_wdg_docker)

        v_box = QVBoxLayout()
        central_wdg_docker.setLayout(v_box)
        if self.dockers:
            self.tabifyDockWidget(self.dockers[-1][0], docker)
        self.dockers.append((docker, v_box))
        return docker, v_box


    def deleteItem(self, widget):
        widget.setParent(None)


    # def deleteItemsOfLayout(self, layout):
    #     if layout is not None:
    #         while layout.count():
    #             item = layout.takeAt(0)
    #             widget = item.widget()
    #             if widget is not None:
    #                 widget.setParent(None)
    #             else:
    #                 self.deleteItemsOfLayout(item.layout())
