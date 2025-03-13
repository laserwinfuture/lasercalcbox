import math
#我封装好的M2计算函数，输入变量是三个拟合系数和波长，返回值是计算出来的M2
#math.pi是常量π
#math.pow(x,y)：用于计算x^y, 因此x开根号=math.pow(x,0.5), x^(-3)= math.pow(x,-3)

def get(c,b,a,wavelength=1.064):                 #a,b,c为曲线拟合的几个系数,wavelength为波长单位um
    #曲线拟合得到的a,b,c和高斯光束那个a和c是反着的                      
    wavelength=wavelength*math.pow(10,-3)  #先把wavelength从um转成mm
    M2=math.pi/8/wavelength*math.pow(abs(4*a*c-b*b),0.5)
    Z0=-b/2/c
    d0=1/2/math.pow(c,0.5)*math.pow(abs(4*a*c-b*b),0.5)
    Theta0=math.pow(c,0.5)
    RayLength=1/2/c*math.pow(abs(4*a*c-b*b),0.5)

    # Z0=-b/2/c
    # d0=math.pow(a-b*b/4/c,0.5)    

    # return M2,Z0,d0
    return M2,Z0,d0,Theta0,RayLength

if __name__=='__main__':
    a=2.823822900576277e-05 
    b=-0.02994774619449656
    c= 8.018573784731394
    wavelength=1.064
    # M2,Z0,d0=get(a,b,c,wavelength)
    M2,Z0,d0,Theta0,Raylength=get(a,b,c,wavelength)
    print("M2:     %.3f"  % M2)
    print("Z0(mm): %.1f"  % Z0)
    print("d0(mm): %.3f"  % d0) 
    Theta0=Theta0*1000                   #rad转成mrad
    print("Full Div.(mrad): %.3f" % Theta0) 
    print("Raylength(mm): %.1f"   % Raylength)
