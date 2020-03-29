from pprint import pprint

from spp.ph import phspprg, phsbpprg, packaging
from spp import visualize_mgroup, visualize_separately
from spp.support import to_json, items_by_index, area


def example_1():
    width = 25
    length = 55
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

    res, unplaced_idx, length_marking, unused_length = packaging(width, length, rect, rounding_func=lambda x: round(x, 1), sorting="width")
    
    unplaced = items_by_index(rect, unplaced_idx)

    s = area(res, as_nt=True)
    required_s = area(rect)
    print(length_marking)
    print('-' * 50)
    print(f'Площадь листа: {width * length}')
    print(f'Минимально возможная площадь: {required_s}')
    print(f'Заполненная площадь: {s}')
    ratio = {k: round(v / (length_marking[k]*width), 2) for k, v in s.items()}
    print(f'Отношение покрытой площади к общей: {ratio}')
    print(f'Неиспользуемая длина при толщине 3.0 мм: {unused_length:.4f}')
    print('-' * 50)
    print('Размещенные прямоугольники:')
    d = {}
    for h, group in res.items():
        d[h] = {}
        for p, list_r in group.items():
            d[h][p] = [rect[h][p][r.idx] for r in list_r]
    pprint(d)  # res
    print('-' * 50)
    print('Неразмещенные прямоугольники:')
    pprint(unplaced)
    print('-' * 50)
    # visualize_mgroup(width, length, length_marking, res)

    visualize_separately(width, length_marking, res)


def example_2():
    width = 25
    length = 55
    rect = {
        3.0: {  # ширина w, длина l
            1: [(5, 3), (5, 3), (5, 5), (10, 10), (20, 14)],
            2: [(30, 8), (20, 10), (1, 10), (6, 6)],
            # 3: [(2, 4), (5, 5), (10, 5), (8, 4)],
            4: [(10, 20), (6, 4)],
        },
        2.0: {
            # 1: [(6, 3), (5, 3), (1, 5), (10, 10), (20, 14)], 
            # 2: [(5, 8), (15, 10), (3, 10), (6, 7), (4, 2)], 
            3: [(2, 4), (5, 7), (9, 5), (6, 4)],
            4: [],
        },
        1.0: {
            # 1: [(7, 7), (4, 5), (3, 3)], 
            2: [(10, 8), (9, 3), (5, 4), (6, 7), (5, 3)], 
            3: [(10, 10), (12, 6), (8, 7)],
        },
    }

    res, unplaced_idx, length_marking, unused_length = packaging(width, length, rect, rounding_func=lambda x: round(x, 1), sorting="width")
    
    unplaced = items_by_index(rect, unplaced_idx)

    s = area(res, as_nt=True)
    required_s = area(rect)

    print('-' * 50)
    print(f'Площадь листа: {width * length}')
    print(f'Минимально возможная площадь: {required_s}')
    print(f'Заполненная площадь: {s}')
    ratio = {k: round(v / (length_marking[k]*width), 2) for k, v in s.items()}
    print(f'Отношение покрытой площади к общей: {ratio}')
    print('-' * 50)
    print('Размещенные прямоугольники:')
    d = {}
    for h, group in res.items():
        d[h] = {}
        for p, list_r in group.items():
            d[h][p] = [rect[h][p][r.idx] for r in list_r]
    pprint(d)  # res
    print('Неразмещенные прямоугольники:')
    pprint(unplaced)
    print('-' * 50)
    # visualize_mgroup(width, length, length_marking, res)
    visualize_separately(width, length_marking, res)


def example_3():
    """Длина листа недостаточна для упаковки всех прямоугольников первого приоритета одной высоты"""
    width = 25
    length = 27
    rect = {
        3.0: {  # ширина w, длина l
            1: [(5, 3), (5, 3), (5, 5), (10, 10), (20, 14)],
            2: [(30, 8), (20, 10), (1, 10), (6, 6)],
            # 3: [(2, 4), (5, 5), (10, 5), (8, 4)],
            4: [(10, 20), (6, 4)],
        },
        2.0: {
            # 1: [(6, 3), (5, 3), (1, 5), (10, 10), (20, 14)], 
            # 2: [(5, 8), (15, 10), (3, 10), (6, 7), (4, 2)], 
            3: [(2, 4), (5, 7), (9, 5), (6, 4)],
            4: [],
        },
        1.0: {
            1: [(7, 7), (4, 5), (3, 3)], 
            2: [(10, 8), (9, 3), (5, 4), (6, 7), (5, 3)], 
            3: [(10, 10), (12, 6), (8, 7)],
        },
    }

    res, unplaced_idx, length_marking, unused_length = packaging(width, length, rect, rounding_func=lambda x: round(x, 1), sorting="width")
    
    unplaced = items_by_index(rect, unplaced_idx)

    s = area(res, as_nt=True)
    required_s = area(rect)
    print(length_marking)
    print('-' * 50)
    print(f'Площадь листа: {width * length}')
    print(f'Минимально возможная площадь: {required_s}')
    print(f'Заполненная площадь: {s}')
    ratio = {k: round(v / (length_marking[k]*width), 2) for k, v in s.items()}
    print(f'Отношение покрытой площади к общей: {ratio}')
    print('Неразмещенные прямоугольники:')
    pprint(unplaced)
    print('-' * 50)
    # visualize_mgroup(width, length, length_marking, res)
    visualize_separately(width, length_marking, res)


def main():
    example_1()
    # example_2()
    # example_3()


if __name__ == "__main__":
    main()
