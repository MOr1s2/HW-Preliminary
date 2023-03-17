import math
import numpy as np
WORCHBENCH = {0: (1, 0.0, 3.0, 0, 0, 1), 1: (2, 1.0, 1.0, 0, 0, 1), 2: (3, 2.0, 2.0, 0, 0, 1), 3: (4, 3.0, 0.0, -1, 0, 0), 4: (5, 2.0, 4.0, 168, 0, 0), 5: (6, 3.0, 3.0, -1, 0, 0), 6: (7, 5.0, 2.0, -1, 0, 0), 7: (8, 5.0, 5.0, -1, 0, 0)}
BOT = {0: (-1, 0, 0.9657950401, 1.0, 0.0, 0.0, 0.0, -0.3755806088, 0.0, 4.0), 1: (-1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.006108176429, 1.0, 2.0), 2: (4, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 4.0), 3: (-1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 1.0)}

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
    for i in range(500):
        for j in range(length - 2):
            if (exchange == True):
                break
            for k in range(i + 2, length):
                if (exchange == True):
                    break
                if (dists[h_route[j][0]][h_route[k][0]] + dists[h_route[j + 1][0]][h_route[(k + 1) % length][0]] <
                        dists[h_route[j][0]][h_route[j + 1][0]] + dists[h_route[k][0]][h_route[(k + 1) % length][0]]):
                    h_route[j + 1: (k + 1)] = h_route[j + 1:(k + 1)][::-1]
                    exchange = True
        exchange = False
        h_length = 0
        old_h_length = -1e18
        for j in range(length):
            h_length += dists[h_route[j][0]][h_route[(j + 1) % length][0]]
        if (h_length <= old_h_length):
            break
        old_h_length = h_length
        ret = [-1] * length
        for idx in range(length):
            ret[h_route[idx][0]] = h_route[(idx + 1) % length][0]
    return ret

def lookfor_start_loc(bots, workbenchs):
    ret = [0] * len(bots)
    for key in bots.keys():
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

h_route = Dispatch(WORCHBENCH)
start_loc = lookfor_start_loc(BOT, WORCHBENCH)
print(start_loc)
# h_route, h_length = Dispatch(WORCHBENCH)
# print(h_route, h_length)
