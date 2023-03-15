import math


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

    # M = 50 # 力矩
    # bot_rho = 20 # bot密度

    # # bot半径
    # if is_carry == 0:
    #     bot_radius = 0.45
    # else:
    #     bot_radius = 0.53
    #
    # # bot质量
    # bot_quality = pi * bot_radius**2 * bot_rho
    #
    # # 角加速度
    # alpha = M / (bot_quality * bot_radius**2)

# def cal_forward_speed()


if __name__ == '__main__':
    print(cal_angel(0, 0, 0.785398, 1, 1))