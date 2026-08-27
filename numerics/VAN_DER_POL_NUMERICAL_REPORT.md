# van der Pol V1--V7 数值实施报告

本报告汇总冻结配置版本 4 下的 van der Pol 主数值运行。论文中的
V1 是精确推导，V2--V7（含 V5A）是解析证明；这里的浮点计算用于展示
这些结论中的可显式对象、检验坐标与渐近公式，并生成真实的定常空间
剖面。它既不替代论文证明，也不是待办任务 #7 所要求的区间验证。

主参数为

\[
 (r,a_2,\epsilon)=(0.08,0,1),\qquad
 d=r^4=4.096\times10^{-5},\quad \delta=r^2=0.0064,\quad a=1.
\]

这些参数是预先冻结的探索性样本，尚未被区间算法认证为论文存在性
参数盒中的显式点。完整的状态边界见
[覆盖矩阵](VAN_DER_POL_COVERAGE_MATRIX.md)，机器可读结果和哈希见
[结果目录](results/vdp_v1_v7/)及
[manifest](results/vdp_v1_v7/manifest.json)。

## 结论摘要

当前实现已经得到五条真实的全 ODE 周期轨道、真实的一至四脉冲对称
同宿剖面，并将它们反标度为原 PDE 的定常空间剖面；相应的闭合、能量和
定常 PDE 残差通过冻结阈值。V1 的 Hamilton 结构及物理/快/中心坐标、
时钟、能量和作用量桥接也已完整实现并通过本次数值 QA。

配置 v4 构造并以冻结接口驱动三类以前缺失的**浮点候选对象**：V3 的非线性
\(W^u\) 源窗到极点的同轨连接及作用量减法；V4--V5 的
\(W^u\to\) central \(\to K_1\to\) finite-\(Q\) 联立匹配；以及 V6 的
B1、A2 两条完整返回与增广长度/作用量。它们有真实研究价值，但仍不等于
“论文全部结论都已数值验证”：显式参数盒、无限时域统一图、伴随交换与
唯一性、混合参数导数、穷尽分支图和全绕转估计尚未做区间认证；V7 的真实
剖面也尚未识别为论文图上的绝对边行程，更没有构造非周期双无限数值轨道。
因此，本次运行的总状态是
`PASS_WITH_EXPLICIT_UNRESOLVED_THEOREM_OBJECTS`，其含义是“已声明的
数值检查通过，同时未显式对象仍保持未解析”，而不是“V1--V7 全部数值
验证通过”。

| 阶段 | 论文状态 | 本次真正算到的对象 | 尚未数值解析的对象 | 主图 |
|---|---|---|---|---|
| V1 | Derived | 9 个精确恒等式；完整坐标/时钟/能量/作用量桥及独立积分加密 | 参数盒上的统一区间认证 | [图 1](results/vdp_v1_v7/figure_01_v1_structure.png) |
| V2 | Proved | 鞍焦谱、7 个参数切片同宿、有限尾横截代理、双符号局部 passage | 精确作用量/绝对相位坐标与穷尽事件布置 | [图 2](results/vdp_v1_v7/figure_02_v2_central_passage.png) |
| V3 | Proved | nonlinear-\(W^u\) 源窗、同一物理 IVP 到 pole、拟合标签、局部重合与同轨作用量有限截断 | 参数/相位区间包络和不定积分极限 | [图 3](results/vdp_v1_v7/figure_03_v3_pole_finite_part.png) |
| V4 | Proved | 精确外层方程、独立终端敏感性梯及联立候选的 finite-\(Q\) outer leg | 最大 infinite future-staying 图及统一法向/聚束估计 | [图 4](results/vdp_v1_v7/figure_04_v4_v5_outer_matching.png) |
| V5 | Proved | nonlinear-\(W^u\to\) central \(\to K_1\to\) outer 三段 BVP、接口和同截面根 | 统一匹配管、伴随交换、唯一性及参数导数 | [图 4](results/vdp_v1_v7/figure_04_v4_v5_outer_matching.png) |
| V5A | Proved | 保存的 matched outer leg 与独立 reference 的同-\(Q\) 有限截断减法及网格加密 | 真实不定积分极限、混合 jets 与统一协变性 | [图 5](results/vdp_v1_v7/figure_05_v5a_algebraic_finite_part.png) |
| V6 | Proved | 166 条首事件样本；B1/A2 两条同截面完整返回和分段增广长度/作用量 | 穷尽分支图、cross forms、绝对绕转及全 \(n\) 界 | [图 6](results/vdp_v1_v7/figure_06_v6_first_event_cells.png)、[图 7](results/vdp_v1_v7/figure_07_v6_length_action.png) |
| V7 | Proved | 5 条周期轨道；真实一至四脉冲定常剖面 | V6 边行程、多边词识别、固定非周期双无限轨道 | [图 8](results/vdp_v1_v7/figure_08_v7_patterns.png) |

## V1：精确 Hamilton 结构与模型桥

[V1 数据](results/vdp_v1_v7/v1_structure.json)中的 9 个符号残差全部精确
化为 `0`，包括第一积分、Hamilton 收缩约定以及 reverser 对向量场、原始
一形式和二形式的作用。对同一条有限轨道，中心到物理再返回的状态误差为
\(1.36\times10^{-12}\)，向量场 push-forward 误差为
\(2.93\times10^{-15}\)，能量缩放误差为 \(1.11\times10^{-16}\)。

中心作用量端值为 \(14.6207589614\)，按精确因子缩放得到
\(4.79093029648\times10^{-5}\)，直接物理计算给出同一数值，端值差为
\(4.00\times10^{-19}\)。独立物理/中心积分加密时，轨道误差从
\(4.04\times10^{-4}\) 降到 \(1.34\times10^{-10}\)，作用量差从
\(3.27\times10^{-9}\) 降到 \(2.83\times10^{-16}\)。这验证了实现中的
符号、尺度和时钟转换，但不从一个样本推出统一参数结论。

## V2：中心同宿与鞍焦局部 passage

[V2 数据](results/vdp_v1_v7/v2_central.json)包含
\(r=0.04,0.06,0.08\)、\(a_2=-0.25,0,0.25\) 和
\(\epsilon=0.8,1,1.2\) 的 7 个非重复样本。所有 BVP 均收敛。主参数处

\[
 \alpha=\beta=2^{-1/2}=0.7071067812,
\]

数值谱与解析四元组的误差为 \(8.01\times10^{-16}\)。主同宿在对称截面
的中心状态约为
\((U,P,V,Q)=(4.92557,0,-8.02334,0)\)；归一化 ODE 残差为
\(2.09\times10^{-9}\)，Hamilton 漂移为 \(4.70\times10^{-12}\)，
截断尾范数为 \(1.35\times10^{-7}\)。有限尾横截代理给出秩三奇异值
\(0.3316\) 和 quotient sine \(0.4558\)，但这不是区间下界或 V2 的
横截证明。

对 \(|\nu_{\rm proxy}|=10^{-4},3\times10^{-5},10^{-5},3\times10^{-6},
10^{-6}\) 的两个符号都完成了精确 ODE passage。JSON 按
\(\log|\nu_{\rm proxy}|\) 回归：时间斜率为 \(-1.41469\) 和
\(-1.41378\)，预测值为 \(-1/\alpha=-1.41421\)；有向相位斜率为
\(1.00114\) 和 \(0.998896\)，预测幅值为 1。事件残差不超过
\(8.67\times10^{-18}\)。这里的 `nu_proxy` 只是线性特征坐标，不是定理
中的精确作用量坐标；故混合二阶余项、绝对相位和完整事件图仍未重建。

## V3：同轨源窗、正参数极点与作用量减法

[V3 数据](results/vdp_v1_v7/v3_pole.json)先用有限后向 BVP 近似非线性
\(W^u\)，按 V2 的冻结相位规范生成正参数源，再沿**同一条物理 IVP**经过
\(x=-U=10\) 门并到达 \(u=20,50,100,200,500\)。相位窗
\([-0.2,0.2]\) 上的 9 个样本全部满足正锥裕量；最小值为

\[
y=26.8759,\quad D=52.2264,\quad K=268.087,\quad
y'=104.360,\quad K'=1755.91.
\]

从高 \(u\) 层拟合得到

\[
(Z_0,W_0,\kappa)=
(-0.6664297671,-0.06889853233,1.6524678712\times10^7),
\]

预测 blow-up 位置为 \(\mathsf x_b=0.9474657682\)。同轨全局解与用这些标签
播种的局部 pole 解在
\(\sigma\in[5\times10^{-4},3\times10^{-3}]\) 上重合，物理/紧化相对
缺陷分别为 \(6.41\times10^{-8}\) 和 \(6.40\times10^{-8}\)。局部场的
物理--紧化相对缺陷为 \(1.01\times10^{-15}\)，独立物理积分重构缺陷为
\(1.89\times10^{-15}\)。这已把旧版中互不相干的源、门和 jet 段变成一个
可回放候选，但 9 个浮点相位点不是闭区间包络。

作用量也作为第五个变量沿该 IVP 累积，密度是
\((\epsilon p^2-q^2)/\delta\)。在最小截断
\(\sigma=5\times10^{-5}\) 上，减去 V3 的 Laurent--log 发散项得到
有限截断值 \(-7.45692005\)；末三层跨度为 \(1.46\times10^{-2}\)，
物理与紧化密度的相对差为 \(2.03\times10^{-16}\)，把截断从源移动到
pole 门的加法残差为 \(1.11\times10^{-10}\)。因此可声称“同轨有限截断
候选和移动截断恒等式已实现”，不能把 \(-7.4569\) 称为已经区间证明存在的
不定积分极限。

## V4、V5 与 V5A：外层尾、匹配缺口和代数有限部

[V4/V5 联立候选](results/vdp_v1_v7/v4_v5_matched_candidate.json)不再把
中心轨道和任意 outer 尾并排展示，而是用一个配点问题同时求解 central、
resolved \(K_1\) 和 outer 三段。源是上述 finite-horizon nonlinear
\(W^u\)，终端条件仍是有限的 \(\alpha(Q_{\rm end})=0\)。得到

\[
\phi_*=5.75883888346,\qquad T_{\rm c}=9.91261798229,
\]

并严格区分 \(Q_R=25<Q_{\rm label}=100<Q_{\rm end}=200\)。BVP/接口最大
残差为 \(2.22\times10^{-16}\)，配点方程的最大 RMS 残差为
\(1.63\times10^{-5}\)，低于冻结阈值 \(2\times10^{-5}\)。独立 beta
continuation 给出的同截面根残差为 \(1.67\times10^{-13}\)，central--
\(K_1\) 的 \(q_1\) 接口残差为 \(4.20\times10^{-12}\)。central、\(K_1\)、
outer 的绝对能量缺陷分别为 \(3.12\times10^{-10}\)、
\(3.73\times10^{-7}\)、
\(2.22\times10^{-16}\)；其中 \(K_1\) 数值来自约 \(5.7\times10^8\)
量级项的抵消，相对尺度约为机器精度。V5A 所需的 scaled/unscaled arrival
margin 均通过。

V4 的独立检查不再只取一个根：冻结的 161 点
\(\beta\in[0,4\times10^{-4}]\) 网格上求得 finite-horizon
\(\Gamma(\beta)\)，最大 solver RMS、边界残差和能量残差分别为
\(2.00\times10^{-8}\)、\(4.53\times10^{-23}\) 和
\(2.78\times10^{-16}\)。在候选 seam beta 处，把终端从
\(Q_{\rm end}=100\) 延至 200、400，\(\Gamma\) 相对候选值的最大变化为
\(5.15\times10^{-19}\)。这些是很强的 finite-\(Q\) 视界敏感性证据，但
仍不是 infinite future-staying 图的存在、最大性或唯一区间证明。

这使“正参数匹配根没有数值实例”的旧结论失效：现在已有一条可复现三段
候选。仍未数值认证的是定理的统一 future-staying 图、完整匹配管、端点伴随
行与交换配对、局部唯一性、参数二阶导数及显式参数盒。冻结解析公式
\(144\sqrt3=249.4153163\) 仍作为理论交叉检查，不应被候选根替代。

[V5A 数据](results/vdp_v1_v7/v5a_outer_finite_part.json)把这条候选的 outer
leg 与独立 \(\beta=0\) reference 放在同一 \(Q\) 网格上。由于
\(Q_R\) 附近存在 \(O(\delta^{-1})\) 的极薄稳定层，输出采用 cosine 端点
加密；801、1601、3201、6401 点的作用量有限截断依次为
\(0.904653,0.885663,0.880935,0.879745\)，最后两层之差为
\(1.19\times10^{-3}\)。6401 点的长度有限截断为
\(-2.63925\times10^{-5}\)，末端 10% 区间的变化分别为
\(9.69\times10^{-14}\)（长度）和 \(2.99\times10^{-7}\)（作用量）。
截断、reference 和 exact-gauge 平衡的最大残差为
\(5.28\times10^{-17}\)。这些结果证明数值采样已解析有限边界层并给出
finite-\(Q\) 候选；它们仍不证明 \(Q\to\infty\) 的不定积分极限、混合
二阶 jets 或在参数盒上的统一参考协变性。

## V6：双符号首事件与两条完整有限返回

[V6 数据](results/vdp_v1_v7/v6_events.json)最终包含 166 个直接积分的
数值源截面样本，分类恰为

| 首事件标签 | 数量 | 正确解释 |
|---|---:|---|
| `pole_gate_proxy` | 163 | 命中有限的 \(U=-10\) 中心门代理；不是区间认证的 V3 极点出口单元 |
| `return+` | 1 | 一条目标横向坐标为正的完整有限返回候选 |
| `return-` | 1 | 一条目标横向坐标为负的完整有限返回候选 |
| `stable_cut_proxy` | 1 | 延拓同宿锚点到达深稳定截断 |

两个返回样本进一步由
[完整分支构造器](vdp_complete_branches.py)沿同一物理 IVP 补齐为“出射面
\(\to\) 全局 excursion \(\to\) 入射面 \(\to\) 局部 saddle passage
\(\to\) 同一出射面”的两段返回：

| 候选 | 数值横向符号 | 物理长度 | 物理作用量 | 局部绕转代理 |
|---|---:|---:|---:|---:|
| B1 | negative \(\to\) negative | \(1.8042270662\) | \(4.7909349748\times10^{-5}\) | \(0.254992\) |
| A2 | positive \(\to\) positive | \(2.1597391152\) | \(4.7909301021\times10^{-5}\) | \(0.754819\) |

B1/A2 的总中心时间分别为 \(22.5528383\) 与 \(26.9967389\)，能量漂移
分别为 \(5.94\times10^{-14}\) 与 \(6.03\times10^{-14}\)。增广变量直接
积分与重采样求积的作用量差分别为 \(1.32\times10^{-17}\) 和
\(5.72\times10^{-18}\)，两段长度和作用量的组合残差均为零。同宿锚点的
截面重构误差为 \(2.62\times10^{-15}\)，抽查加密保持了已观察标签。

这里的正负号是冻结数值特征标架中的**横向坐标符号**，不是 V2 已正规化的
精确作用量符号；绕转数也是未校准代理，不是 V6 的绝对整数标签。因此结果
支持“两个符号各有一条可回放完整返回候选”，但不支持无缝、无重叠、全绕转
分支 census，也没有验证 cross form 或所有可组合边上的作用量 cocycle。

[候选验证合同](results/vdp_v1_v7/v6_candidate_contract.json)采用 schema v2，
已经把 B1/A2、
V3、V4--V5、V5A 输入及理论文本逐项绑定到 SHA-256，并固定参数点和可观测量
规范；配置、直接生成器源码、分支 NPZ 前缀/形状/端点也进入交叉检查。其状态
故意保持 `DRAFT_CANDIDATE_ONLY`、`claim_bearing: false` 和
`final_status: NOT_RUN`。当前工作树未提交，所以 checker 正确给出
`PASS_WITH_DIRTY_SOURCE_WARNING`；可回放性依赖合同中的逐文件哈希，不能只靠
基准提交号。这正是下一阶段 #7 区间回放的输入接口，而不是把浮点计算升级为
严格证明。

## V7：真实周期与多脉冲定常 PDE 剖面

[V7 数据](results/vdp_v1_v7/v7_patterns.json)包含 5 条实际求解的可逆
零能周期轨道。A/B 是数值射击家族名，`relative_winding` 是家族内偏移，
二者都不是 V7 的绝对图边标签。

| 数值家族 | 相对绕转 | 物理空间周期 | 物理作用量 | 闭合残差 |
|---|---:|---:|---:|---:|
| A | 0 | 0.740101 | \(4.73393\times10^{-5}\) | \(2.45\times10^{-13}\) |
| B | 0 | 1.093207 | \(4.79344\times10^{-5}\) | \(3.92\times10^{-13}\) |
| A | 1 | 1.448810 | \(4.79082\times10^{-5}\) | \(2.92\times10^{-12}\) |
| B | 1 | 1.804230 | \(4.79093\times10^{-5}\) | \(1.00\times10^{-11}\) |
| A | 2 | 2.159661 | \(4.79093\times10^{-5}\) | \(2.49\times10^{-11}\) |

V7 的单绕转周期主斜率预测为

\[
 {2\pi r\over \epsilon^{1/4}\beta}=0.71086127.
\]

允许 A/B 具有不同截距的共同拟合斜率为 \(0.71002834\)，相对差
\(1.17\times10^{-3}\)，最大拟合残差为 \(7.14\times10^{-4}\)。这说明
五个样本与鞍焦高绕转的主尺度相容，但不证明 \(n\to\infty\) 一致渐近，
也不确定绝对绕转整数。

周期剖面的最大 Hamilton 漂移为 \(7.25\times10^{-14}\)，最大物理定常
PDE 残差为 \(6.81\times10^{-7}\)，低于冻结阈值
\(2\times10^{-6}\)。此外，一至四脉冲剖面均为求解后的全 ODE 轨道，而非
保留的叠加初猜；请求脉冲数与观察脉冲数分别为 1、2、3、4。二至四脉冲的
最大 collocation RMS 残差为 \(1.995\times10^{-6}\)，最大 Hamilton
漂移为 \(1.648\times10^{-6}\)，最大物理定常 PDE 残差为
\(1.276\times10^{-6}\)，均通过各自冻结门限。

| 脉冲数 | 截断物理区间长度 | 物理作用量 | Hamilton 漂移 | 最大定常 PDE 残差 |
|---:|---:|---:|---:|---:|
| 1 | 4.16 | \(4.79093\times10^{-5}\) | \(4.70\times10^{-12}\) | \(6.41\times10^{-7}\) |
| 2 | 5.92 | \(9.58175\times10^{-5}\) | \(2.23\times10^{-7}\) | \(1.06\times10^{-6}\) |
| 3 | 7.36 | \(1.43726\times10^{-4}\) | \(6.37\times10^{-7}\) | \(1.28\times10^{-6}\) |
| 4 | 8.80 | \(1.91634\times10^{-4}\) | \(1.65\times10^{-6}\) | \(1.06\times10^{-6}\) |

尚不能把这些剖面标成已验证的有限边词：当前显示的 `A0`、`B1` 等字符串
只是请求/家族元数据，缺少 V6 截面交叉的完整行程检查。四个增长窗口也只是
四条通过残差门的全 ODE 有限截断边值解，并不单独认证无穷区间同宿性或唯一性；
也没有验证固定非周期词在公共中心窗口上收敛，因此不能称为数值构造的非周期
双无限轨道。

## 与 Turing 斑纹、canard 和时间稳定性的关系

V1--V7 先令 PDE 的时间导数为零，把问题变成以物理空间 \(\mathsf x\) 为
“时间”的四维可逆 Hamilton ODE。V7 的周期轨道和同宿/多脉冲轨道经反标度
后确实是原 PDE 的**定常空间斑纹**。因此，当前数值结果能具体展示：固定
参数处存在不同空间周期的周期剖面；增加相对绕转会按约 \(0.7109\) 的尺度
增长空间周期；一至四个宏观脉冲的局域剖面可以直接求出。

这与 Turing 分岔仍是两个不同层次。Turing 分析考察齐次态在时间演化下对
有限波数 Fourier 模式的线性失稳，并需要从中延拓定常分支；本仓库的 V7
存在性证明和本次射击/配点计算都没有建立“这些高绕转剖面从某条 Turing
中性曲线分岔”的连接。因而当前数据不能确定随控制参数变化时实际系统会
选择哪种波长、何时在不同斑纹间跳转，或这些剖面是否可在时间模拟/实验中
观察到。

canard 只应作为 V4--V5 外层慢几何的一个待检验解释。局部高绕转及周期增长
来自原点附近的 saddle-focus 旋转和对数 passage，**不是 canard**。本次已
得到 nonlinear-\(W^u\to\) central \(\to K_1\to\) finite-\(Q\) outer 的
联立匹配候选，所以“V5 匹配完全没有数值实例”已不再成立；但代码没有沿慢
流形计算吸引/排斥分支、定位折叠慢流形，也没有测量随小参数指数敏感的
canard 区间。因此目前只能说 outer 退出几何已被显式化，不能把它命名为
已识别或已验证的 canard。极点门和代数门本身也只是退出方向，不组成有界
周期斑纹。

最后，定常 PDE 残差只说明一个剖面近似满足“时间导数为零”的方程，不说明
它在 PDE 时间流下稳定。要从“定理保证存在、数值画出剖面”走到“真实动力学
选择这种斑纹”，至少还需要周期剖面的 Bloch/Floquet 或 Evans 谱计算、局域
剖面的相应谱与非线性稳定性分析，以及直接时变 PDE 模拟。当前结论是空间
存在与空间组织，不是时间稳定、时间混沌或 Turing 选择。

## 图与机器证据索引

| 图 | 内容 | 证据边界 | PDF / SVG |
|---|---|---|---|
| [1](results/vdp_v1_v7/figure_01_v1_structure.png) | V1 精确结构与时钟桥 | 精确恒等式 + 单轨道 QA | [PDF](results/vdp_v1_v7/figure_01_v1_structure.pdf) / [SVG](results/vdp_v1_v7/figure_01_v1_structure.svg) |
| [2](results/vdp_v1_v7/figure_02_v2_central_passage.png) | V2 同宿延拓与局部 passage | 有限切片与线性坐标代理 | [PDF](results/vdp_v1_v7/figure_02_v2_central_passage.pdf) / [SVG](results/vdp_v1_v7/figure_02_v2_central_passage.svg) |
| [3](results/vdp_v1_v7/figure_03_v3_pole_finite_part.png) | V3 同轨源窗、pole 匹配与 Laurent--log 减法 | finite-horizon 浮点候选；未做区间包络 | [PDF](results/vdp_v1_v7/figure_03_v3_pole_finite_part.pdf) / [SVG](results/vdp_v1_v7/figure_03_v3_pole_finite_part.svg) |
| [4](results/vdp_v1_v7/figure_04_v4_v5_outer_matching.png) | V4--V5 central/\(K_1\)/outer 联立匹配 | finite-\(Q\) 匹配候选；无统一图/唯一性认证 | [PDF](results/vdp_v1_v7/figure_04_v4_v5_outer_matching.pdf) / [SVG](results/vdp_v1_v7/figure_04_v4_v5_outer_matching.svg) |
| [5](results/vdp_v1_v7/figure_05_v5a_algebraic_finite_part.png) | V5A 同-\(Q\) 长度/作用量有限部与网格加密 | finite-\(Q\) 候选；未证明不定积分极限 | [PDF](results/vdp_v1_v7/figure_05_v5a_algebraic_finite_part.pdf) / [SVG](results/vdp_v1_v7/figure_05_v5a_algebraic_finite_part.svg) |
| [6](results/vdp_v1_v7/figure_06_v6_first_event_cells.png) | V6 有限首事件截面与双符号返回 | 163/1/1/1；有限采样非穷尽图册 | [PDF](results/vdp_v1_v7/figure_06_v6_first_event_cells.pdf) / [SVG](results/vdp_v1_v7/figure_06_v6_first_event_cells.svg) |
| [7](results/vdp_v1_v7/figure_07_v6_length_action.png) | B1/A2 完整返回的分段长度/作用量及周期趋势 | 两条同轨候选；非全分支 cocycle | [PDF](results/vdp_v1_v7/figure_07_v6_length_action.pdf) / [SVG](results/vdp_v1_v7/figure_07_v6_length_action.svg) |
| [8](results/vdp_v1_v7/figure_08_v7_patterns.png) | 周期及一至四脉冲 PDE 剖面 | 真实剖面；边词未识别 | [PDF](results/vdp_v1_v7/figure_08_v7_patterns.pdf) / [SVG](results/vdp_v1_v7/figure_08_v7_patterns.svg) |
| [9](results/vdp_v1_v7/figure_09_numerical_qa.png) | 汇总 QA 与覆盖边界 | 质量控制，不是定理认证 | [PDF](results/vdp_v1_v7/figure_09_numerical_qa.pdf) / [SVG](results/vdp_v1_v7/figure_09_numerical_qa.svg) |

每幅图的语义、允许结论和禁止过度解释见
[图合同](VAN_DER_POL_FIGURE_CONTRACTS.md)。

## QA 与复现

[QA 文件](results/vdp_v1_v7/qa.json)中的 40 个布尔检查全部为真，包括
V1 桥接与独立时钟加密、V2 切片和 passage 斜率、V3 源窗/同轨 overlap/
独立场与作用量检查、V4--V5 联立候选接口和到达裕量、V5A 端点网格加密、
V6 双符号完整返回/分段组合/候选合同，以及 V7 周期闭合和多脉冲残差门。
同时，QA 强制保留下列未解析状态：V3 的统一区间参数盒与不定积分包络；V4
的 infinite future-staying 图和统一 cocycle/bunching 界；V5 的统一匹配管、
伴随交换、唯一性与参数导数；V6 的定理坐标穷尽单元、cross forms 和全绕转
界；V7 的定理边行程和一条双无限数值轨道。这些是数值/严格认证的缺口，
不是论文证明失败。

当前 manifest 记录提交 `262d12dd61bc9fd3a4f44017fdfc5f14cc571259`，
同时记录 `repository_dirty: true`；因此复现应以 manifest 中的逐文件 SHA-256
为准，而不能只依赖提交号。记录环境为 Python 3.14.4、NumPy 2.5.2、
SciPy 1.18.0 和 Matplotlib 3.11.1。

在仓库根目录运行：

```bash
python3 numerics/run_vdp_master.py
python3 numerics/check_vdp_master.py
python3 validation/check_candidate_contract.py numerics/results/vdp_v1_v7/v6_candidate_contract.json
python3 -m unittest discover -s numerics -p 'test_*.py'
python3 -m unittest discover -s validation -p 'test_*.py'
```

第一条命令重新计算 V1--V7 数据并输出九幅 PDF/SVG/PNG；第二条检查必需
文件、manifest 哈希、NPZ 类型和强制未解析状态；第三条验证候选合同的 schema
和所有哈希，但会明确报告没有执行区间证明；最后两条分别运行 54 项数值回归
测试与 10 项合同/验证脚手架测试，共 64 项。若只需从已保存数据重绘而不重跑
求解器，可运行：

```bash
python3 numerics/render_vdp_figures.py numerics/results/vdp_v1_v7
```
