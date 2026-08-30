# van der Pol V1--V7 数值实施报告

本报告汇总冻结配置版本 5 下的 van der Pol 主数值运行。论文中的
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

配置 v5 构造并以冻结接口驱动三类以前缺失的**浮点候选对象**：V3 的非线性
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

后续的[时间动力学、Turing 与 canard 预筛](VDP_DYNAMICS_SCREENING_REPORT.md)
没有改变 V1--V7 数值图册的证据等级。它精确排除了本模型从时间稳定齐次态
出发的经典静止 Turing 机制；后续独立目标验证还分别给出了 A2 周期斑纹和
`pulse_1` 的正实时间谱值及相应非线性轨道不稳定性结论，但不推出动力选择。
折点 passage 与奇异 FSN-II 退化已被诊断，有限边界 canard coincidence 已由
多重打靶重放，但 intrinsic maximal canard 尚未识别。Issue #7 的 v2 盒上
P1、受限 P2a--P2d 和三个 P2e 相位间隙已经局部通过；完整 P2e 事件图册、
后续统一区间义务及独立 replay 仍待完成。

| 阶段 | 论文状态 | 本次真正算到的对象 | 尚未数值解析的对象 | 主图 |
|---|---|---|---|---|
| V1 | Derived | 9 个精确恒等式；完整坐标/时钟/能量/作用量桥及独立积分加密 | 参数盒上的统一区间认证 | [图 1](results/vdp_v1_v7/figure_01_v1_structure.png) |
| V2 | Proved | 鞍焦谱、7 个参数切片同宿、有限尾横截代理、Kato 相位的非线性 \(W^u\) 零能量源探针、双符号局部 passage | 精确 Moser/作用量坐标与穷尽事件布置 | [图 2](results/vdp_v1_v7/figure_02_v2_central_passage.png) |
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

同一输出还实现了 P2bK 的显式 Kato frame 和 V2(28) 的相位约定。在
\((r,a_2,\epsilon)=(0.08,0,1)\)、相位 0 上，有限时域非线性 \(W^u\)
主干以及 \(\nu=\pm10^{-6}\) 的零能量横向点均通过门限：8 与 10 的图
horizon 状态差为 \(1.14\times10^{-12}\)，最大 Hamilton 残差为
\(1.28\times10^{-11}\)，辛定向 pairing 为 1，正 \(\nu\) 逆坐标的
状态重构误差为 \(3.50\times10^{-18}\)。这是 Kato 相位兼容、第一阶
Darboux 定向的数值源截面；它明确设置 `raw_chart_identical=false`，不是
论文中存在性给出的精确非线性 Moser/Darboux 图，也不是精确作用量坐标。

对 \(|\nu_{\rm proxy}|=10^{-4},3\times10^{-5},10^{-5},3\times10^{-6},
10^{-6}\) 的两个符号都完成了精确 ODE passage。JSON 按
\(\log|\nu_{\rm proxy}|\) 回归：时间斜率为 \(-1.41469\) 和
\(-1.41378\)，预测值为 \(-1/\alpha=-1.41421\)；有向相位斜率为
\(1.00114\) 和 \(0.998896\)，预测幅值为 1。事件残差不超过
\(8.67\times10^{-18}\)。这里的 `nu_proxy` 只是线性特征坐标，不是定理
中的精确作用量坐标；故混合二阶余项、绝对相位和完整事件图仍未重建。

在 Issue #7 的 v2 盒中心，另有一个冻结的 100 点 thick-source 浮点普查：
20 个相位点分别取自 algebraic、homoclinic 和 pole 邻域，并配以 5 个
\(\nu\) 偏移。首事件计数为 40 个 algebraic、59 个 pole 和 1 个 return；
pole patch 的 25 点全为 pole，而 homoclinic patch 出现细薄交替。唯一 return
位于 homoclinic 中心、\(\nu=0\)，其首返时间约为 `19.2759361067`。
[完整矩阵](P2E_V2_SOURCE_PATCH_CENSUS_REPORT.md)是 P2e 单元生成器；它没有
闭区间包络、连通分支证明或无遗漏证明，不能代替完整事件图册。

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
(Z_0,W_0,c_4)=
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
候选。后续 v2 中心计算又补上了固定能量切片缺失的方向。线性化
positive-`pi` BVP 给出
\(\partial_H\Gamma=6.4288158988\times10^{-16}\)，随后把完整三分量共法向
沿 resolved \(K_1\) 回传到中心截面。Jost 归一化行与冻结行的余弦为
`0.9999999962`，正向配对为 `249.4535908217`，相对解析值
\(144\sqrt3=249.4153162899\) 的偏差为 `0.01535%`；对应的二乘二匹配
导数最小奇异值为 `0.00182658`。这些是有限 `Q=200` 图代理上的单点
`COMPUTED/E1`/QA 结果。仍未数值认证的是定理的无限 maximal graph、统一
匹配管和 exchange 下界、局部非线性唯一性、参数二阶导数及显式参数盒。

同一候选现在还按 V5(61)--(62) 保存了完整的有限三段作用量。central、
resolved \(K_1\) 和 outer \(Q_R=25\to Q_*=100\) 三项分别约为
\(-2.70633\times10^{-4}\)、\(-4.99788\times10^4\) 和
\(-1.90430\times10^6\)，合计约
\(-1.95428\times10^6\)。两个物理接口、各图 primitive 的独立密度重构、
resolved \(K_1\) 的独立拉回积分以及现有输出网格阶梯都进入机器 QA。
最大接口缺陷为 \(1.72\times10^{-14}\)，central/end 点态密度缺陷分别为
\(1.29\times10^{-9}\) 和 \(1.88\times10^{-9}\)，\(K_1\) 直接积分与
central 拉回积分的相对差为 \(1.34\times10^{-7}\)，最后两层网格的最大
相对端点差为 \(3.65\times10^{-7}\)。
同一累计数组上的移动切口只记为 `EXACT/DERIVED` 簿记恒等式，不冒充独立
数值验证。这是所选浮点轨道的 V5 truncated
action 分解，不是端点伴随、交换配对或参数盒上的统一协变性证明。

[V5A 数据](results/vdp_v1_v7/v5a_outer_finite_part.json)把这条候选的 outer
leg 与独立 \(\beta=0\) reference 放在定理要求的固定后置切口
\(Q_*=Q_{\rm label}=100\) 上，而不是在内部 seam \(Q_R=25\) 重新归一化。
由于 \(Q_*\) 后存在 \(O(\delta^{-1})\) 的极薄稳定层，输出采用 cosine
端点加密；801、1601、3201、6401 点的作用量有限截断依次为
\(2.137228,2.139812,2.141233,2.142937\)，最后两层之差为
\(1.70\times10^{-3}\)。6401 点的长度有限截断为
\(-3.22547\times10^{-6}\)。截断、reference 和 exact-gauge 平衡保持在
浮点误差量级；把 V5/V5A 分界移到三个更晚的 \(Q_c\) 时，有限网格公式显式
加入 reference endpoint correction，并保存省略该项的非零负对照。这个余额
是代数簿记检查，不是无穷有限部协变性的独立数值证据。旧值
\(0.879745\) 属于从 \(Q_R\) 开始的同-\(Q\) 实验，不再作为 V5A 定理
归一化的数值代表。这些结果表明数值采样已解析有限边界层并给出
finite-\(Q\) 候选；它们仍不证明 \(Q\to\infty\) 的不定积分极限、混合
二阶 jets 或在参数盒上的统一参考协变性。

当前 v2 energy-preserving centerline 还单独重算了同一对象：在保存点
\(Q_*=100.1711422055\) 到 \(Q=200\) 上，实际 member 与 \(\beta=0\)
reference 的有限相对长度和作用量分别为
\(-1.13057890\times10^{-7}\) 与 `2.14446326497`。四层网格最后变化为
\(1.21\times10^{-14}\) 和 \(2.30\times10^{-7}\)，独立 Simpson--trapezoid
差为 \(4.04\times10^{-15}\) 和 \(7.66\times10^{-8}\)。有限 cut、reference
和 exact-gauge 平衡通过；坐标协变性、无穷极限、指数平坦性和混合 jets
仍明确未计算。

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
`final_status: NOT_RUN`。合同记录的源提交早于提交候选制品后的当前 HEAD；
checker 因而明确给出 `PASS_WITH_ADVANCED_HEAD_WARNING`，并分别报告生成时和
当前工作树的 dirty 状态，而不把当前 checkout 描述成源提交的 clean replay。
可回放输入仍接受逐文件 SHA-256 的严格检查，不能只靠提交号。这正是下一阶段
#7 区间回放的输入接口，而不是把浮点计算升级为严格证明。

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
只是请求/家族元数据。现已提取线性数值特征坐标中的 source--incoming--source
穿越 proxy，但它们尚未绑定到 V2 的精确坐标、V6 边或绝对绕转整数。四个增长窗口也只是
四条通过残差门的全 ODE 有限截断边值解，并不单独认证无穷区间同宿性或唯一性；
也没有验证固定非周期词在公共中心窗口上收敛，因此不能称为数值构造的非周期
双无限轨道。

## 与 Turing 斑纹、canard 和时间稳定性的关系

V1--V7 先令 PDE 的时间导数为零，把问题变成以物理空间 \(\mathsf x\) 为
“时间”的四维可逆 Hamilton ODE。V7 的周期轨道和同宿/多脉冲轨道经反标度
后确实是原 PDE 的**定常空间斑纹**。因此，当前数值结果能具体展示：固定
参数处存在不同空间周期的周期剖面；增加相对绕转会按约 \(0.7109\) 的尺度
增长空间周期；一至四个宏观脉冲的局域剖面可以直接求出。

后续预筛把 Turing 问题进一步分清了。齐次时间线性化的 Fourier 符号满足

\[
 \operatorname{tr}L(k)=-f'(a)-(1+r^4)k^2,
 \qquad
 \det L(k)=r^4k^4+f'(a)k^2+\epsilon.
\]

齐次态时间稳定要求 \(f'(a)>0\)，而某个 \(k>0\) 出现静止零特征值要求
\(f'(a)\leq-2r^2\sqrt{\epsilon}<0\)。所以对本 PDE，**从时间稳定齐次态
产生的经典静止 Turing 机制被精确排除**。这是代数结论，不是扫描所得；它
不排除齐次模已经不稳定时的有限波数增长，也不提供非线性分支或其他选波
机制。V7 的高绕转斑纹来自全局空间动力学，不能再解释为尚未找到的经典
Turing 分支。

时间谱工作已有两项超出预筛。对真实 A2 周期目标，区间验证的自伴算子铅笔
判据证明存在 \(\lambda\in(0.01,2)\) 的共周期正实谱值；对真实
`pulse_1`，整线本质谱边界与同一区间内的离散正实谱值也已严格闭合。一般
半线性桥因此分别给出共周期和局域的非线性轨道不稳定性。其余周期/多脉冲
图册仍只有 `COMPUTED/E1` 离散候选。上述不稳定性排除了“这些目标是吸引子”，
但仍不能断言时间演化会选择另一个具体斑纹。

canard 仍是另一问题。局部高绕转及周期增长来自原点附近的 saddle-focus
旋转和对数 passage，**不是 canard**。在
\((r,\epsilon)=(0.08,1)\) 上，有限边界 \(q_2=-80\) 的 80 段 exact-IVP
多重打靶给出
\(a_2=-0.00833819526698\)、\(T=14.2905556259\)，连续性和端点缺陷均低于
\(1.1\times10^{-11}\)。但固定参数分支的双精度 Jacobian 条件数约为
\(3.9\times10^{16}\)，预先冻结的 simple-zero 交叉检查失败。因此这只是
高质量有限边界 coincidence 候选；尚未以 intrinsic \(W^{cu}\) 入口替换
人工边界，也未识别或包络 maximal-canard 曲线。V4--V5 的远端 outer leg
本身仍与折点保持正距离。

Issue #7 仍验证空间存在、两端、首事件、作用量与编码，而不是时间稳定性。
当前预选盒为

\[
 (r,a_2,\epsilon)\in
 [0.04,0.08]\times[-0.25,0.25]\times[0.8,1.2].
\]

它已正式冻结，且本地 clean outward-rounded 检查已通过 V1/V2(1)、
P2a 与 P2b0；但高阶 jets、完整 V2--V6 与独立 replay 未完成，仍不能称为显式认证的论文
参数盒或全盒时间稳定区。筛查的完整数据、停止规则和四幅 D 系列图见
[动力学预筛报告](VDP_DYNAMICS_SCREENING_REPORT.md)及其
[图合同](VDP_DYNAMICS_FIGURE_CONTRACTS.md)。

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
python3 numerics/run_vdp_dynamics_screening.py
python3 numerics/check_vdp_dynamics_screening.py
python3 validation/check_candidate_contract.py numerics/results/vdp_v1_v7/v6_candidate_contract.json
python3 -m unittest discover -s numerics -p 'test_*.py'
python3 -m unittest discover -s validation -p 'test_*.py'
```

第一条命令重新计算 V1--V7 数据并输出九幅 PDF/SVG/PNG；第二条检查必需
文件、manifest 哈希、NPZ 类型和强制未解析状态；第三、四条生成并检查独立的
时间动力学/Turing/canard 预筛；第五条验证候选合同的 schema 和所有哈希，
但会明确报告没有执行区间证明；最后两条运行数值与验证回归测试。若只需从已
保存数据重绘而不重跑求解器，可运行：

```bash
python3 numerics/render_vdp_figures.py numerics/results/vdp_v1_v7
```
