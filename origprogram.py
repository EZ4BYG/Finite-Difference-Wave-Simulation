import numpy as np
import math 
import datetime as dt
import copy

def write_into_file(u4,XN,ZN):
    print("数据写入文件开始:")
    ARRS = []
    f = open('testorignew.txt', 'w+')
    for i in range(XN):
        jointsFrame = u4[i]
        ARRS.append(jointsFrame)
        for ji in range(ZN):
            strNum = str(jointsFrame[ji])
            f.write(strNum)
            f.write(',')
        f.write('\n')
    f.close()
    print("-----波场快照数据写入完毕!-----")
# def write_into_file(u4,XN,ZN):
#     print("数据写入文件开始:")
#     #ARRS = []
#     f = open('testfenqu2.txt','w+')
#     for i in range(XN):
#         for j in range(ZN):
#             f.write(str(i))
#             f.write(',')
#             f.write(str(j))
#             f.write(',')
#             f.write(str(u4[i][j]))
#             f.write('\n')
#     f.close()
#     print("波长快照数据写入完毕!")
# def write_into_file(u4,XN,ZN):
#     print("数据写入文件开始:")
#     f = open('testorig.dat', 'wb')
#     for i in range(XN):
#         for j in range(ZN):
#             f.write(bytes(u4[i][j]))
#             #f.write('\r\n')
#     f.close()
#     print("写入完毕")


def finite_difference(XN,ZN,KN,u1,u2,u3,w,f,v,DT,DH,num):
    # XN ZN KN u1,u2,u3,w,f,v,DT,DH
    print("正在进行差分计算:")
    u4 = np.zeros([XN,ZN])
    for k in range(KN):
        for i in range(2,XN-2): # 这一轮i,j全部算完!才进入下面的更新循环
            for j in range(2,ZN-2):
                # 在一次i,j循环中,uu0 uu1 uu2是可以分开算的
                # 并行:每次k更新的时候u3需要更新过的uu0 uu1 uu2二维数组
                uu0 = (v[i][j]**2) * (DT/DH)**2
                uu1 = -1.0/12*(u2[i-2][j] + u2[i+2][j]) + \
                       4.0/3*(u2[i-1][j] + u2[i+1][j]) - \
                       5.0/2*u2[i][j]
                uu2 = -1.0/12*(u2[i][j-2] + u2[i][j+2]) + \
                       4.0/3*(u2[i][j-1] + u2[i][j+1]) - \
                       5.0/2*u2[i][j]
                u3[i][j] = 2*u2[i][j] - u1[i][j] + \
                           uu0*uu1 + uu0*uu2 + \
                           w[k]*f[i][j]

        u1 = copy.copy(u2)
        u2 = copy.copy(u3)
                    
        # 波场快照时间定在10时
        if k == num:
            u4 = copy.copy(u3)
        print("第%d次迭代完成"%(k+1), '还有%d次迭代'%(KN-k-1))

    print("-----有限差分迭代完毕!-----")
    return u4


def main():
    start = dt.datetime.now()
    E = math.e    # 自然对数e
    PI = math.pi  # 圆周率
    cos = math.cos
    FM = 60       # 基频
    R = 3         # 控制频带宽度的参数
    KN = 200      # 采样总次数
    XN = 101      # 横向有101个点
    ZN = 101      # 纵向有101个点
    DH = 5        # 网格中小正方形的边长
    DT = 0.001    # 采样时间间隔
    num = 40

    v = np.zeros([XN,ZN])+2000
    u1 = np.zeros([XN,ZN])
    u2 = np.zeros([XN,ZN])
    u3 = np.zeros([XN,ZN])
    #n4 = np.zeros([XN,ZN])

    # 震源函数1:原始震源
    # w = []
    # delay = 0.1
    # idd = delay/DT
    # for k in range(KN):
    #     temp = PI*FM*(k-idd)*DT
    #     temp = temp**2
    #     w1 = (1.0-2.0*temp)*(E**(-temp))
    #     w.append(w1)

    # 震源函数2:雷克子波
    w = []
    for k in range(KN):
        w1 = E ** (- pow(2*PI*FM/R,2)*pow(k*DT,2)) * cos(2*PI*FM*k*DT)
        print("w1",w1)
        w.append(w1)

    # 激活函数的初始化:
    f = np.zeros([XN,ZN])
    for i in range(XN):
        for j in range(ZN):
            if i == round(XN/2) and j == round(ZN/2):
                f[i][j] = 1
            else:
                f[i][j] = 0

    # 迭代过程:finite_difference函数来实现
    u4 = finite_difference(XN,ZN,KN,u1,u2,u3,w,f,v,DT,DH,num)
    # 文件写入过程:
    write_into_file(u4,XN,ZN)    
    end = dt.datetime.now()
    print("单进场/线程耗时:", (end-start).seconds, '秒')

main()
