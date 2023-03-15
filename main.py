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


# K 行数据，每一行表示一个工作台，（工作台类型  坐标 剩余生产时间（帧数） 原材料格状态 产品格状态）
def read_k_workbench(k):
    for i in range(k):
        parts = input().split(' ')
        WORKBENCH.update({(int(parts[0]), float(parts[1]), float(parts[2])):
                              (int(parts[3]), int(parts[4]), int(parts[5]))})


# 每一行表示一个机器人，(所处工作台ID  携带物品类型  时间价值系数  碰撞价值系数 角速度 线速度(x,y) 朝向 坐标(x,y))
def read_bot():
    for i in range(4):
        parts = input().split(' ')
        BOT.update({i: (int(parts[0]), int(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]),
                        float(parts[5]), float(parts[6]), float(parts[7]), float(parts[8]), float(parts[9]))})

    BOT_LOCATION = BOT[0][-2:]


def finish():
    sys.stdout.write('OK\n')
    sys.stdout.flush()


def cal_angel(x_bot, y_bot, ori, x_bench, y_bench):
    """
    计算bot前往指定工作台的旋转角度
    :param x_bot: bot坐标x
    :param y_bot: bot坐标y
    :param ori: bot朝向，弧度，范围[-π,π]
    :param x_bench: 工作台坐标x
    :param y_bench: 工作台坐标y
    :return: 将bot转向工作台需要旋转的角度，负数为顺时针，正数为逆时针
    """
    pi = 3.1415926
    if ori >= 0:
        pass
    else:
        ori = pi - ori
    A = (x_bench - x_bot, y_bench - y_bot)  # bot与目标点构成的向量
    B = (1, 0)  # x轴正方向单位向量
    beta = math.acos(A[0] / math.sqrt(A[0] ** 2 + A[1] ** 2))
    if A[0] * B[1] - A[1] * B[0] > 0:
        beta = 2 * pi - beta
    else:
        pass
    return beta - ori


def cal_rotate_speed(rotate_angel):
    """
    计算bot每一帧的旋转速度
    :param rotate_angel: bot需要旋转的角度
    :return: bot旋转速度
    """

    pi = 3.1415926
    if rotate_angel >= 0:
        return min(pi, 50 * rotate_angel)
    else:
        return max(-pi, 50 * rotate_angel)


if __name__ == '__main__':
    init_util_ok()
    finish()
    while True:
        # 第一行输入 2 个整数，表示帧序号（从 1 开始递增）、当前金钱数。
        line = sys.stdin.readline()
        if not line:
            break
        parts = line.split(' ')
        frame_id = int(parts[0])
        money = int(parts[1])

        # 第二行输入 1 个整数，表示场上工作台的数量 K（K<=50）。
        line = input()
        k = int(line)

        read_k_workbench(k)
        read_bot()

        list_work = list(WORKBENCH)

        if input() != 'OK':
            break

        sys.stdout.write('%d\n' % frame_id)

        # if flag == 0:
        #     line_speed, angle_speed = cal_speed(BOT_LOCATION, FROM)
        # else:
        #     line_speed, angle_speed = cal_speed(BOT_LOCATION, TO)

        if flag == 0:
            sys.stdout.write('forward %d %d\n' % (0, 6))
            sys.stdout.write('rotate %d %f\n' % (0, cal_rotate_speed(cal_angel(BOT[0][-2], BOT[0][-1],
                                                                        BOT[0][-3], 27.75, 48.75))))
            if BOT[0][0] != -1:
                sys.stdout.write('buy %d\n' % 0)
                flag = 1
        else:
            sys.stdout.write('rotate %d %f\n' % (0, cal_rotate_speed(cal_angel(BOT[0][-2], BOT[0][-1],
                                                                               BOT[0][-3], 13.25,34.25))))
            if BOT[0][0] != -1:
                sys.stdout.write('sell %d\n' % 0)
        finish()
