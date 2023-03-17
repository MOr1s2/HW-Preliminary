#!/bin/bash
import sys
import math

import numpy as np

BOT = {}  # key:机器人ID  value:(0:工作台ID,1:携带物品类型,2:时间系数,3:碰撞系数,4:角速度,5:线速度x,6:线速度y,7:朝向,8:坐标x,9:坐标y)
WORKBENCH = {}  # key:工作台ID  value:(0:工作台类型,1:坐标x,2:坐标y,3:剩余生产时间,4:原材料格状态,5:产品格状态)
ZERO = [3, 4, 9, 13]  # i:机器人ID  ZERO[i]:机器人距离最近的工作台ID
LAST_BENCH = [-1] * 4  # i:机器人ID  LAST_BENCH[i]:机器人最后经过的工作台ID
PATH = []  # i:工作台ID  PATH[i]:工作台i指向的工作台ID

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


def cal_rotate(x_v, y_v, x_b2w, y_b2w):
    b2w = np.array((x_b2w, y_b2w))
    v = np.array((x_v, y_v))
    angle = np.arctan2(np.cross(v, b2w), np.dot(v, b2w))

    if abs(angle) < math.pi / 20:
        return 0
    else:
        if angle > 0:
            return MAX_ROTATE_SPEED
        else:
            return -MAX_ROTATE_SPEED


def get_zero(bots, workbenchs):
    for key in bots.keys:
        if (bots[key][0] != -1):
            ZERO[key] = bots[key][0]
        else:
            min = 1e18
            for key_2 in workbenchs.keys():
                if (workbenchs[key_2][0] in (1, 2, 3)):
                    temp = (workbenchs[key_2][1] - bots[key][8]) ** 2 + (workbenchs[key_2][2] - bots[key][9]) ** 2
                    if (temp < min):
                        min = temp
                        ZERO[key] = key_2

def get_path(workbenchs):
    h_route = []   # h_route中每个元素为元组：（工作台ID，坐标x，坐标y）。整个h_route存放的是H圈的到达序列
    for key in workbenchs.keys():
        h_route += [(key, workbenchs[key][1], workbenchs[key][2])]
    length = len(h_route)
    dists = [[0] * length] * length
    dists = np.array(dists, dtype=np.float32)
    # 算各个工作台之间的距离，共 n中取2 次
    for i in range(length):
        for j in range(i+1, length):
            dists[i][j] = dists[j][i] = math.sqrt((h_route[i][1] - h_route[j][1])**2 + (h_route[i][2] - h_route[j][2])**2)
    # 开始边交换寻找近似最优H圈
    exchange = False
    old_h_length = 1e18
    for i in range(5000):
        for j in range(length - 2):
            if (exchange == True):
                break
            for k in range(j + 2, length):
                if (exchange == True):
                    break
                if (dists[h_route[j][0]][h_route[k][0]] + dists[h_route[j + 1][0]][h_route[(k + 1) % length][0]] <
                        dists[h_route[j][0]][h_route[j + 1][0]] + dists[h_route[k][0]][h_route[(k + 1) % length][0]]):
                    h_route[j + 1: (k + 1)] = h_route[j + 1:(k + 1)][::-1]
                    exchange = True
        exchange = False
        h_length = 0

        for j in range(length):
            h_length += dists[h_route[j][0]][h_route[(j + 1) % length][0]]
        if (h_length >= old_h_length):
            break
        old_h_length = h_length
    for idx in range(length):
        PATH[h_route[idx][0]] = h_route[(idx + 1) % length][0]


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
                    BOT.update({bot_id: (-1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, x, y)})
                    bot_id += 1
                else:
                    WORKBENCH.update({bench_id: (int(c), x, y, -1, 0, 0)})
                    PATH.append(-1)
                    bench_id += 1
            count += 1
        _line = input()
    get_path(WORKBENCH)

    # f = open('log.txt', 'w')
    # f.write(str(PATH) + '\n')
    # f.write(str(bench_id) + '\n')
    # f.close()


def read_workbench(_k):
    for _i in range(_k):
        _parts = input().split(' ')
        WORKBENCH.update({_i: (int(_parts[0]), float(_parts[1]), float(_parts[2]),
                               int(_parts[3]), int(_parts[4]), int(_parts[5]))})


def read_bot():
    for _i in range(4):
        _parts = input().split(' ')
        BOT.update({_i: (int(_parts[0]), int(_parts[1]), float(_parts[2]), float(_parts[3]), float(_parts[4]),
                         float(_parts[5]), float(_parts[6]), float(_parts[7]), float(_parts[8]), float(_parts[9]))})


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

            if LAST_BENCH[i] == -1:
                j = ZERO[i]
            else:
                j = PATH[LAST_BENCH[i]]
            rotate = cal_rotate(BOT[i][5], BOT[i][6], WORKBENCH[j][1] - BOT[i][8], WORKBENCH[j][2] - BOT[i][9])
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
                if item == 0 and WORKBENCH[j][5] == 1:
                    sys.stdout.write('buy %d\n' % i)
                LAST_BENCH[i] = j

        finish()
