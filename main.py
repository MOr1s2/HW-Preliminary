#!/bin/bash
import sys
import math
import numpy as np

BOT = {}  # key:机器人ID  value:(0:工作台ID,1:携带物品类型,2:时间系数,3:碰撞系数,4:角速度,5:线速度x,6:线速度y,7:朝向,8:坐标x,9:坐标y)
WORKBENCH = {}  # key:工作台ID  value:(0:工作台类型,1:坐标x,2:坐标y,3:剩余生产时间,4:原材料格状态,5:产品格状态)
WORKBENCH = {}  # key:工作台ID  value:(0:工作台类型,1:坐标x,2:坐标y,3:剩余生产时间,4:原材料格状态,5:产品格状态)

UNIT_LEN = 0.5
MAX_FORWARD_SPEED = 6.0
MAX_BACKWARD_SPEED = -2.0
MAX_ROTATE_SPEED = math.pi
MAX_TRACTION = 250
MAX_TORQUE = 50

flag = 0


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
    _vec = x_v * x_b2w + y_v * y_b2w
    _len = math.sqrt(x_v * x_v + y_v * y_v) * math.sqrt(x_b2w * x_b2w + y_b2w * y_b2w)
    _cos = _vec / (_len * 1.0 + 1e-6)
    if x_v * y_b2w - x_b2w * y_v > 0:
        angle = math.acos(_cos)
    else:
        angle = -math.acos(_cos)

    b2w = np.array((x_b2w, y_b2w))
    v = np.array((x_v, y_v))
    angle = np.arctan2(np.cross(v, b2w), np.dot(v, b2w))

    if abs(angle) < math.pi / 20:
        return 0
    else:
        if angle > 0:
            return math.pi
        else:
            return -math.pi


def init_util_ok():
    count = 0
    bot_id = 0
    bench_id = 0
    while input() != "OK":
        for c in input():
            if c != '.':
                x = count % 100 * UNIT_LEN + 0.25
                y = count / 100 * UNIT_LEN + 0.25
                if c == 'A':
                    BOT.update({bot_id: (-1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, x, y)})
                    bot_id += 1
                else:
                    WORKBENCH.update({bench_id: (int(c), x, y, -1, 0, 0)})
                    bench_id += 1
            count += 1


def read_workbench(_k):
    for i in range(_k):
        _parts = input().split(' ')
        WORKBENCH.update({i: (int(_parts[0]), float(_parts[1]), float(_parts[2]),
                              int(_parts[3]), int(_parts[4]), int(_parts[5]))})


def read_bot():
    for i in range(4):
        _parts = input().split(' ')
        BOT.update({i: (int(_parts[0]), int(_parts[1]), float(_parts[2]), float(_parts[3]), float(_parts[4]),
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

        if flag % 4 == 0:
            sys.stdout.write('forward %d %f\n' % (0, 6.0))

            rotate = cal_rotate(BOT[0][5], BOT[0][6], 40.75 - BOT[0][8], 34.25 - BOT[0][9])
            sys.stdout.write('rotate %d %f\n' % (0, rotate))
            if BOT[0][0] == 12:
                sys.stdout.write('buy %d\n' % 0)
                flag += 1
        elif flag % 4 == 1:
            sys.stdout.write('forward %d %f\n' % (0, 6.0))

            rotate = cal_rotate(BOT[0][5], BOT[0][6], 13.25 - BOT[0][8], 34.25 - BOT[0][9])
            sys.stdout.write('rotate %d %f\n' % (0, rotate))

            if BOT[0][0] == 10:
                sys.stdout.write('sell %d\n' % 0)
                flag += 1
        elif flag % 4 == 2:
            sys.stdout.write('forward %d %f\n' % (0, 6.0))

            rotate = cal_rotate(BOT[0][5], BOT[0][6], 24.75 - BOT[0][8], 31.75 - BOT[0][9])
            sys.stdout.write('rotate %d %f\n' % (0, rotate))
            if BOT[0][0] == 13:
                sys.stdout.write('buy %d\n' % 0)
                flag += 1
        else:
            sys.stdout.write('forward %d %f\n' % (0, 6.0))

            rotate = cal_rotate(BOT[0][5], BOT[0][6], 13.25 - BOT[0][8], 34.25 - BOT[0][9])
            sys.stdout.write('rotate %d %f\n' % (0, rotate))

            if BOT[0][0] == 10:
                sys.stdout.write('sell %d\n' % 0)
                flag += 1
        finish()
