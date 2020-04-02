import json
from copy import deepcopy
from typing import List, Tuple, Union, Optional, MutableMapping, Callable

from .rectangle import Rectangle


Num = Union[int, float]
RectType = Tuple[Num, Num]
Group = MutableMapping[Num, List[RectType]]
DictGroup = MutableMapping[Num, Group]
GroupIdx = MutableMapping[Num, List[Num]]
DictGroupIdx = MutableMapping[Num, GroupIdx]


def scaling_all_group(rectangles: DictGroup, strain: Num=1., h1: Optional[Num]=None, 
                      rounding_func: Optional[Callable[[Num], Num]]=None) -> DictGroup:
    """Функция масштабирования группы прямоугольников

    Подробнее см. описание функции scaling.
    
    Parameters
    ----------
    rectangles : MutableMapping[Num, MutableMapping[Num, List[Optional[Tuple[Num, Num]]]]]
        Набор прямоугольников, сгруппированных по толщине и приоритету. 
        Словарь, где толщина является ключом, а значением - отображение 
        приоритета в список прямоугольников.
    strain : Num
        Поправочный коэффициент. Если :math:`k < 1`, то длина корректируется 
        в меньшую строну, а :math:`k > 1` в большую. Если нужен дополнительный 
        запас по длине, нужно установить значение :math:`k > 1`.
    h1 : Optional[Num]
        Толщина детали после деформации. Если она не установлена, то бурется 
        максимальная толщина из деталей в rectangles.
    rounding_func : Optional[Callable[[Num], Num]]
        Функция округления длины. По умолчанию None, т.е. округления не производится.
    
    Returns
    -------
    remaining : MutableMapping[Num, MutableMapping[Num, List[Optional[Tuple[Num, Num]]]]]
        Новы набор прямоугольников с преобразованной длиной, ширина остается неизменной.

    Examples
    --------
    >>> d = {3.0: {1: [(2, 3), (5, 5)]}, 2.0: {1: [(10, 10)]}, 1.0: {2: [(7, 9)], 3: [(5, 3), (4, 6)]}} 
    >>> scaling_all_group(d) 
    {3.0: {1: [(2, 3), (5, 5)]}, 2.0: {1: [(10, 6.666666666666667)]}, 1.0: {2: [(7, 3.0)], 3: [(5, 1.0), (4, 2.0)]}}

    Корректировака размеров в меньшую сторону:

    >>> scaling_all_group(d, strain=0.8) 
    {3.0: {1: [(2, 3), (5, 5)]}, 2.0: {1: [(10, 5.333333333333334)]}, 1.0: {2: [(7, 2.4000000000000004)], 3: [(5, 0.8), (4, 1.6)]}}

    Преобразование к произвольной толщине:

    >>> scaling_all_group(d, strain=1.1, h1=4) 
    {3.0: {1: [(2, 2.475), (5, 4.125)]}, 2.0: {1: [(10, 5.5)]}, 1.0: {2: [(7, 2.475)], 3: [(5, 0.8250000000000001), (4, 1.6500000000000001)]}}
    >>> scaling_all_group(d, strain=1.1, h1=1.5) 
    {3.0: {1: [(2, 6.6000000000000005), (5, 11.0)]}, 2.0: {1: [(10, 14.666666666666668)]}, 1.0: {2: [(7, 6.6000000000000005)], 3: [(5, 2.2), (4, 4.4)]}}

    Округление размеров:

    >>> scaling_all_group(d, strain=1.1, rounding_func=round) 
    {3.0: {1: [(2, 3), (5, 5)]}, 2.0: {1: [(10, 7)]}, 1.0: {2: [(7, 3)], 3: [(5, 1), (4, 2)]}}
    >>> scaling_all_group(d, strain=1.1, rounding_func=lambda x: round(x, 1)) 
    {3.0: {1: [(2, 3), (5, 5)]}, 2.0: {1: [(10, 7.3)]}, 1.0: {2: [(7, 3.3)], 3: [(5, 1.1), (4, 2.2)]}}
    """
    if h1 is None:
        h1 = max(rectangles.keys())

    remaining: DictGroup = {}

    for height, group in rectangles.items():
        if h1 != height:
            remaining[height] = scaling(group, height, h1, 
                                        strain=strain, rounding_func=rounding_func)
        else:
            remaining[height] = deepcopy(group)  # mypy error, Sequence to List
    
    return remaining


def scaling(group: Group, height: Num, h1: Num, strain: Num=1., 
            rounding_func: Optional[Callable[[Num], Num]]=None) -> Group:
    """Функция масштабирования прямоугольников

    Новая длина детали рассчитывается по формуле:
    :math:`l_1=k\\frac{h_0 l_0}{h_1}`, 
    где :math:`k` - поправочный коэффициент, 
        :math:`h_0` - исходная толщина, 
        :math:`l_0` - исходная длина, 
        :math:`h_1` - толщина после деформации.

    Parameters
    ----------
    group : MutableMapping[Num, List[Optional[Tuple[Num, Num]]]]
        Набор прямоугольников, сгруппированных по приоритету, представленный 
        словарем, где приоритет в качестве ключа, а в качестве значения список 
        кортежей с парами ширина, длина прямоугольника.
    height : Num
        Текущая толщина детали.
    h1 : Num
        Толщина детали после деформации.
    strain : Num
        Поправочный коэффициент. Если :math:`k < 1`, то длина корректируется 
        в меньшую строну, а :math:`k > 1` в большую. Если нужен дополнительный 
        запас по длине, нужно установить значение :math:`k > 1`.
    rounding_func : Optional[Callable[[Num], Num]]
        Функция округления длины. По умолчанию None, т.е. округления не производится.
    
    Returns
    -------
    new_group : MutableMapping[Num, List[Optional[Tuple[Num, Num]]]]
        Новый набор прямоугольников, с измененной длиной, ширина 
        (первая компонента кортежа) остается неизменной.

    Examples
    --------
    >>> d = {1: [(6, 4), (5, 7)], 2: [(10, 10)]}
    >>> scaling(d, 1.0, 3.0) 
    {1: [(6, 1.3333333333333333), (5, 2.3333333333333335)], 2: [(10, 3.3333333333333335)]}

    Корректировка длины в большую сторону:

    >>> scaling(d, 1.0, 3.0, strain=1.1) 
    {1: [(6, 1.4666666666666668), (5, 2.566666666666667)], 2: [(10, 3.666666666666667)]}
    
    Использование функции округления:

    >>> scaling(d, 1.0, 3.0, strain=1.1, rounding_func=round) 
    {1: [(6, 1), (5, 3)], 2: [(10, 4)]}
    >>> scaling(d, 1.0, 3.0, strain=1.1, rounding_func=lambda x: round(x, 1)) 
    {1: [(6, 1.5), (5, 2.6)], 2: [(10, 3.7)]}
    """
    new_group: Group = {}

    for priority, v in group.items():
        new_group[priority] = []
        for i, r in enumerate(v):
            l_1 = deformation(r[1], height, h1, strain=strain, rounding_func=rounding_func)
            # l_1 = strain * (height * r[1] / h1)
            # if rounding_func is not None:
            #     l_1 = rounding_func(l_1)
            new_group[priority].append((r[0], l_1))
    
    return new_group


def deformation(length, height: Num, h1: Num, strain: Num=1., rounding_func: Optional[Callable[[Num], Num]]=None):
    l_1 = strain * (height * length / h1)
    if rounding_func is not None:
        l_1 = rounding_func(l_1)
    return l_1


def back_deformation(length, height: Num, h1: Num, strain: Num=1., rounding_func: Optional[Callable[[Num], Num]]=None):
    l_1 = length / (strain * height) * h1
    if rounding_func is not None:
        l_1 = rounding_func(l_1)
    return l_1


def items_by_index(rectangles: DictGroup, indices: DictGroupIdx) -> DictGroup:
    """Получение выборки элементов из вложенного словаря по индексам

    Parameters
    ----------
    rectangles : MutableMapping[Num, MutableMapping[Num, List[Optional[Tuple[Num, Num]]]]]
        Набор прямоугольников, сгруппированных по толщине и приоритету.
    indices : 
        Индексы элементов, той же структуры, что и rectangles.
    
    Returns
    -------
    d : MutableMapping[Num, MutableMapping[Num, List[Optional[Tuple[Num, Num]]]]]
        Новый набор прямоугольников, индексы которых указаны в indices.

    Examples
    --------
    >>> d = {3.0: {2: [(7, 9), (4, 3), (5, 5)]}, 2.0: {1: [(2, 4)], 3: [(5, 3), (4, 6), (1, 2)]}}
    >>> idxs = {3.0: {2: [1]}, 2.0: {3: [0, 2]}}
    >>> items_by_index(d, idxs) 
    {3.0: {2: [(4, 3)]}, 2.0: {3: [(5, 3), (1, 2)]}}
    """
    d: DictGroup = {}
    for h, group in indices.items():
        d[h] = {}
        for p, idx in group.items():
            d[h][p] = [item for i, item in enumerate(rectangles[h][p]) if i in idx]

    return d


def add_allowance(rectangles, allowance):
    """Добавление припусков к размерам прямоугольников"""
    # TODO: Добавить реализацию
    pass


def isnamedtupleinstance(x):
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple: 
        return False
    f = getattr(t, '_fields', None)
    d = getattr(t, '_asdict', None)
    if not isinstance(f, tuple) and d is not None: 
        return False
    return all(type(n) == str for n in f)


def area(rectangles, as_nt=False):
    s = dict()
    for h, group in rectangles.items():
        s[h] = 0.
        for p, list_r in group.items():
            if as_nt:
                for r in list_r:
                    s[h] += r.w * r.l
            else:
                for r in list_r:
                    s[h] += r[0] * r[1]
    return s


def to_json(name: str, rectangles: DictGroup) -> None:
    if not name.endswith('.json'):
        name += '.json'
    
    with open(name, 'w') as f:
        res = _to_json(rectangles, indent=4)
        f.write(res)
        # json.dump(res, f, indent=4)


def _to_json(o, level=0, indent=4):
    SPACE = " "
    NEWLINE = "\n"
    ret = ""
    if isinstance(o, dict):
        ret += "{" + NEWLINE
        comma = ""
        for k,v in o.items():
            ret += comma
            comma = ",\n"
            ret += SPACE * indent * (level+1)
            ret += '"' + str(k) + '":' + SPACE
            ret += _to_json(v, level + 1)

        ret += NEWLINE + SPACE * indent * level + "}"
    elif isinstance(o, list):
        ret += "["
        if len(o) > 1 and isinstance(o[0], (tuple, list, dict)):
            ret += NEWLINE + SPACE * indent * (level+1)
            ret += ("," + NEWLINE + SPACE * indent * (level+1)).join([_to_json(e, level+1) for e in o])
            ret += NEWLINE + SPACE * indent * level
        else:
            ret += ", ".join([_to_json(e, level+1) for e in o])
        ret += "]"
    elif isnamedtupleinstance(o):
        ret += json.dumps(o._asdict())
    # elif isinstance(o, numpy.ndarray) and numpy.issubdtype(o.dtype, numpy.integer):
    #     ret += "[" + ','.join(map(json.dumps, o.flatten().tolist())) + "]"
    # elif isinstance(o, numpy.ndarray) and numpy.issubdtype(o.dtype, numpy.inexact):
    #     ret += "[" + ','.join(map(lambda x: json.dumps(x), o.flatten().tolist())) + "]"
    elif isinstance(o, (str, bool, int, float, tuple, list)) or o is None:
        ret += json.dumps(o)
    else:
        raise TypeError("Unknown type '%s' for json serialization" % str(type(o)))
    return ret