from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class MlpCanvas(FigureCanvas):
    def __init__(self, parent=None, fontsize=14, width=30, height=30): 
        self.fig = Figure(figsize=(width, height))  # , tight_layout=True
        
        super().__init__(self.fig)
        
        self.axis = self.fig.add_subplot(1, 1, 1)

        self.fig.subplots_adjust(0.15, 0.2)
        self.set_params(fontsize)
        self.setParent(parent)


    def get_toolbar(self):
        """Панель инструментов для графика"""
        toolbar = NavigationToolbar(self, self)
        return toolbar

    def create_graph(self, constraints_high, constraints_down, func):
        """Построение карты раскроя"""
        pass

    def set_labels(self, xlabel="", ylabel="", title=""):
        self.axis.set_xlabel(xlabel)
        self.axis.set_ylabel(ylabel, rotation=0)
        self.axis.title.set_text(title)

    def set_params(self, fontsize=14):
        params = {'legend.fontsize': fontsize,
                  'axes.labelsize': fontsize,
                  'axes.titlesize': fontsize,
                  'xtick.labelsize': fontsize - 2,
                  'ytick.labelsize': fontsize - 2}
        plt.rcParams.update(params)

    def close(self):
        """Метод закрытия графиков библиотеки mathplotlib"""
        plt.close()
