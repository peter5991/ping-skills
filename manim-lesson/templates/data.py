"""贯穿全片的数据与所有画面上出现的数值。运行本文件即执行断言。

规约:场景与 web 教具页出现的每个数字都从这里算,禁手写;改数字先改这里并重跑断言。
断言要和独立方法对拍(如自己实现的拟合 vs np.polyfit)。

示例(最小二乘):
    import numpy as np
    X = np.array([1, 2, 3, 4, 5], dtype=float)
    Y = np.array([50, 62, 68, 78, 82], dtype=float)
    XM, YM = X.mean(), Y.mean()
    K = ((X - XM) * (Y - YM)).sum() / ((X - XM) ** 2).sum()
    B = YM - K * XM

    if __name__ == "__main__":
        kp, bp = np.polyfit(X, Y, 1)
        assert np.isclose(kp, K) and np.isclose(bp, B)
        print(f"OK k={K} b={B}")
"""

if __name__ == "__main__":
    print("OK(还没有数据,补上你的断言)")
