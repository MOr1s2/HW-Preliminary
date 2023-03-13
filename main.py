#!/bin/bash
import sys
import math

BOT = {}  # key: BOT_ID   value: LOCATION (x, y)
WORKBENCH = {}  # key: (TYPE, LOCATION)    value: (TIME, MATERIAL, PRODUCT)

UNIT_LEN = 0.5
MAX_FORWARD_SPEED = 6.0
MAX_BACKWARD_SPEED = -2.0
MAX_ROTATE_SPEED = math.pi
MAX_TRACTION = 250
MAX_TORQUE = 50

BOT_LOCATION = ()
FROM = ()
TO = ()

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

def cal_speed(start, end):
    return 0, 0


def init_util_ok():
    count = 0
    bot_id = 0
    while input() != "OK":
        for c in input():
            if c != '.':
                x = count % 100 * UNIT_LEN + 0.25
                y = count / 100 * UNIT_LEN + 0.25
                if c == 'A':
                    BOT.update({bot_id: (-1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, -1, x, y)})
                    bot_id += 1
                else:
                    WORKBENCH.update({(int(c), x, y): -1})
            count += 1
    for key in WORKBENCH.keys():
        if key[0] == 1:
            FROM = key[2: 4]
        if key[0] == 4:
            TO = key[2: 4]


def read_k_workbench(k):
    for i in range(k):
        parts = input().split(' ')
        WORKBENCH.update({(int(parts[0]), float(parts[1]), float(parts[2])):
                              (int(parts[3]), int(parts[4]), int(parts[5]))})


def read_bot():
    for i in range(4):
        parts = input().split(' ')
        BOT.update({i: (int(parts[0]), int(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]),
                        float(parts[5]), float(parts[6]), float(parts[7]), float(parts[8]), float(parts[9]))})

    BOT_LOCATION = BOT[0][-2:]


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

        read_k_workbench(k)
        read_bot()

        if input() != 'OK':
            break

        sys.stdout.write('%d\n' % frame_id)

        if flag == 0:
            line_speed, angle_speed = cal_speed(BOT_LOCATION, FROM)
        else:
            line_speed, angle_speed = cal_speed(BOT_LOCATION, TO)

        sys.stdout.write('forward %d %d\n' % (0, line_speed))
        sys.stdout.write('rotate %d %f\n' % (0, angle_speed))
        finish()
