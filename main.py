#!/bin/bash
import sys
import math
import numpy as np

BOT = {}  # key:机器人ID  value:[0:工作台ID,1:携带物品类型,2:时间系数,3:碰撞系数,4:角速度,5:线速度x,6:线速度y,7:朝向,8:坐标x,9:坐标y]
WORKBENCH = {}  # key:工作台ID  value:[0:工作台类型,1:坐标x,2:坐标y,3:剩余生产时间,4:原材料格状态,5:产品格状态]
TARGET_WB = [-1] * 4  # 每个机器人到达一个目标工作台应把对应下标的TARGET_WB的值设为-1
CONDITIONAL_TARGET_WB = {1: [4, 5, 9], 2: [4, 6, 9], 3: [5, 6, 9], 4: [7, 9], 5: [7, 9], 6: [7, 9], 7: [8, 9]}
WORKBENCH_TYPE2ID = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
ITEM_NEEDED_BY_WB = {4: [1, 2], 5: [1, 3], 6: [2, 3]}
BOT_GUIDING = [-1] * 8
SELECT_456 = 0
ITEM2SCORE = [3000, 3200, 3400, 7100, 7800, 8300, 29000]

UNIT_LEN = 0.5
MAX_FORWARD_SPEED = 6.0
MAX_BACKWARD_SPEED = -2.0
MAX_ROTATE_SPEED = math.pi

MIN_ANGLE = math.pi / 21
COFFS = np.polyfit([MIN_ANGLE, math.pi], [4, MAX_FORWARD_SPEED], 2)
MAX_FRAME = 8800
MAX_FRAME_SPEED = 0
COLLISION_COFF = 3
COLLISION_ANGLE = math.radians(150)
COLLISION_ANGLE_METHOD = 'abs'
WALL_DIST = 1.6
WALL_ANGLE = math.radians(20)
WALL_SPEED = 0

MAP_1234 = [0, 0, 0, 0]


def cal_rotate_speed(ori, x_b2w, y_b2w):
    b2w = np.array((x_b2w, y_b2w))
    v = np.array((math.cos(ori), math.sin(ori)))
    angle = np.arctan2(np.cross(v, b2w), np.dot(v, b2w))
    if abs(angle) < MIN_ANGLE:
        return 0, MAX_FORWARD_SPEED
    else:
        _speed = COFFS[0] * abs(angle) * abs(angle) + COFFS[1] * abs(angle) + COFFS[2]
        if angle > 0:
            return MAX_ROTATE_SPEED, _speed
        else:
            return -MAX_ROTATE_SPEED, _speed


def cal_angle_vector(ori, vec):
    vec_ori = [math.cos(ori), math.sin(ori)]
    vector_prod = vec_ori[0] * vec[0] + vec_ori[1] * vec[1]
    length_prod = math.sqrt(vec_ori[0] ** 2 + vec_ori[1] ** 2) * math.sqrt(vec[0] ** 2 + vec[1] ** 2)
    cos = vector_prod * 1.0 / (length_prod * 1.0 + 1e-8)
    angle = math.acos(cos)
    return angle


def is_collision(bot_id, method='abs'):
    flag = False
    for _i in range(4):
        if _i == bot_id:
            continue
        x_b2b = BOT[_i][8] - BOT[bot_id][8]
        y_b2b = BOT[_i][9] - BOT[bot_id][9]
        r = 0.9 + 0.08 * (bool(BOT[_i][1]) + bool(BOT[bot_id][1]))
        dist = x_b2b ** 2 + y_b2b ** 2
        if method == 'abs':
            ori = abs(BOT[_i][7] - BOT[bot_id][7])
        else:
            ori = cal_angle_vector(BOT[_i][7], [math.cos(BOT[bot_id][7]), math.sin(BOT[bot_id][7])])
        if dist < r * r * COLLISION_COFF and ori > COLLISION_ANGLE:
            flag = True
            b2w = np.array((x_b2b, y_b2b))
            v = np.array((math.cos(BOT[_i][7]), math.sin(BOT[_i][7])))
            angle = np.arctan2(np.cross(v, b2w), np.dot(v, b2w))
            if BOT[_i][7] * BOT[bot_id][7] > 0:
                if angle > 0:
                    sys.stdout.write('rotate %d %f\n' % (_i, MAX_ROTATE_SPEED))
                    sys.stdout.write('rotate %d %f\n' % (bot_id, -MAX_ROTATE_SPEED))
                else:
                    sys.stdout.write('rotate %d %f\n' % (_i, -MAX_ROTATE_SPEED))
                    sys.stdout.write('rotate %d %f\n' % (bot_id, MAX_ROTATE_SPEED))
            else:
                if angle > 0:
                    sys.stdout.write('rotate %d %f\n' % (_i, MAX_ROTATE_SPEED))
                    sys.stdout.write('rotate %d %f\n' % (bot_id, MAX_ROTATE_SPEED))
                else:
                    sys.stdout.write('rotate %d %f\n' % (_i, -MAX_ROTATE_SPEED))
                    sys.stdout.write('rotate %d %f\n' % (bot_id, -MAX_ROTATE_SPEED))
            sys.stdout.write('forward %d %f\n' % (bot_id, MAX_FORWARD_SPEED))
    if flag:
        return True
    else:
        return False


def is_hit_wall(bot_id, bench_id):
    x_b2w = WORKBENCH[bench_id][1] - BOT[bot_id][8]
    y_b2w = WORKBENCH[bench_id][2] - BOT[bot_id][9]
    ori = BOT[bot_id][7]
    if (BOT[bot_id][8] < WALL_DIST or BOT[bot_id][9] < WALL_DIST
        or BOT[bot_id][8] > 50 - WALL_DIST or BOT[bot_id][9] > 50 - WALL_DIST) \
            and (cal_angle_vector(ori, [x_b2w, y_b2w])) > WALL_ANGLE:
        b2w = np.array((x_b2w, y_b2w))
        v = np.array((math.cos(ori), math.sin(ori)))
        angle = np.arctan2(np.cross(v, b2w), np.dot(v, b2w))
        _speed = 0
        if angle > 0:
            _rotate = MAX_ROTATE_SPEED
        else:
            _rotate = -MAX_ROTATE_SPEED
        sys.stdout.write('forward %d %f\n' % (bot_id, _speed))
        sys.stdout.write('rotate %d %f\n' % (bot_id, _rotate))
        return True
    else:
        return False


def init_dispatch(workbenchs):
    for key in workbenchs.keys():
        WORKBENCH_TYPE2ID[workbenchs[key][0]] += [key]


def dispatch(frame_id, bots, bots_id, reject_wb_id, wb_id=[]):  # 该函数调用于初始时，以及每次到达一个目标工作台执行完买卖操作后
    """
    :param bots: 所有机器人的状态信息，参考上面定义的BOT全局变量的结构
    :param bots_id: 需要寻找新目标的机器人ID
    :return: 无返回，所有结果在全局变量TARGET_WB中
    """

    global SELECT_456
    bot_key = bots_id
    option_wb_id = -1
    option_wb_id_1 = -1
    option_wb_id_2 = -1
    material_status = -1
    dist = 1e18
    dist_1 = 1e18
    dist_2 = 1e18
    award = 0

    if bots[bot_key][1] > 0 and wb_id != []:
        for temp_wb_id in wb_id:
            if WORKBENCH[temp_wb_id][0] in [4, 5, 6, 7] and MAP_1234[0] == 1:
                if WORKBENCH[temp_wb_id][4] > material_status:
                    option_wb_id = temp_wb_id
                    material_status = WORKBENCH[temp_wb_id][4]
            elif MAP_1234[2] == 1 and frame_id >= 6000:
                if WORKBENCH[temp_wb_id][5] == 1:
                    dist_now = (WORKBENCH[temp_wb_id][1] - bots[bot_key][8]) ** 2 + (
                            WORKBENCH[temp_wb_id][2] - bots[bot_key][9]) ** 2
                    if dist_now < dist_1:
                        option_wb_id_1 = temp_wb_id
                        dist_1 = dist_now
                else:
                    dist_now = (WORKBENCH[temp_wb_id][1] - bots[bot_key][8]) ** 2 + (
                            WORKBENCH[temp_wb_id][2] - bots[bot_key][9]) ** 2
                    if dist_now < dist_2:
                        option_wb_id_2 = temp_wb_id
                        dist_2 = dist_now
            else:
                dist_now = (WORKBENCH[temp_wb_id][1] - bots[bot_key][8]) ** 2 + (
                        WORKBENCH[temp_wb_id][2] - bots[bot_key][9]) ** 2
                if dist_now < dist:  # 暂时只考虑有空位放置的工作台中距离最短的那个，之后可以进一步考虑物品栏满的工作台的剩余时间
                    option_wb_id = temp_wb_id
                    dist = dist_now
        if option_wb_id_1 != -1:
            option_wb_id = option_wb_id_1
        elif option_wb_id_2 != -1:
            option_wb_id = option_wb_id_2
        TARGET_WB[bot_key] = option_wb_id
        return

    elif bots[bot_key][1] > 0:  # BOT手上有东西 且 已经在路上
        option_wb_type = ITEM_NEEDED_BY_WB[BOT_GUIDING[bot_key * 2]] + [BOT_GUIDING[bot_key * 2]] + [
            7]
        option_wb_type = list(set(option_wb_type) & set(CONDITIONAL_TARGET_WB[bots[bot_key][1]]))
    else:  # BOT 手上没东西（包括刚从上一个到达的工作台出发 和 已经在路上）
        if reject_wb_id != -1:# and (MAP_1234[0] == 0 or (MAP_1234[0] == 1 and i == 3)):# and MAP_1234[2] == 0:
            while BOT_GUIDING[bot_key * 2] == SELECT_456 % 3 + 4:
                SELECT_456 += 1
            BOT_GUIDING[bot_key * 2] = SELECT_456 % 3 + 4
            SELECT_456 += 1
            BOT_GUIDING[bot_key * 2 + 1] = ITEM_NEEDED_BY_WB[BOT_GUIDING[bot_key * 2]][0]
            option_wb_type = ITEM_NEEDED_BY_WB[BOT_GUIDING[bot_key * 2]] + [BOT_GUIDING[bot_key * 2]] + [
                7]
        else:
            option_wb_type = ITEM_NEEDED_BY_WB[BOT_GUIDING[bot_key * 2]] + [BOT_GUIDING[bot_key * 2]] + [
                7]
        if BOT_GUIDING[bot_key * 2 + 1] != option_wb_type[0]:
            option_wb_type = option_wb_type[1::-1] + option_wb_type[2::]

        guiding_wb_ids = WORKBENCH_TYPE2ID[BOT_GUIDING[bot_key * 2]]
        for item_type in [BOT_GUIDING[bot_key * 2 + 1]]:  # ITEM_NEEDED_BY_WB[BOT_GUIDING[bot_key * 2]]:
            num = 0
            for guiding_wb_id in guiding_wb_ids:
                if (WORKBENCH[guiding_wb_id][4] >> item_type) & 1 == 1:
                    num += 1
            if num == len(guiding_wb_ids):
                option_wb_type.remove(item_type)

    for wb_type in option_wb_type:  # 除了从工作台成功购买产品并开始新的送货目标外，其余情况均遵循一下逻辑进行调度。
        if option_wb_id != -1:
            if frame_id < 6000:
                break
            elif wb_type == 9:
                break
        temp_wb_ids = WORKBENCH_TYPE2ID[wb_type]
        for temp_wb_id in temp_wb_ids:
            if temp_wb_id in TARGET_WB and temp_wb_id != TARGET_WB[bot_key] and WORKBENCH[temp_wb_id][0] not in [1, 2, 3, 8, 9]:
                ii = 0  # 这里面的判断逻辑是判断有没有跟其他机器人的选择目标重了（但是如果两个机器人分别给同一个7号工作台送4，5的话，这不算重）
                is_continue = 0  # 注意：这里的逻辑一开始只是为当机器人手上有原材料时考虑的，单纯去取货的没考虑。不过目前来看这逻辑对于后者好像也没问题
                while ii <= 3:
                    if TARGET_WB[ii] == temp_wb_id:
                        if BOT[ii][1] == BOT[bot_key][1]:
                            is_continue = 1
                            break
                    ii += 1
                if is_continue == 1:
                    continue
            if temp_wb_id == reject_wb_id:
                continue
            if ((bots[bot_key][1] > 0) and ((WORKBENCH[temp_wb_id][4] >> bots[bot_key][
                1]) & 1 == 0)) or (bots[bot_key][1] == 0 and (WORKBENCH[temp_wb_id][
                5] == 1 or WORKBENCH[temp_wb_id][0] in [1, 2, 3])):  # temp_wb_id 这个工作台上 bots[bot_key][1] 类型的物品格是空的，即可以到该工作台放机器人手中的物品
                if bots[bot_key][1] == 0:
                    dist_now = (WORKBENCH[temp_wb_id][1] - bots[bot_key][8]) ** 2 + (
                            WORKBENCH[temp_wb_id][2] - bots[bot_key][9]) ** 2
                    if frame_id >= 6000:
                        if dist_now == 0:
                            dist_now = 0.1
                        award_now = ITEM2SCORE[WORKBENCH[temp_wb_id][0] - 1] / dist_now
                        if award_now > award:
                            option_wb_id = temp_wb_id
                            award = award_now
                    else:
                        if dist_now < dist:  # 暂时只考虑有空位放置的工作台中距离最短的那个，之后可以进一步考虑物品栏满的工作台的剩余时间
                            option_wb_id = temp_wb_id
                            dist = dist_now
                else:
                    if WORKBENCH[temp_wb_id][0] in [4, 5, 6, 7] and MAP_1234[0] == 1:
                        if WORKBENCH[temp_wb_id][4] > material_status:
                            option_wb_id = temp_wb_id
                            material_status = WORKBENCH[temp_wb_id][4]
                    elif MAP_1234[2] == 1 and frame_id >= 6000:
                        if WORKBENCH[temp_wb_id][5] == 1:
                            dist_now = (WORKBENCH[temp_wb_id][1] - bots[bot_key][8]) ** 2 + (
                                    WORKBENCH[temp_wb_id][2] - bots[bot_key][9]) ** 2
                            if dist_now < dist_1:
                                option_wb_id_1 = temp_wb_id
                                dist_1 = dist_now
                        else:
                            dist_now = (WORKBENCH[temp_wb_id][1] - bots[bot_key][8]) ** 2 + (
                                    WORKBENCH[temp_wb_id][2] - bots[bot_key][9]) ** 2
                            if dist_now < dist_2:
                                option_wb_id_2 = temp_wb_id
                                dist_2 = dist_now
                    else:
                        dist_now = (WORKBENCH[temp_wb_id][1] - bots[bot_key][8]) ** 2 + (
                                WORKBENCH[temp_wb_id][2] - bots[bot_key][9]) ** 2
                        if dist_now < dist:  # 暂时只考虑有空位放置的工作台中距离最短的那个，之后可以进一步考虑物品栏满的工作台的剩余时间
                            option_wb_id = temp_wb_id
                            dist = dist_now
    if option_wb_id_1 != -1:
        option_wb_id = option_wb_id_1
    elif option_wb_id_2 != -1:
        option_wb_id = option_wb_id_2
    if option_wb_id != -1:
        TARGET_WB[bot_key] = option_wb_id
        if MAP_1234[0] == 1 and WORKBENCH[option_wb_id][0] in [1, 2, 3]:
            if WORKBENCH[option_wb_id][0] != BOT_GUIDING[bot_key * 2 + 1]:
                BOT_GUIDING[bot_key * 2 + 1] = \
                    list(set(ITEM_NEEDED_BY_WB[BOT_GUIDING[bot_key * 2]]) - set([BOT_GUIDING[bot_key * 2 + 1]]))[
                        0]  # 3.24 17:32 add
    return


def init_util_ok():
    global SELECT_456
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
                    if int(c) in [1, 2, 3]:
                        WORKBENCH.update({bench_id: [int(c), x, y, -1, 0, 1]})
                    else:
                        WORKBENCH.update({bench_id: [int(c), x, y, -1, 0, 0]})
                    bench_id += 1
            count += 1
        _line = input()

    init_dispatch(WORKBENCH)
    for _i in range(4):
        BOT_GUIDING[_i * 2] = SELECT_456 % 3 + 4
        BOT_GUIDING[_i * 2 + 1] = ITEM_NEEDED_BY_WB[BOT_GUIDING[_i * 2]][0]
        SELECT_456 += 1
    for _i in range(4):
        dispatch(0, BOT, _i, -1)
    if len(WORKBENCH) == 43:
        MAP_1234[0] = 1
        BOT_GUIDING[0] = 4
        BOT_GUIDING[2] = 5
        BOT_GUIDING[4] = 6
        BOT_GUIDING[1] = 1
        BOT_GUIDING[3] = 3
        BOT_GUIDING[5] = 2
        BOT_GUIDING[7] = 2
    elif len(WORKBENCH) == 25:
        MAP_1234[1] = 1
    elif len(WORKBENCH) == 50:
        MAP_1234[2] = 1
    else:
        MAP_1234[3] = 1


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


def buy(bot_id, wb_id): # 当前机器人id，所处工作台id
    optional_wb_ids = []
    reject_wb_id = -1
    if WORKBENCH[wb_id][0] not in [4, 5, 6, 7]:
        workbench_types = [BOT_GUIDING[bot_id * 2]]
    else:
        workbench_types = CONDITIONAL_TARGET_WB[WORKBENCH[wb_id][0]]
    for workbench_type in workbench_types:
        optional_wb_ids += WORKBENCH_TYPE2ID[workbench_type]
    temp_optional_wb_ids = []
    for optional_wb_id in optional_wb_ids:
        temp_optional_wb_ids.append(optional_wb_id)
    for optional_wb_id in temp_optional_wb_ids:
        if (WORKBENCH[optional_wb_id][4] >> WORKBENCH[wb_id][0]) & 1 == 1:
            optional_wb_ids.remove(optional_wb_id)
        elif optional_wb_id in TARGET_WB and WORKBENCH[optional_wb_id][0] not in [8, 9]:
            ii = 0
            while ii <= 3:
                if TARGET_WB[ii] == optional_wb_id:
                    if BOT[ii][1] == WORKBENCH[wb_id][0]:
                        optional_wb_ids.remove(optional_wb_id)
                        break
                ii += 1
    if optional_wb_ids:
        if frame_id < MAX_FRAME:
            sys.stdout.write('buy %d\n' % bot_id)
            BOT[bot_id][1] = WORKBENCH[wb_id][0]
            WORKBENCH[wb_id][5] = 0
    else:
        reject_wb_id = wb_id
    return optional_wb_ids, reject_wb_id


def sell(bot_id, wb_id):
    if BOT[bot_id][1] > 0:
        if (WORKBENCH[wb_id][0] in CONDITIONAL_TARGET_WB[BOT[bot_id][1]] and (
                (WORKBENCH[wb_id][4] >> BOT[bot_id][1]) & 1 == 0)):
            sys.stdout.write('sell %d\n' % bot_id)
            WORKBENCH[wb_id][4] += (2 ** BOT[bot_id][1])
            BOT[bot_id][1] = 0


if __name__ == '__main__':
    init_util_ok()
    finish()

    map_id = MAP_1234.index(1)
    if map_id == 0:
        pass
    elif map_id == 1:
        COLLISION_ANGLE_METHOD = 'vec'
        COLLISION_ANGLE = math.radians(90)
        WALL_DIST = 1.96
        WALL_SPEED = -0.1
    elif map_id == 2:
        MAX_FRAME_SPEED = 2
        COLLISION_ANGLE_METHOD = 'vec'
        COLLISION_ANGLE = math.radians(130)
        WALL_ANGLE = math.radians(25)
    else:
        COLLISION_COFF = 3.1

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
            if frame_id > MAX_FRAME and BOT[i][1] == 0:
                sys.stdout.write('rotate %d %f\n' % (i, 0))
                sys.stdout.write('forward %d %f\n' % (i, MAX_FRAME_SPEED))
                continue
            k = TARGET_WB[i]
            if k == -1:
                dispatch(frame_id, BOT, i, -1)
                continue

            if is_collision(i, COLLISION_ANGLE_METHOD):
                pass
            else:
                if is_hit_wall(i, k):
                    pass
                else:
                    (rotate, speed) = cal_rotate_speed(BOT[i][7], WORKBENCH[k][1] - BOT[i][8],
                                                       WORKBENCH[k][2] - BOT[i][9])
                    sys.stdout.write('rotate %d %f\n' % (i, rotate))
                    sys.stdout.write('forward %d %f\n' % (i, speed))

            j = BOT[i][0]  # j表示机器人当前处于工作台的id，不在任何一个工作台则为-1
            optional_wb_ids = []
            reject_wb_id = -1
            if j > -1 and j == TARGET_WB[i]:

                if BOT[i][1] > 0:   # 卖
                    sell(i, j)
                if BOT[i][1] == 0 and WORKBENCH[j][5] == 1:  # 买
                    optional_wb_ids, reject_wb_id = buy(i, j)
                else:   # 到达的工作台有产品可买，但当前选择的目标工作台类型的任意一个工作台均不能接收它，因此需要及时切换目标工作台类型
                    if WORKBENCH[j][0] in [7, 8, 9]:# and (MAP_1234[0] == 0 or (MAP_1234[0] == 1 and i == 3)):# and MAP_1234[2] == 0:
                        while BOT_GUIDING[i * 2] == SELECT_456 % 3 + 4:
                            SELECT_456 += 1
                        BOT_GUIDING[i * 2] = SELECT_456 % 3 + 4
                        SELECT_456 += 1
                        BOT_GUIDING[i * 2 + 1] = \
                            list(set(ITEM_NEEDED_BY_WB[BOT_GUIDING[i * 2]]) - set([BOT_GUIDING[i * 2 + 1]]))[0]
                    elif WORKBENCH[j][0] in [4, 5, 6]:
                        BOT_GUIDING[i * 2 + 1] = \
                            list(set(ITEM_NEEDED_BY_WB[BOT_GUIDING[i * 2]]) - set([BOT_GUIDING[i * 2 + 1]]))[0]
            dispatch(frame_id, BOT, i, reject_wb_id, optional_wb_ids)
        finish()
