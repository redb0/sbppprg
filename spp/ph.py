import sys
from copy import deepcopy
from itertools import product
from typing import Callable, List, MutableMapping, Optional, Tuple, Union, Dict

from .support import deformation, back_deformation
from .rectangle import Rectangle


Num = Union[int, float]
ListNum = List[Num]
RectType = Tuple[Num, Num]
Group = MutableMapping[Num, List[RectType]]
DictGroup = MutableMapping[Num, Group]
GroupIdx = MutableMapping[Num, List[int]]
DictGroupIdx = MutableMapping[Num, GroupIdx]
ResGroup = MutableMapping[Num, List[Rectangle]]
ResDictGroup = MutableMapping[Num, ResGroup]

    
def packaging(width: Num, length: Num, rectangles: DictGroup, 
              sorting: str="width", strain: Num=1., 
              rounding_func: Optional[Callable[[Num], Num]]=None) -> Tuple[ResDictGroup, DictGroupIdx, Dict[Num, Num], Num]:
    """Функция двумерной упаковки прямоугольников

    Алгоритм учитывает приоритета детали, толщину и возможность 
    гильотинного раскроя.

    Parameters
    ----------
    width : Union[int, float]
        Ширина прямоугольного листа.
    length : Union[int, float]
        Длина прямоугольного листа.
    rectangles : MutableMapping[Num, MutableMapping[Num, List[Optional[Tuple[Num, Num]]]]]
        Набор прямоугольников, сгруппированных по толщине и приоритету. 
        Словарь, где толщина является ключом, а значением - отображение 
        приоритета в список прямоугольников.
    sorting : str, {'width', 'length'}, default='width'
        Вариант сортировки: width или length.
    strain : Union[int, float]
        Корректирующи коэффициент. Используется при преобразовании размеров
        с учетом деформации после прокатки.
    rounding_func : Optional[Callable[[Num], Num]]
        Функция округления.

    Returns
    -------
    res : MutableMapping[Num, MutableMapping[Num, List[namedtuple('Rectangle', ('x', 'y', 'w', 'h'))]]]
        Набор прямоугольников, сгруппированных по толщине и приоритету, та же структура, что и у rectangles.
    indices : MutableMapping[Num, MutableMapping[Num, List[int]]]
        Индексы неразмещенных элементов, сгруппированные по толщине и приоритету.
    length_marking : List[Num]
        Длины листов для упаковки прямоугольников соответствующей толщины. 
        Порядок аналогичен res.
    length : Num
        Незадествованная длина.
    Examples
    --------

    """
    length_marking = {}  # значения длин выделенных для каждой толщины (группы)
    res: ResDictGroup = {}  # результат

    # толщина для преобразования, по максимальной толщине первого приоритета группы
    conversion_height = max([(k, min(v.keys())) for k, v in rectangles.items()], key=lambda x: x[0])[0]

    transformed_rectangles = deepcopy(rectangles)
    transformed_rectangles, indices = sort_rectangles(transformed_rectangles, sorting)
    
    sorted_keys_all: List[Tuple[Num, Num]] = []
    for h, g in transformed_rectangles.items():
        sorted_keys_all.extend(product((h, ), [p for p, v in g.items() if v]))
    sorted_keys_all = sorted(sorted_keys_all, key=lambda x: (x[1], -x[0]))

    for height, p in sorted_keys_all:
        if (height in res) and (not indices[height][p]):  # пустой
            continue
        if height not in length_marking:
            length_marking[height] = 0.
        current_y = length_marking[height]
        group = transformed_rectangles[height]
        if height != 3.0:                                                                                              
            new_len = deformation(length, conversion_height, height, strain=strain, rounding_func=lambda x: round(x, 1))
        else:
            new_len = length                                                                                          
        # получаем и упаковываем группы прямоугольников на лист с неизвестно длиной
        l, rect = phspprg(width, group, indices[height], y0=current_y)
        if l > new_len:
            reestablish(indices[height], rect)
            transformed_rectangles, indices = sort_rectangles(transformed_rectangles, sorting, indices)
            upper_bound, rect = phsbpprg(width, length, group, indices[height], y0=current_y)  # TODO: приоритет не учитывается
            if upper_bound == 0:
                continue
            l = upper_bound - current_y

        length_marking[height] += l

        if height in res:
            for key, list_r in rect.items():
                if key in res[height]:
                    res[height][key].extend(list_r)
                else:
                    res[height][key] = list_r
        else:
            res[height] = rect

        length -= back_deformation(l, conversion_height, height, strain=strain, rounding_func=lambda x: round(x, 4))
        if length == 0:
            break

    return res, indices, length_marking, length


def reestablish(indexes, donor):
    for p, list_r in donor.items():
        for r in list_r:
            indexes[p].append(r.idx)


def sort_rectangles(rectangles, sorting: str, indices=None):
    if sorting not in ["width", "length"]:
        raise ValueError(f"The algorithm only supports sorting by width or length but {sorting} was given.")
    if sorting == "width":
        wh = 0
    else:
        wh = 1
    
    if indices is None:
        indices = dict()

    for height, group in rectangles.items():
        if height not in indices:
            indices[height] = {}
        for p, r_list in group.items():
            for i, r in enumerate(r_list):
                if r[0] > r[1]:
                    r_list[i] = (r_list[i][1], r_list[i][0])
            if p not in indices[height]:
                indices[height][p] = sorted(range(len(r_list)), key=lambda x: -group[p][x][wh])
            else:
                indices[height][p] = sorted(indices[height][p], key=lambda x: -group[p][x][wh])
    
    return rectangles, indices


def phsbpprg(width: Num, length: Num, rectangles: Group, 
             indexes: GroupIdx, x0: Num=0., y0: Num=0.) -> Tuple[Num, ResGroup]:
    """Функция упаковки листа с фиксированно длиной"""
    
    result: ResGroup = {}
    
    recursive_packing(x0, y0, width, length, 1, rectangles, indexes, result)

    if result:
        real_lenght = max([max([r.y + r.l for r in list_r]) for p, list_r in result.items()])
    else:
        real_lenght = 0.

    return real_lenght, result


def phspprg(width: Num, rectangles: Group, indices: GroupIdx, x0: Num=0., y0: Num=0) -> Tuple[Num, ResGroup]:
    """Функция упаковки листа неограниченной длины"""
    
    result: ResGroup = {}
    
    max_priority = min([k for k, v in indices.items() if v])
    first_priority = indices[max_priority]

    x, y, w, l, L = x0, y0, 0, 0, y0
    while first_priority:
        idx = first_priority.pop(0)
        r = rectangles[max_priority][idx]

        if max_priority not in result:
            result[max_priority] = []
        if r[1] > width:
            result[max_priority].append(Rectangle(x, y, r[0], r[1], idx))
            x, y, w, l, L = r[0], L, width - r[0], r[1], L + r[1]
        else:
            result[max_priority].append(Rectangle(x, y, r[1], r[0], idx))
            x, y, w, l, L = r[1], L, width - r[1], r[0], L + r[0]
        recursive_packing(x, y, w, l, 1, rectangles, indices, result)
        x, y = 0, L

    return L - y0, result


def recursive_packing(x: Num, y: Num, w: Num, h: Num, D: int, 
                      remaining: Group, indices: GroupIdx, result: ResGroup) -> None:
    """Helper function to recursively fit a certain area."""
    g = len(remaining.keys())
    variant: List[int] = []
    orientation: List[int] = []
    best: List[int] = []
    priorities: List[Num] = []
    for i, key in enumerate(remaining.keys()):
        priorities.append(key)
        v, o, b = get_best_fig(w, h, D, indices[key], remaining[key])
        variant.append(v) 
        orientation.append(o) 
        best.append(b)

    for i in range(g):
        if variant[i] < 5:
            key = priorities[i]
            if orientation[i] == 0:
                omega, d = remaining[key][best[i]]
            else:
                d, omega = remaining[key][best[i]]
            if key not in result:
                result[key] = []
            result[key].append(Rectangle(x, y, omega, d, best[i]))
            indices[key].remove(best[i])
            if variant[i] == 2:
                recursive_packing(x, y + d, w, h - d, D, remaining, indices, result)
            elif variant[i] == 3:
                recursive_packing(x + omega, y, w - omega, h, D, remaining, indices, result)
            elif variant[i] == 4:
                min_w, min_h = sys.maxsize, sys.maxsize
                for p, idxs in indices.items():
                    for idx in idxs:
                        min_w = min(min_w, remaining[p][idx][0])
                        min_h = min(min_h, remaining[p][idx][1])
                # Because we can rotate:
                min_w = min(min_h, min_w)
                min_h = min_w
                if w - omega < min_w:
                    recursive_packing(x, y + d, w, h - d, D, remaining, indices, result)
                elif h - d < min_h:
                    recursive_packing(x + omega, y, w - omega, h, D, remaining, indices, result)
                elif omega < min_w:
                    recursive_packing(x + omega, y, w - omega, d, D, remaining, indices, result)
                    recursive_packing(x, y + d, w, h - d, D, remaining, indices, result)
                else:
                    recursive_packing(x, y + d, omega, h - d, D, remaining, indices, result)
                    recursive_packing(x + omega, y, w - omega, h, D, remaining, indices, result)
            break
    

def get_best_fig(w: Num, l: Num, D: int, indices: List[int], remaining: List[RectType]) -> Tuple[int, int, int]:
    priority, orientation, best = 6, None, None  # mypy error Optional[int]
    for idx in indices:
        for j in range(0, D + 1):
            if priority > 1 and remaining[idx][(0 + j) % 2] == w and remaining[idx][(1 + j) % 2] == l:
                priority, orientation, best = 1, j, idx
                break
            elif priority > 2 and remaining[idx][(0 + j) % 2] == w and remaining[idx][(1 + j) % 2] < l:
                priority, orientation, best = 2, j, idx
            elif priority > 3 and remaining[idx][(0 + j) % 2] < w and remaining[idx][(1 + j) % 2] == l:
                priority, orientation, best = 3, j, idx
            elif priority > 4 and remaining[idx][(0 + j) % 2] < w and remaining[idx][(1 + j) % 2] < l:
                priority, orientation, best = 4, j, idx
            elif priority > 5:
                priority, orientation, best = 5, j, idx
    return priority, orientation, best
