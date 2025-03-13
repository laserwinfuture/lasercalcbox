import math
'''我封装好的束腰变换函数
    输入变量:经过聚焦镜之后的参数(双曲线拟合得到), M2,d0_束腰直径mm,Z0_束腰位置mm,Zr_锐利长度mm,波长单位um，焦距单位mm   
    输出结果:透镜变换之前的各种参数：M2,d0,Theta0,Z0,ZR 
'''
def solve(M2,d0_,Z0_,Zr_,wavelength=1.064,f=300):   
    #a,b,c为曲线拟合的几个系数,wavelength为波长单位um                         
    d0=2*math.pow(d0_*d0_/4/(math.pow(1-Z0_/f,2)+math.pow(Zr_/f,2)),0.5)
    Theta0=4*M2*wavelength/math.pi/d0
    Z0=f-f*((1-Z0_/f)/(math.pow(1-Z0_/f,2)+math.pow(Zr_/f,2)))
    ZR=math.pi*d0**2/(4*wavelength*M2)*1000
    return M2,d0,Theta0,Z0,ZR

if __name__=='__main__':
    M2=1.075
    d0_=0.284
    Z0_=529.342
    Zr_=55.5002
    wavelength=1.064
    f=300
    M2,d0,Theta0,Z0,ZR=solve(M2,d0_,Z0_,Zr_,wavelength,f)
    print('Before focus report:')
    print("M2:     %.3f"  % M2)
    print("Z0(mm): %.1f"  % Z0)
    print("d0(mm): %.3f"  % d0) 
    print("Full Div.(mrad): %.3f" % Theta0) 
    print("Raylength(mm): %.1f"   % ZR)

    M2=1.054
    d0_=0.284
    Z0_=529.742
    Zr_=56.535
    wavelength=1.064
    f=300
    M2,d0,Theta0,Z0,ZR=solve(M2,d0_,Z0_,Zr_,wavelength,f)
    print('Before focus report:')
    print("M2:     %.3f"  % M2)
    print("Z0(mm): %.1f"  % Z0)
    print("d0(mm): %.3f"  % d0) 
    print("Full Div.(mrad): %.3f" % Theta0) 
    print("Raylength(mm): %.1f"   % ZR)