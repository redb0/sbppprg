import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from random import uniform, random


def patch_rect(axis, xy, w, h, **kwargs):
    obj = axis.add_patch(
        patches.Rectangle(xy, w, h, **kwargs)
    )
    return obj


def visualize_separately(width, length_marking, rectangles):
    n = len(rectangles.keys())
    fig, axes = plt.subplots(1, n)
    if n == 1:
        axes = [axes]
    rectangles_with_annotation = []
    for i, (h, group) in enumerate(rectangles.items()):
        patch_rect(axes[i], (0, 0), width, length_marking[h], hatch='x', fill=False)
        for p, list_r in group.items():
            for r in list_r:
                obj = patch_rect(axes[i], (r.x, r.y), r.w, r.l, color=(random(), random(), random()), ec='k', lw=0.5)
                axes[i].text(r.x + 0.5 * r.w, r.y + 0.5 * r.l, str(r.idx))
                description = (f'Деталь:\nТолщина: {h:.1f}\n'
                               f'Приоритет: {p:d}\n'
                               f'Размеры: {r.w:.2f}$\\times${r.l:.2f}\n'
                               f'Координаты: ({r.x:.2f}, {r.y:.2f})')
                annot = get_annotation(axes[i], description, (r.x, r.y), (0, 0))
                rectangles_with_annotation.append((obj, annot))
        axes[i].set_xlim(0, width)
        axes[i].set_ylim(0, length_marking[h])
        axes[i].title.set_text(f'Height {h} mm')
        axes[i].set_xlabel(f'$x$')
        axes[i].set_ylabel(f'$y$', rotation=0)
        axes[i].set_aspect('equal', adjustable='box')
    on_move_id = fig.canvas.mpl_connect('button_press_event', on_move)
    plt.show()


def get_annotation(ax, description, xy, pos):
    annotation = ax.annotate(description,
        xy=xy,
        xycoords='data',
        xytext=pos, textcoords='data',
        horizontalalignment="left",
        bbox=dict(boxstyle="round", facecolor="w", 
                edgecolor="0.5", alpha=0.9),
        va='top',
        ha = 'left'
    )
    annotation.set_visible(False)
    return annotation


def create_grad(max_x):
    a = [uniform(0, 1)]
    for i in range(max_x - 1):
        a.append(a[-1] + (1. - a[0]) / max_x)
    return a


def visualize_mgroup(width, length, length_marking, groups):
    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1)
    axes.add_patch(
        patches.Rectangle(
            (0, 0),
            width,
            sum(length_marking),
            hatch='x',
            fill=False,
        )
    )
    rectangles_with_annotation = []
    l = None
    for i, (height, group) in enumerate(groups.items()):
        if l is None:
            l = 0
        else:
            l += length_marking[i-1]
        c_0 = uniform(0, 1)
        c_1 = create_grad(max(group.keys()))
        for k, (p, rects) in enumerate(group.items()):
            c_2 = create_grad(len(rects))
            for j, r in enumerate(rects):
                obj = axes.add_patch(
                    patches.Rectangle(
                        (r.x, r.y+l),
                        r.w,
                        r.l,
                        color=(c_0, c_1[k], c_2[j]), 
                        ec='k', lw=0.5
                    )
                )
                # axes.text(r.x + 0.45 * r.w, r.y+l + 0.45 * r.l, str(r.idx))
                description = (f'Деталь:\nТолщина: {height:.1f}\n'
                               f'Приоритет: {p:d}\n'
                               f'Размеры: {r.w:.2f}$\\times${r.l:.2f}\n'
                               f'Координаты: ({r.x:.2f}, {r.y+l:.2f})')
                annot = get_annotation(axes, description, (r.x, r.y+l), (0, 0))
                rectangles_with_annotation.append((obj, annot))
        if i > 0:
            axes.axhline(l, 0, width, color='k', linewidth=2)
    
    on_move_id = fig.canvas.mpl_connect('button_press_event', on_move)
    
    axes.set_xlim(0, width)
    axes.set_ylim(0, sum(length_marking))
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


def on_move(rectangles_with_annotation):
    def inner(event):
        if event.button == 1:
            for rectangle, annotation in rectangles_with_annotation:
                if event.xdata is not None and event.ydata is not None:
                    x0, y0 = rectangle.get_xy()
                    h = rectangle.get_height()
                    w = rectangle.get_width()
                    if (x0 < event.xdata < x0 + w) and (y0 < event.ydata < y0 + h):
                        # annotation.set_position((event.xdata, event.ydata))
                        annotation.set_position((x0+w, y0))
                        # annotation.xy = (event.xdata, event.ydata)
                        annotation.xy = (x0, y0)
                        annotation.set_visible(True)
                    else:
                        annotation.set_visible(False)
        else:
            for rectangle, annotation in rectangles_with_annotation:
                annotation.set_visible(False)
        plt.draw()
    return inner
