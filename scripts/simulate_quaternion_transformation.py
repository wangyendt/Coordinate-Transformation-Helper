# author: wangye(Wayne)
# license: Apache Licence
# file: simulate_quaternion_transformation.py
# time: 2023-11-24-10:48:03
# contact: wang121ye@hotmail.com
# site:  wangyendt@github.com
# software: PyCharm
# code is far away from bugs.


from sympy import Quaternion, cos, sin, rad, symbols, simplify

w, x, y, z = symbols('w x y z')

# 初始化（左手系）
q = Quaternion(w, x, y, z)

# x轴关于yOz平面镜像
q = Quaternion(w, x, -y, -z)

# 右手系绕x轴顺时针旋转90度
theta = 90
w = cos(rad(theta) / 2)
x = sin(rad(theta) / 2)
q_rotate = Quaternion(w, x, 0, 0)
q_rotate_inv = q_rotate.inverse()
q = q_rotate * q * q_rotate_inv

# 右手系绕z轴顺时针旋转180度
theta = 180  # 旋转角度为 -90 度
w = cos(rad(theta) / 2)
z = sin(rad(theta) / 2)
q_rotate = Quaternion(w, 0, 0, z)
q_rotate_inv = q_rotate.inverse()
q = q_rotate * q * q_rotate_inv

print(simplify(q))
