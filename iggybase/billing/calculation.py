from iggybase import core

def line_item_total_cost(cols):
    cost = cols[0] * cols[1]
    percent = cols[2]
    return core.calculation.percent([cost, percent])

