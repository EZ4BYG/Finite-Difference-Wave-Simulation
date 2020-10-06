# Forward modeling of 2D acoustic wave field by finite difference

**Contents**: using Python to realize the parallel computation of 2D acoustic wave field forward simulation 

**Tips**:
- Due to the existence of GIL global task lock in Python, '**multi-threading**' cannot improve the efficiency of computational-intensive programs! So this task is all carried out by '**multi-process**'
- origprogram.py：Original computor, single process
- subarea.py: Using this program to divide the calculated grid into 4 regions, so that the program could be run in 4 processes simultaneously. More detailed regional division information can be found in **分区思路.pdf** file
- processprogram.py: Performing parallel computation according to the divided region
- print.m: Drawing snapshots of the wave field at different times

---

# 有限差分二维声波波场正演模拟

**内容**：利用python实现二维声波波场的并行计算

**注意**：
- 由于python存在GIL全局任务锁导致“多线程”对高计算量程序效率的改善的不升反降！因此本任务全部使用多进程。  
- origprogram.py：原始计算程序，单进程
- subarea.py：将计算的网格分成4个区域，按照这4个区域进行并行计算；具体分区情况及注意事项见“分区思路.pdf”文件；
- processprogram.py：是根据计算公式拆解来进行并行计算；
- print.m：matlab画图文件，可以绘制波场快照；
