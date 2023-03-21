#!/bin/bash
import sys
import math

import numpy as np

BOT = {}    # key:机器人ID  value:[0:工作台ID,1:携带物品类型,2:时间系数,3:碰撞系数,4:角速度,5:线速度x,6:线速度y,7:朝向,8:坐标x,9:坐标y]
WORKBENCH = {}    # key:工作台ID  value:[0:工作台类型,1:坐标x,2:坐标y,3:剩余生产时间,4:原材料格状态,5:产品格状态]
ITEM2BENCH = []    # i:机器人携带物品类型  ITEM2BENCH[i]:回收当前物品的工作台ID
NEXT_BENCH_ID = [-1] * 4    # i:机器人ID  NEXT_BENCH_ID[i]:机器人i需要前往的工作台编号

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
    """
    根据机器人的朝向和坐标以及工作台的坐标计算机器人应有的旋转速度
    :param ori: 机器人的朝向
    :param x_b2w: 工作台与机器人连线向量的x坐标
    :param y_b2w: 工作台与机器人连线向量的y坐标
    :return: 机器人的旋转角度 pi/-pi
    """
    b2w = np.array((x_b2w, y_b2w))
    v = np.array((math.cos(ori), math.sin(ori)))    # 将朝向转化为单位向量
    angle = np.arctan2(np.cross(v, b2w), np.dot(v, b2w))

    if abs(angle) < math.pi / 20:
        return 0
    else:
        if angle > 0:
            return MAX_ROTATE_SPEED
        else:
            return -MAX_ROTATE_SPEED


def item2bench(bench_id, bench_type):
    """
    建立机器人携带物体类型到工作台编号的映射类型，即ITEM2BENCH[i]为携带物品类型为i时可以前往的工作台编号，i=0时对应所有可以生产产品的工作台
    :param bench_id: 工作台ID
    :param bench_type: 工作台类型，1-7同时表示能合成的物品类型
    :return: 更新全局变量ITEM2BENCH
    """
    for _ in range(8):
        ITEM2BENCH.append([])
    if bench_type == 4:
        ITEM2BENCH[0].append(bench_id)
        ITEM2BENCH[1].append(bench_id)
        ITEM2BENCH[2].append(bench_id)
    elif bench_type == 5:
        ITEM2BENCH[0].append(bench_id)
        ITEM2BENCH[1].append(bench_id)
        ITEM2BENCH[3].append(bench_id)
    elif bench_type == 6:
        ITEM2BENCH[0].append(bench_id)
        ITEM2BENCH[2].append(bench_id)
        ITEM2BENCH[3].append(bench_id)
    elif bench_type == 7:
        ITEM2BENCH[0].append(bench_id)
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
    """
    获得ID为bot_id的机器人应该前往的工作台ID
    :param bot_id: 机器人ID
    :return: ID为bot_id的机器人应该前往的工作台ID
    """
    _item = BOT[bot_id][1]    # 机器人所携带的物品类型
    bench_ids = ITEM2BENCH[_item]    # 机器人携带当前物品类型时可以前往的工作台ID
    x_bot, y_bot = BOT[bot_id][8], BOT[bot_id][9]    # 机器人当前的坐标

    min_dist = 5e3
    next_bench_id = -1    # 如果当前不存在机器人可以前往的工作台，即设为-1
    for bench_id in bench_ids:
        if _item != 0:    # 如果机器人携带有原材料，但工作台当前对应原材料格已满（1）或不收当前原材料（-1），则跳过
            _material = get_material(bench_id)
            if _material[_item] == 1 or _material[_item] == -1:
                continue
        if _item == 0 and WORKBENCH[bench_id][5] == 0:    # 如果机器人不携带原材料，但工作台当前也没有成品，则跳过
            continue
        if _item == 0 and WORKBENCH[bench_id][5] == 1:    # 如果机器人不携带原材料，工作台当前有成品，但携带成品时机器人不存在可以前往的工作台，则跳过
            flag = 0
            _i = WORKBENCH[bench_id][0]
            for _b in ITEM2BENCH[_i]:
                _m = get_material(_b)
                if _m[_i] == 0:
                    flag = 1
            if flag == 0:
                continue

        x_bench, y_bench = WORKBENCH[bench_id][1], WORKBENCH[bench_id][2]    # 根据距离最短来选择应该前往的工作台
        dist = (x_bench - x_bot) ** 2 + (y_bench - y_bot) ** 2
        if dist < min_dist:
            next_bench_id = bench_id
            min_dist = dist
    return next_bench_id


def get_material(bench_id):
    """
    获得ID为bench_id当前所对应的原材料格状态列表，其中下标为物品类型，值为原材料格状态，-1为不收当前原材料，0为收且未收，1为收但已收
    :param bench_id: 工作台ID
    :return:ID为bench_id当所对应的原材料格状态列表
    """
    if WORKBENCH[bench_id][0] in [1, 2, 3]:    # 类型为1、2、3时不收购原材料
        return [-1] * 8
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

    d2b = bin(WORKBENCH[bench_id][4])    # 获得工作台当前的原材料格状态（十进制），并将其转化为二进制
    for _i in range(len(d2b) - 2):    # 忽略二进制开头的0b
        if _material[_i] != -1:    # 判断是否收购当前原材料类型
            _material[_i] = int(d2b[-_i - 1])    # 将d2b的下标-1,-2,-3,...对应为_material的下标0,1,2,...
    return _material


def init_util_ok():
    """
    根据地图初始化全局变量BOT和WORKBENCH，主要获得其位置，并获得ITEM2BENCH和NEXT_BENCH_ID
    :return: 初始化全局变量BOT和WORKBENCH，获得ITEM2BENCH和NEXT_BENCH_ID
    """
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
    for _i in range(4):
        NEXT_BENCH_ID[_i] = get_next_bench(_i)


def read_workbench(_k):
    """
    用于每一帧读取工作台信息以更新全局变量WORKBENCH
    :param _k: 工作台的数量，即需要读取的行数
    :return: 更新全局变量WORKBENCH
    """
    for _i in range(_k):
        _parts = input().split(' ')
        WORKBENCH.update({_i: [int(_parts[0]), float(_parts[1]), float(_parts[2]),
                               int(_parts[3]), int(_parts[4]), int(_parts[5])]})


def read_bot():
    """
    用于每一帧读取机器人信息以更新全局变量BOT
    :return: 更新全局变量BOT
    """
    for _i in range(4):
        _parts = input().split(' ')
        BOT.update({_i: [int(_parts[0]), int(_parts[1]), float(_parts[2]), float(_parts[3]), float(_parts[4]),
                         float(_parts[5]), float(_parts[6]), float(_parts[7]), float(_parts[8]), float(_parts[9])]})


def finish():
    """
    输出OK以示结束
    """
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
        frame_id = int(parts[0])    # 帧ID
        money = int(parts[1])    # 当前所拥有的资金

        line = input()
        k = int(line)    # 工作台数量

        read_workbench(k)
        read_bot()

        if input() != 'OK':
            break

        sys.stdout.write('%d\n' % frame_id)

        for i in range(4):
            j = NEXT_BENCH_ID[i]    # 获得当前机器人所应该前往的工作台ID
            if j == -1:    # 如果机器人无法找到当前所应该前往的工作台，则更新NEXT_BENCH_ID，同时跳过这一帧以避免数组越界
                for _ in range(4):
                    NEXT_BENCH_ID[_] = get_next_bench(_)
                continue
            rotate = cal_rotate(BOT[i][7], WORKBENCH[j][1] - BOT[i][8], WORKBENCH[j][2] - BOT[i][9])
            sys.stdout.write('rotate %d %f\n' % (i, rotate))

            if rotate == 0:
                speed = MAX_FORWARD_SPEED
            else:    # 旋转时设置较小的前进速度以避免公转
                speed = MAX_FORWARD_SPEED / 2
            # if BOT[i][8] < 0.5 or BOT[i][9] < 0.5 or BOT[i][8] > 49.5 or BOT[i][9] > 49.5:
            #     speed = MAX_BACKWARD_SPEED
            sys.stdout.write('forward %d %f\n' % (i, speed))

            if BOT[i][0] == j:    # 判断是否到达应该前往的工作台ID
                item = BOT[i][1]    # 机器人所携带物品类型
                material = get_material(j)    # 工作台所对应的原材料格状态，以列表表示，下标与物品类型对应
                if material[item] == 0:    # 机器人携带原材料，且工作台可以收够当前原材料
                    sys.stdout.write('sell %d\n' % i)
                    BOT[i][1] = 0    # 实时更新机器人携带材料的状态
                    WORKBENCH[j][4] += (2 ** item)    # 实时更新工作台原材料格的状态
                    for _ in range(4):
                        NEXT_BENCH_ID[_] = get_next_bench(_)    # 状态存在变化，故更新NEXT_BENCH_ID
                    continue
                if BOT[i][1] == 0 and WORKBENCH[j][5] == 1:    # 机器人不携带原材料，且工作台存在成品
                    sys.stdout.write('buy %d\n' % i)
                    BOT[i][1] = WORKBENCH[j][0]    # 实时更新机器人携带材料的状态
                    WORKBENCH[j][5] = 0    # 实时更新工作台产品格的状态
                    for _ in range(4):
                        NEXT_BENCH_ID[_] = get_next_bench(_)    # 状态存在变化，故更新NEXT_BENCH_ID
        finish()
