from typing import List, Tuple


def sort_bbox(cells: List[Tuple[int, int, int, int]], px_bias: int = 5):
    """
    :param cells: 单元格坐标列表，格式为 [(x1, y1, x2, y2), ...]
    :param px_bias: 容忍度，坐标差在这个范围内认为是重复的
    """
    cells.sort(key=lambda cell: cell[1])
    rows = []
    current_row = []
    current_y = cells[0][1]
    for cell in cells:
        if abs(cell[1] - current_y) > px_bias:  # 如果y坐标相差较大，则认为是新的一行
            if current_row:
                rows.append(current_row)
            current_row = [cell]
            current_y = cell[1]
        else:
            current_row.append(cell)

    if current_row:
        rows.append(current_row)

    for row in rows:
        row.sort(key=lambda cell: cell[0])

    return rows


def remove_duplicates(cells: List[Tuple[int, int, int, int]], px_bias: int = 10):
    """
    移除重复的单元格
    :param cells: 单元格坐标列表，格式为 [(x1, y1, x2, y2), ...]
    :param px_bias: 容忍度，坐标差在这个范围内认为是重复的
    :return: 移除重复后的单元格列表
    """

    def is_duplicate(cell1, cell2):
        """
        判断两个单元格是否是重复的
        :param cell1: 第一个单元格坐标 (x1, y1, x2, y2)
        :param cell2: 第二个单元格坐标 (x1, y1, x2, y2)
        :return: 如果是重复的返回 True，否则返回 False
        """
        return all(abs(c1 - c2) <= px_bias for c1, c2 in zip(cell1, cell2))

    unique_cells = []
    for cell in cells:
        if not any(is_duplicate(cell, unique_cell) for unique_cell in unique_cells):
            unique_cells.append(cell)
    return unique_cells


def is_contained(box1: Tuple, box2: Tuple, px_bias: int):
    """
    判断 box1 是否完全包含在 box2 中。
    :param box1: (x1, y1, x2, y2)
    :param box2: (x1, y1, x2, y2)
    :param px_bias: 容忍偏差
    """
    a1, b1, a2, b2 = box1
    x1, y1, x2, y2 = box2
    return ((x1 - px_bias <= a1 <= x2 + px_bias)
            and (y1 - px_bias <= b1 <= y2 + px_bias)
            and (x1 - px_bias <= a2 <= x2 + px_bias)
            and (y1 - px_bias <= b2 <= y2 + px_bias))


def remove_duplicates_and_contained_bbox(bbox_res, px_bias=10):
    """
    去重和剔除包含关系的文本框， 并按上边界排序
    """
    cells = {tuple(item["bbox"]): item for item in bbox_res}
    unique_blocks = remove_duplicates(list(cells.keys()), 10)
    filtered_blocks = []
    for i, block1 in enumerate(unique_blocks):
        rect1 = tuple(block1)
        contained = False
        for j, block2 in enumerate(unique_blocks):
            if i != j:
                rect2 = tuple(block2)
                if is_contained(rect1, rect2, px_bias):
                    contained = True
                    break
        if not contained:
            filtered_blocks.append(block1)
    data = [v for k, v in cells.items() if k in filtered_blocks]
    data.sort(key=lambda k: k['bbox'][1])
    return data
