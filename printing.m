s = load('D:\��-������������ܼ���\HPCGeo\pythonʵ��\����\�������\orig-testorig.dat')
m = 101
n = 101
dx = 1;
dz = 1;

for i=1:m
    for j=1:n
        x(j) = (i-1)*dx + s((i-1)*n+j+2)*4*dx;
        y(j) = (j-1)*dz;
        imagesc(x(i),y(j))
    hold on 
    end
end

%axis ij
title('��������')

