# KL–DW figure insertion — 2026-11-26

## Inserted English paragraph

```latex
Figure~\ref{fig-kl-dw-comparison} compares the KL and DW pointwise acceptance regions at a common sample size and threshold. Since $\psi(q,p)\ge0$, the KL constraint $N^{\mathrm{te}}\phi(q,p)\le\theta$ implies the DW constraint $N^{\mathrm{te}}\phi(q,p)-\psi(q,p)\le\theta$. The additional gold region contains probabilities accepted by DW and excluded by KL, with the left-tail enlargement shown in the inset. The ambiguity set in \eqref{eq-cdf-ambiguity-set} imposes the DW constraint simultaneously over all residual thresholds. The figure uses an illustrative threshold; finite-sample confidence coverage requires the calibration below.
```

## Inserted caption

```latex
Comparison of KL and DW pointwise probability acceptance regions for common illustrative parameters $N^{\mathrm{te}}=100$, $\theta=3$, and $s=\nu=1$. Blue denotes the KL region; blue and gold together denote the DW region. The inset magnifies the left tail. Solid blue and dashed gold boundaries are obtained by numerical inversion; the dotted line is $p=q$. Continuous acceptance envelopes are shown, with empirical CDF levels restricted to $j/N^{\mathrm{te}}$.
```

## 位置和论证

比较图放在第 3 节 Ambiguity Set Design 的 DW 模糊集定义（Definition 1）之后、阈值校准之前。此处 q、p、N^te 和 theta 均已定义，读者可先理解多尺度修正如何改变逐点接受域，再进入置信阈值校准。

同时修订修正项说明：当 q、p 之间的区间包含 1/2 时，psi(q,p)=0；当两者同时深入同一尾部时，修正增大。图中金色区域的描述明确为 DW 接受而 KL 排除的概率。

图中 N^te=100、theta=3、s=nu=1 为示意参数。共同阈值用于比较接受域几何形状；有限样本置信覆盖仍依赖原稿 Proposition 1 的校准。逐点接受域与对所有残差阈值同时施加约束的完整分布模糊集已区分。

## Terminology ledger

| Canonical notation / term | Meaning | Decision |
|---|---|---|
| Bernoulli KL divergence, phi(q,p) | 局部概率偏差 | 沿用原稿定义，不改为完整分布之间的 KL 散度 |
| DW multiscale correction, psi(q,p) | 非负多尺度修正 | 沿用原稿定义 |
| q / p | 经验概率 / 候选概率 | 与图中坐标和原稿一致 |
| N^te / theta | 测试样本量 / 接受阈值 | 共同示意阈值与置信校准阈值明确区分 |

## Claim–evidence check

| Claim | Evidence | Status |
|---|---|---|
| 相同 N^te、theta 下 KL 逐点接受域包含于 DW 接受域 | psi(q,p)>=0，直接代入两类约束 | 由定义支持 |
| 金色区域为 DW 额外接受域，左尾放大显示差异 | 既有图形及数值边界 CSV/JSON | 已核对 |
| 置信覆盖需要校准阈值 | 原稿 Proposition 1 | 理论内容保持原样 |

## Current figure numbering and layout

| Figure | Content | PDF page |
|---|---|---|
| 1 | KL–DW comparison | 4 |
| 2 | Simultaneous response-threshold band | 7 |
| 3 | Residual and input-threshold partitions | 8 |
| 4 | Joint partition | 10 |

稿件编译为 19 页，交叉引用已解析。已目视检查比较图及后续两张划分图的插入效果。既有三张图片及其图注保持不变；只增加新图及图注，修订修正项说明，并加入比较段落。全部正式公式、定义、定理、命题、推论及证明保持原样，引用文献键保持不变。

备份：`../../backups/insert_kl_dw_comparison_20261126_130743/`。
