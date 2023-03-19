#!/bin/bash
import sys
import math

import numpy as np

BOT = {}  # key:机器人ID  value:[0:工作台ID,1:携带物品类型,2:时间系数,3:碰撞系数,4:角速度,5:线速度x,6:线速度y,7:朝向,8:坐标x,9:坐标y]
WORKBENCH = {}  # key:工作台ID  value:[0:工作台类型,1:坐标x,2:坐标y,3:剩余生产时间,4:原材料格状态,5:产品格状态]
ITEM2BENCH = []  # i:机器人携带物品类型  ITEM2BENCH[i]:回收当前物品的工作台ID
NEXT_BENCH_ID = [-1] * 4

UNIT_LEN = 0.5
MAX_FORWARD_SPEED = 6.0
MAX_BACKWARD_SPEED = -2.0
MAX_ROTATE_SPEED = math.pi
MAX_TRACTION = 250
MAX_TORQUE = 50


def f(x, max_x, min_rate):
    if x < max_x:
        return (1 - pow(1 - pow(1 - x / max_x, 2), 0.5)) * (1 - min_rate) + min_rate


def cal_frame():
    pass


def cal_momentum():
    pass


def cal_price(initial, frame, momentum):
    loss_time = f(frame, 9000, 0.8)
    loss_collision = f(momentum, 1000, 0.8)
    return initial * loss_time * loss_collision


def cal_speed():
    pass


def cal_rotate(ori, x_b2w, y_b2w):
    b2w = np.array((x_b2w, y_b2w))
    v = np.array((math.cos(ori), math.sin(ori)))
    angle = np.arctan2(np.cross(v, b2w), np.dot(v, b2w))

    if abs(angle) < math.pi / 20:
        return 0
    else:
        if angle > 0:
            return MAX_ROTATE_SPEED
        else:
            return -MAX_ROTATE_SPEED


def item2bench(bench_id, bench_type):
    for _ in range(8):
        ITEM2BENCH.append([])
    if bench_type == 4:
        ITEM2BENCH[1].append(bench_id)
        ITEM2BENCH[2].append(bench_id)
    elif bench_type == 5:
        ITEM2BENCH[1].append(bench_id)
        ITEM2BENCH[3].append(bench_id)
    elif bench_type == 6:
        ITEM2BENCH[2].append(bench_id)
        ITEM2BENCH[3].append(bench_id)
    elif bench_type == 7:
        ITEM2BENCH[4].append(bench_id)
        ITEM2BENCH[5].append(bench_id)
        ITEM2BENCH[6].append(bench_id)
    elif bench_type == 8:
        ITEM2BENCH[7].append(bench_id)
    elif bench_type == 9:
        for _i in range(7):
            ITEM2BENCH[_i + 1].append(bench_id)
    else:
        ITEM2BENCH[0].append(bench_id)


def get_next_bench(bot_id):
    _item = BOT[bot_id][1]
    bench_ids = ITEM2BENCH[_item]
    x_bot, y_bot = BOT[bot_id][8], BOT[bot_id][9]

    min_dist = 5e3
    next_bench_id = -1
    for bench_id in bench_ids:
        if _item != 0:
            _material = get_material(bench_id)
            if _material[_item] == 1:
                continue
        if _item == 0 and WORKBENCH[bench_id][5] == 0:
            continue
        x_bench, y_bench = WORKBENCH[bench_id][1], WORKBENCH[bench_id][2]
        dist = (x_bench - x_bot) ** 2 + (y_bench - y_bot) ** 2
        if dist < min_dist:
            next_bench_id = bench_id
            min_dist = dist
    return next_bench_id


def get_material(bench_id):
    if WORKBENCH[bench_id][0] in [1, 2, 3]:
        return [-1] * 7
    elif WORKBENCH[bench_id][0] == 4:
        _material = [-1, 0, 0, -1, -1, -1, -1, -1]
    elif WORKBENCH[bench_id][0] == 5:
        _material = [-1, 0, -1, 0, -1, -1, -1, -1]
    elif WORKBENCH[bench_id][0] == 6:
        _material = [-1, -1, 0, 0, -1, -1, -1, -1]
    elif WORKBENCH[bench_id][0] == 7:
        _material = [-1, -1, -1, -1, 0, 0, 0, -1]
    elif WORKBENCH[bench_id][0] == 8:
        _material = [-1, -1, -1, -1, -1, -1, -1, 0]
    else:
        _material = [-1, 0, 0, 0, 0, 0, 0, 0]

    d2b = bin(WORKBENCH[bench_id][4])
    for _i in range(len(d2b) - 2):
        if _material[_i] != -1:
            _material[_i] = int(d2b[-_i - 1])
    return _material


def init_util_ok():
    count = 0
    bot_id = 0
    bench_id = 0
    _line = input()
    while _line != "OK":
        for c in _line:
            if c != '.':
                x = count % 100 * UNIT_LEN + 0.25
                y = count / 100 * UNIT_LEN + 0.25
                if c == 'A':
                    BOT.update({bot_id: [-1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, x, y]})
                    bot_id += 1
                else:
                    WORKBENCH.update({bench_id: [int(c), x, y, -1, 0, 1]})
                    item2bench(bench_id, int(c))
                    bench_id += 1
            count += 1
        _line = input()
    for _i in range(4, 8):
        ITEM2BENCH[0].extend(ITEM2BENCH[_i])
    for _i in range(4):
        NEXT_BENCH_ID[_i] = get_next_bench(_i)


def read_workbench(_k):
    for _i in range(_k):
        _parts = input().split(' ')
        WORKBENCH.update({_i: [int(_parts[0]), float(_parts[1]), float(_parts[2]),
                               int(_parts[3]), int(_parts[4]), int(_parts[5])]})


def read_bot():
    for _i in range(4):
        _parts = input().split(' ')
        BOT.update({_i: [int(_parts[0]), int(_parts[1]), float(_parts[2]), float(_parts[3]), float(_parts[4]),
                         float(_parts[5]), float(_parts[6]), float(_parts[7]), float(_parts[8]), float(_parts[9])]})


def finish():
    sys.stdout.write('OK\n')
    sys.stdout.flush()


if __name__ == '__main__':
    init_util_ok()
    finish()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        parts = line.split(' ')
        frame_id = int(parts[0])
        money = int(parts[1])

        line = input()
        k = int(line)

        read_workbench(k)
        read_bot()

        if input() != 'OK':
            break

        sys.stdout.write('%d\n' % frame_id)

        for i in range(4):
            j = NEXT_BENCH_ID[i]
            if j == -1:
                for _ in range(4):
                    NEXT_BENCH_ID[_] = get_next_bench(_)
                continue
            rotate = cal_rotate(BOT[i][7], WORKBENCH[j][1] - BOT[i][8], WORKBENCH[j][2] - BOT[i][9])
            sys.stdout.write('rotate %d %f\n' % (i, rotate))

            if rotate == 0:
                speed = MAX_FORWARD_SPEED
            else:
                speed = MAX_FORWARD_SPEED / 5
            # if BOT[i][8] < 0.5 or BOT[i][9] < 0.5 or BOT[i][8] > 49.5 or BOT[i][9] > 49.5:
            #     speed = MAX_BACKWARD_SPEED

            sys.stdout.write('forward %d %f\n' % (i, speed))
            if BOT[i][0] == j:
                item = BOT[i][1]
                material = get_material(j)
                if material[item] == 0:
                    sys.stdout.write('sell %d\n' % i)
                    BOT[i][1] = 0
                    WORKBENCH[j][4] += (2 ** item)
                if BOT[i][1] == 0 and WORKBENCH[j][5] == 1:
                    sys.stdout.write('buy %d\n' % i)
                    BOT[i][1] = WORKBENCH[j][0]
                    WORKBENCH[j][5] == 0
                for _ in range(4):
                    NEXT_BENCH_ID[_] = get_next_bench(_)
        finish()
