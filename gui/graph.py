from random import random

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from spp.visualize import create_grad, get_annotation
from .mpl_canvas import MlpCanvas


class CanvasCuttingChart(MlpCanvas):
    def create_graph(self, width, length, h, rectangles, label_on_rect=False):
        rectangles_with_annotation = []
        self.patch_rect((0, 0), width, length, hatch='x', fill=False)
        for p, list_r in rectangles.items():
            for r in list_r:
                obj = self.patch_rect((r.x, r.y), r.w, r.l, color=(random(), random(), random()), ec='k', lw=0.5)
                if label_on_rect:
                    self.axis.text(r.x + 0.5 * r.w, r.y + 0.5 * r.l, str(r.idx))
                description = (f'Деталь:\nТолщина: {h:.1f}\n'
                               f'Приоритет: {p:d}\n'
                               f'Размеры: {r.w:.2f}$\\times${r.l:.2f}\n'
                               f'Координаты: ({r.x:.2f}, {r.y:.2f})')
                annot = get_annotation(self.axis, description, (r.x, r.y), (0, 0))
                rectangles_with_annotation.append((obj, annot))
        self.axis.set_xlim(0, width)
        self.axis.set_ylim(0, length)
        self.axis.title.set_text(f'Толщина {h} мм')
        self.axis.set_xlabel(f'$x$')
        self.axis.set_ylabel(f'$y$')
        self.axis.set_aspect('equal', adjustable='box')
        on_move_id = self.fig.canvas.mpl_connect('button_press_event', self.on_move(rectangles_with_annotation))

    
    def patch_rect(self, xy, w, h, **kwargs):
        obj = self.axis.add_patch(
            patches.Rectangle(xy, w, h,**kwargs)
        )
        return obj

    
    def on_move(self, rectangles_with_annotation):
        def inner(event):
            if event.button == 1:
                for rectangle, annotation in rectangles_with_annotation:
                    if event.xdata is not None and event.ydata is not None:
                        x0, y0 = rectangle.get_xy()
                        h = rectangle.get_height()
                        w = rectangle.get_width()
                        if (x0 < event.xdata < x0 + w) and (y0 < event.ydata < y0 + h):
                            annotation.set_position((x0+w, y0))
                            annotation.xy = (x0, y0)
                            annotation.set_visible(True)
                        else:
                            annotation.set_visible(False)
            else:
                for rectangle, annotation in rectangles_with_annotation:
                    annotation.set_visible(False)
            self.fig.canvas.draw()
        return inner
