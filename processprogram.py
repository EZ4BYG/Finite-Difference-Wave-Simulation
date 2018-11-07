from multiprocessing import Process,Pipe,Event
import numpy as np
import math 
import datetime as dt
import time
import copy

# 写文件
def write_into_file(u4):
    print("数据写入文件开始:")
    ARRS = []
    f = open('testprocess.txt', 'w+')
    for i in range(100):
        jointsFrame = u4[i]
        ARRS.append(jointsFrame)
        for ji in range(100):
            strNum = str(jointsFrame[ji])
            f.write(strNum)
            f.write(',')
        f.write('\n')
    f.close()
    print("波场快照数据写入完毕!")

# 独立事件1:计算uu0矩阵
def uu0_function(XN,ZN,KN,DT,DH,v,uu0):
    print("独立事件1已开始!")
    for k0 in range(KN):
        for i0 in range(2,XN-2):
            for j0 in range(2,ZN-2):
                uu0[i0][j0] = (v[i0][j0]**2) * (DT/DH)**2
        child1_conn.send(uu0)
        e.wait()
    print("事件1结束!")

# 独立事件2:计算uu1矩阵
def uu1_function(XN,ZN,KN,u2,uu1):
    print("独立事件2已开始!")
    for k1 in range(KN):
        for i1 in range(2,XN-2):
            for j1 in range(2,ZN-2):
                uu1[i1][j1] = -1.0/12*(u2[i1-2][j1] + u2[i1+2][j1]) + \
                               4.0/3*(u2[i1-1][j1] + u2[i1+1][j1]) - \
                               5.0/2*u2[i1][j1]
        child2_conn.send(uu1)
        e.wait()
        u2 = child2_conn.recv()
    print("事件2结束!")

# 独立事件3:计算uu2矩阵
def uu2_function(XN,ZN,KN,u2,uu2):
    print("独立事件3已开始!") 
    for k2 in range(KN):
        for i2 in range(2,XN-2):
            for j2 in range(2,ZN-2):
                uu2[i2][j2] = -1.0/12*(u2[i2][j2-2] + u2[i2][j2+2]) + \
                               4.0/3*(u2[i2][j2-1] + u2[i2][j2+1]) - \
                               5.0/2*u2[i2][j2]
        child3_conn.send(uu2)
        e.wait()
        u2 = child3_conn.recv()
    print("事件3结束!")

# 独立事件4:计算u3和u4矩阵
def uu3_function(XN,ZN,KN,w,f,u1,u2,u3,u4,uu0,uu1,uu2):
    print("独立事件4已开始!")
    for k3 in range(KN):
        for i3 in range(2,XN-2):
            for j3 in range(2,ZN-2):
                u3[i3][j3] = 2*u2[i3][j3] - u1[i3][j3] + \
                             uu0[i3][j3]*uu1[i3][j3] + \
                             uu0[i3][j3]*uu2[i3][j3] + \
                             w[k3]*f[i3][j3]

        u1 = copy.copy(u2)
        u2 = copy.copy(u3)

        if k3 == 10:
            u4 = copy.copy(u3)

        uu0 = parent1_conn.recv()
        uu1 = parent2_conn.recv()
        uu2 = parent3_conn.recv()
        parent2_conn.send(u2)
        parent3_conn.send(u2)
        e.set()
        print("第%d次并行迭代结束!"%(k3+1), '还有%d次迭代!'%(KN-k3-1))
        e.clear()
        time.sleep(0.01)
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
child1_conn, parent1_conn = Pipe()
child2_conn, parent2_conn = Pipe()
child3_conn, parent3_conn = Pipe()

uu0process = Process(target = uu0_function, args = (XN,ZN,KN,DT,DH,v,uu0))
uu1process = Process(target = uu1_function, args = (XN,ZN,KN,u2,uu1))
uu2process = Process(target = uu2_function, args = (XN,ZN,KN,u2,uu2))
uu3process = Process(target = uu3_function, args = (XN,ZN,KN,w,f,u1,u2,u3,u4,uu0,uu1,uu2))

uu0process.start()
uu1process.start()
uu2process.start()
uu3process.start()

uu0process.join()
uu1process.join()
uu2process.join()
uu3process.join()

end = dt.datetime.now()
print("多进程耗时:", end - start)