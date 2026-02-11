# Coordinate Transformation Helper

Language: [English](README.md) | **中文**

一个用于姿态与坐标表达统一的 GUI 工具。当前支持两类可解耦、可组合的转换：

1. 坐标系变换（Frame Transform）
2. 手表佩戴模式变换（Wear Transform：左右手 + 左右表冠）

两类转换共用同一套输出区（日志 + 公式），点击 `Transform` 后会自动合成为最终变换。

## UI 预览

| 坐标系变换页签 | 佩戴模式页签 |
|---|---|
| ![坐标系变换页签](docs/images/tab-frame-transform.png)<br>配置 source/target 坐标轴方向与四元数顺序。 | ![佩戴模式页签](docs/images/tab-wear-transform.png)<br>配置 source/target 左右手与表冠左右模式。 |

## 为什么需要两类转换

### 1) 坐标系变换（坐标系变换页签）

**典型场景**

- 算法模块之间坐标定义不一致（如 OpenCV / OpenGL / IMU / Unity）。
- 同一个旋转在不同坐标系下需要等价表示（含四元数分量顺序差异）。

**核心原理**

- 根据 source/target 的轴方向映射（轴置换 + 符号翻转）构造正交矩阵 `R_frame`。
- 普通向量（位置、速度、加速度）：
  `v_t = R_frame * v_s`
- 伪向量（角速度、四元数虚部对应旋转轴）：
  `p_t = det(R_frame) * R_frame * p_s`

### 2) 佩戴模式变换（佩戴模式页签）

**典型场景**

- 微手势模型以“左手 + 表冠右侧”为训练基准，但线上设备可能是右手/表冠左侧。
- 需要在模型前对 IMU 数据做统一化，或把一种佩戴方式映射到另一种佩戴方式。

**核心原理（基于文档推导）**

- 左右手切换等价于 `yz` 平面镜像：
  `M = diag(-1, 1, 1)`
- 表冠右/左切换等价于平面内翻转：
  `C = diag(-1, -1, 1)`
- 对普通向量（`acc`）使用 `R_wear`；
- 对伪向量（`gyro`）使用 `det(R_wear) * R_wear`。
- 若左右手发生变化，需要做手势语义映射：`左摆 <-> 右摆`。

## 两类转换如何组合

工具内部按以下方式组合：

- `R_total_vec = R_frame * R_wear`
- `R_total_pseudo = det(R_total_vec) * R_total_vec`

因此：

- `acc_out = R_total_vec * acc_in`
- `gyro_out = R_total_pseudo * gyro_in`
- 四元数虚部同样使用 `R_total_pseudo` 映射，标量部 `q_w` 不变。

## 四种佩戴模式（相对“左手-表冠右(基准)”）

| 佩戴方式 | acc 变换 | gyro 变换 | 手势语义 |
|---|---|---|---|
| 左手-表冠右 | `( ax,  ay, az)` | `( gx,  gy,  gz)` | 不变 |
| 左手-表冠左 | `(-ax, -ay, az)` | `(-gx, -gy,  gz)` | 不变 |
| 右手-表冠右 | `(-ax,  ay, az)` | `( gx, -gy, -gz)` | 左摆↔右摆 |
| 右手-表冠左 | `( ax, -ay, az)` | `(-gx,  gy, -gz)` | 左摆↔右摆 |

## 使用流程

1. 在 `坐标系变换` 页签配置 source/target 坐标系（或用预设按钮）。
2. 在 `佩戴模式` 页签选择 source/target 佩戴方式。
3. 选择四元数分量顺序（`w,x,y,z` 或 `x,y,z,w`）。
4. 点击 `Transform`，在下方查看：
   - 日志矩阵结果
   - 分层公式：`R_frame`、`R_wear`、`R_total_vec`、`R_total_pseudo`
   - 四元数映射表达式

## 说明

- 两类转换在 UI 上解耦，便于分别理解；在计算上自动组合，避免手工连乘出错。
- 当日志内容较宽时，左右滚动条可用于查看完整矩阵文本。
