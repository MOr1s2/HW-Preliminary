#!/bin/bash
import sys
import math
import numpy as np

BOT = {}  # key:机器人ID  value:(0:工作台ID,1:携带物品类型,2:时间系数,3:碰撞系数,4:角速度,5:线速度x,6:线速度y,7:朝向,8:坐标x,9:坐标y)
WORKBENCH = {}  # key:工作台ID  value:(0:工作台类型,1:坐标x,2:坐标y,3:剩余生产时间,4:原材料格状态,5:产品格状态)
TARGET_WB = [-1] * 4 # 每个机器人到达一个目标工作台应把对应下标的TARGET_WB的值设为-1
CONDITIONAL_TARGET_WB = {1:[4,5,9], 2:[4,6,9], 3:[5,6,9], 4:[7,9], 5:[7,9], 6:[7,9], 7:[8,9]}
WORKBENCH_TYPE2ID = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[]}
ITEM_NEEDED_BY_WB = {4:[1,2], 5:[1,3], 6:[2,3]}
#WORKBENCH = {}  # key:工作台ID  value:(0:工作台类型,1:坐标x,2:坐标y,3:剩余生产时间,4:原材料格状态,5:产品格状态)

UNIT_LEN = 0.5
MAX_FORWARD_SPEED = 6.0
MAX_BACKWARD_SPEED = -2.0
MAX_ROTATE_SPEED = math.pi
MAX_TRACTION = 250
MAX_TORQUE = 50

flag = 0

def Dispatch_init(workbenchs):
    for key in workbenchs.keys():
        WORKBENCH_TYPE2ID[workbenchs[key][0]] += key
def Dispatch_greedy(bots, bots_id):  # 该函数调用于初始时，以及每次到达一个目标工作台执行完买卖操作后
    """
    :param bots: 所有机器人的状态信息，参考上面定义的BOT全局变量的结构
    :param bots_id: 需要寻找新目标的所有机器人ID
    :return: 无返回，所有结果在全局变量TARGET_WB中
    """
    # ret = {}
    type_7_wb = WORKBENCH_TYPE2ID[7]
    num_item_456 = [0, 0, 0]
    for wb in type_7_wb:
        if ((wb[4] >> 4) & 1 == 1):
            num_item_456[0] += 1
        if ((wb[4] >> 5 & 1) == 1):
            num_item_456[1] += 1
        if ((wb[4] >> 6 & 1) == 1):
            num_item_456[2] += 1
    min_item = num_item_456[0]
    min_item_id = 4
    while(min_item_id <= 6):
        if(num_item_456[min_item_id - 4] < min_item):
            min_item_id -= 4
            min_item = num_item_456[min_item_id]
        min_item_id += 1

    for bot_key in bots_id:
        Is_bot_has_item = 0
        if(bots[bot_key][1] > 0):
            Is_bot_has_item = 1
            option_wb_type = CONDITIONAL_TARGET_WB[bots[bot_key][1]]
            if(4 in option_wb_type or 5 in option_wb_type or 6 in option_wb_type):
                if (min_item_id != option_wb_type[0]):
                    option_wb_type = [option_wb_type[1]] + [option_wb_type[0]] + [option_wb_type[2]]
        else:
            option_wb_type = ITEM_NEEDED_BY_WB[min_item_id] + [min_item_id] + [7] #4，5，6类型的工作台中只有一个可供选择，可能会有bug

        option_wb_id = -1
        dist = 1e18
        for type in option_wb_type:
            if (type == 9 and option_wb_id != -1):
                break
            temp_wb_ids = WORKBENCH_TYPE2ID[type]
            for temp_wb_id in temp_wb_ids:
                if (temp_wb_id in TARGET_WB):
                    continue
                if (((Is_bot_has_item == 1) and ((WORKBENCH[temp_wb_id][4] >> bots[bot_key][
                    1]) & 1 == 0)) or (Is_bot_has_item == 0 and WORKBENCH[temp_wb_id][5] == 1)):  # temp_wb_id 这个工作台上 bots[bot_key][1] 类型的物品格是空的，即可以到该工作台放机器人手中的物品
                    dist_now = (WORKBENCH[temp_wb_id][1] - bots[bot_key][8]) ** 2 + (
                            WORKBENCH[temp_wb_id][2] - bots[bot_key][9]) ** 2
                    if (dist_now < dist):  # 暂时只考虑有空位放置的工作台中距离最短的那个，之后可以进一步考虑物品栏满的工作台的剩余时间
                        option_wb_id = temp_wb_id
                        dist = dist_now
        TARGET_WB[bot_key] = option_wb_id
    return

def Dispatch(workbenchs):
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
    # print(h_route, h_length)
    ret = [-1] * length
    for idx in range(length):
        ret[h_route[idx][0]] = h_route[(idx + 1) % length][0]
    return ret

def lookfor_start_loc(bots, workbenchs):# 传入参数分别是BOT字典，WORKBENCH字典
    ret = [0] * len(bots)   # ret的索引是BOT的ID，对应的值是初始要切入H圈所选择的工作台ID
    for key in bots.keys:
        if(bots[key][0] != -1):
            ret[key] = bots[key][0]
        else:
            min = 1e18
            for key_2 in workbenchs.keys():
                if(workbenchs[key_2][0] in (1,2,3)):
                    temp = (workbenchs[key_2][1] - bots[key][8])**2 + (workbenchs[key_2][2] - bots[key][9])**2
                    if(temp < min):
                        min = temp
                        ret[key] = key_2
    return ret

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
        h_route = Dispatch(WORKBENCH)
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
