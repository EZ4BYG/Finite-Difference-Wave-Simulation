from threading import *
import numpy as np
import math 
import datetime as dt
import copy
import sys 

# 写文件
def write_into_file(u4):
    print("数据写入文件开始:")
    ARRS = []
    f = open('testARRS.txt', 'w+')
    for i in range(100):
        jointsFrame = u4[i]
        ARRS.append(jointsFrame)
        for ji in range(100):
            strNum = str(jointsFrame[ji])
            f.write(strNum)
            f.write(',')
        f.write('\n')
    f.close()
    print("数据写入完毕!")


# 独立事件1:计算uu0矩阵
def uu0_function(XN,ZN,KN,DT,DH,v):
    global uu0
    print("独立事件1已开始!")
    for k0 in range(KN):
        for i0 in range(2,XN-2):
            for j0 in range(2,ZN-2):
                uu0[i][j] = (v[i0][j0]**2) * (DT/DH)**2
        e.wait()
    print("事件1结束!")


# 独立事件2:计算uu1矩阵
def uu1_function(XN,ZN,KN):
    global uu1
    #global u2
    # try1 = np.zeros([XN,ZN])
    print("独立事件2已开始!")
    for k1 in range(KN):
        for i1 in range(2,XN-2):
            for j1 in range(2,ZN-2):
                uu1[i1][j1] = -1.0/12*(u2[i1-2][j1] + u2[i1+2][j1]) + \
                               4.0/3*(u2[i1-1][j1] + u2[i1+1][j1]) - \
                               5.0/2*u2[i1][j1]
        # print((uu1==try1).all())
        # try1 = copy.copy(uu1)
        e.wait()
    print("事件2结束!")


# 独立事件3:计算uu2矩阵
def uu2_function(XN,ZN,KN):
    global uu2
    #global u2
    print("独立事件3已开始!") 
    for k2 in range(KN):
        for i2 in range(2,XN-2):
            for j2 in range(2,ZN-2):
                uu2[i2][j2] = -1.0/12*(u2[i2-2][j2] + u2[i2+2][j2]) + \
                               4.0/3*(u2[i2-1][j2] + u2[i2+1][j2]) - \
                               5.0/2*u2[i2][j2]
        e.wait()
    print("事件3结束!")
    

# 独立事件4:计算u3和u4矩阵
def uu3_function(XN,ZN,KN,w,f):
    global u1,u2,u3,u4   # 都是自己要用的
    global uu0,uu1,uu2
    uu1old = np.zeros([XN,ZN])
    uu2old = np.zeros([XN,ZN])
    uu0old = np.zeros([XN,ZN])
    try1 = np.zeros([XN,ZN])
    print("独立事件4已开始!")

    for k3 in range(KN):

        if k3 != 0:
            while True:
                # 为了下面的u3计算公式里的元素uu0,uu1,uu2每次都是更新过的
                if (uu1old==uu1).all() or (uu2old == uu2).all() or (uu0old == uu0).all():  # 全部“不相等”才可以
                    continue
                else: # 上面条件全是False, 即所有全局已改变
                    #print("检验已经通过,数据更新了")
                    uu1old = copy.copy(uu1)
                    uu2old = copy.copy(uu2)  
                    break
 
        for i3 in range(2,XN-2):
            for j3 in range(2,ZN-2):
                u3[i3][j3] = 2*u2[i3][j3] - u1[i3][j3] + \
                             uu0[i3][j3]*uu1[i3][j3] + \
                             uu0[i3][j3]*uu2[i3][j3] + \
                             w[k3]*f[i3][j3]
        #write_into_file(u3)

        u1 = copy.copy(u2)
        u2 = copy.copy(u3)

        if k3 == 10:
            u4 = copy.copy(u3)
            print((u4==try1).all())

        # print((u3==try1).all())
        # try1 = copy.copy(u3)

        e.set()
        e.clear()  
        print("第%d次并行迭代结束!"%(k3+1), '还有%d次迭代!'%(KN-k3-1))

    # 最后把u4计算结果写到文件中
    e.set()
    print("事件4结束!")
    write_into_file(u4)

# -----------------------------------------------#
start = dt.datetime.now()
E = math.e    # 自然对数e
PI = math.pi  # 圆周率
FM = 30       # 基频
R = 3         # 控制频带宽度的参数
KN = 200      # 采样总次数
XN = 101      # 横向有101个点
ZN = 101      # 纵向有101个点
DH = 5        # 网格中小正方形的边长
DT = 0.001    # 采样时间间隔

v = np.zeros([XN,ZN])+2000
u1 = np.zeros([XN,ZN])
u2 = np.zeros([XN,ZN])
u3 = np.zeros([XN,ZN])
u4 = np.zeros([XN,ZN])
uu0 = np.zeros([XN,ZN])
uu1 = np.zeros([XN,ZN])
uu2 = np.zeros([XN,ZN])

# 对震源函数的离散化
w = []
delay = 0.1
idd = delay/DT
for k in range(KN):
    temp = PI*FM*(k-idd)*DT
    temp = temp**2
    w1 = (1.0-2.0*temp)*(E**(-temp))
    w.append(w1)

# 激活函数的初始化:
f = np.zeros([XN,ZN])
for i in range(XN):
    for j in range(ZN):
        if i == round(XN/2) and j == round(ZN/2):
            f[i][j] = 1
        else:
            f[i][j] = 0

e = Event()

uu0thread = Thread(target = uu0_function, args = (XN,ZN,KN,DT,DH,v))
uu1thread = Thread(target = uu1_function, args = (XN,ZN,KN))
uu2thread = Thread(target = uu2_function, args = (XN,ZN,KN))
uu3thread = Thread(target = uu3_function, args = (XN,ZN,KN,w,f))

uu0thread.start()
uu1thread.start()
uu2thread.start()
uu3thread.start()

uu0thread.join()
uu1thread.join()
uu2thread.join()
uu3thread.join()

end = dt.datetime.now()
print("多线程耗时:", end - start)
