# finite-difference
利用python实现二维声波波场的并行计算
说明：由于python存在GIL全局任务锁导致“多线程”对高计算量程序效率的改善的不升反降！因此本任务全部使用多进程。  
origprogram.py文件：原始计算程序，单进程
subarea.py文件：将计算的网格分成4个区域，按照这4个区域进行并行计算；具体分区情况及注意事项见“分区思路.pdf”文件；
processprogram.py文件：是根据计算公式拆解来进行并行计算；
print.m文件：matlab画图文件，可以绘制波场快照；
