import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq

#三个方法的结果都是完全一样的，都存在过渡拟合的现象。

# 我封装好的曲线拟合函数，输入X数据点列表和Y数据点列表，返回拟合值a,b,c,cost
def solution(X,Y):
    regularization = 0.1  # 正则化系数lambda

    # 二次函数的标准形式
    def func(params, x):
        a, b, c = params
        return a * x * x + b * x + c

    # 误差函数，即拟合曲线所求的值与实际值的差
    def error(params, x, y):
        ret = func(params, x) - y
        return ret

    # 对参数求解
    def slovePara(X,Y):
        p0 = np.array([1, 1, 1])
        Para = leastsq(error, p0, args=(X, Y))
        return Para

    Para = slovePara(X,Y)
    a, b, c = Para[0]
    cost=str(Para[1])

    return a,b,c,cost


def solution_2(X,Y):
    # 生成系数矩阵A
    def gen_coefficient_matrix(X, Y):
        N = len(X)
        m = 3
        A = []
        # 计算每一个方程的系数
        for i in range(m):
            a = []
            # 计算当前方程中的每一个系数
            for j in range(m):
                a.append(sum(X ** (i + j)))
            A.append(a)
        return A

    # 计算方程组的右端向量b
    def gen_right_vector(X, Y):
        N = len(X)
        m = 3
        b = []
        for i in range(m):
            b.append(sum(X ** i * Y))
        return b

    A = gen_coefficient_matrix(X, Y)
    b = gen_right_vector(X, Y)

    a0, a1, a2 = np.linalg.solve(A, b)

    return a2, a1, a0, '0'


def solution_3(X,Y):
    from scipy.optimize import curve_fit

    def Fun(x, a, b, c):  # 定义拟合函数形式
        return a * x ** 2 + b * x + c

    para, pcov = curve_fit(Fun, X, Y)

    return para[0], para[1], para[2] , '0'


def solution_4(X,Y):
    from scipy.optimize import curve_fit

    def get_sqrt(x):
        X_ = []
        for i in x:
            X_.append(np.sqrt(i))
        return  np.array(X_)

    def Fun(x, a, b, c):  # 定义拟合函数形式
        return np.sqrt(a * x ** 2 + b * x + c)

    para, pcov = curve_fit(Fun, get_sqrt(X), get_sqrt(Y))

    return para[0], para[1], para[2] , '0'




if __name__=='__main__':
    X = np.linspace(0, 10, 100)
    Y = 4 * X ** 2 - 9 * X + 3 + np.random.randn(100) * 3
    result=solution(X,Y)
    # a=result[0]
    # b=result[1]
    # c=result[2]
    # cost=result[3]
    a,b,c,cost=result
    print("a=", a, " b=", b, " c=", c)
    print("cost:" , cost)
    print(type(X))

    plt.scatter(X, Y, color="green", label="sample data", linewidth=2)

    #   画拟合直线
    x = np.linspace(0, 10, 100)
    y = a * x * x + b * x + c
    plt.plot(x, y, color="red", label="solution line", linewidth=2)
    plt.legend()  # 绘制图例
    plt.show()
