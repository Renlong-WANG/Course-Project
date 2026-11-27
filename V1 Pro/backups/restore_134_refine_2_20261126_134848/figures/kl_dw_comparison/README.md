# KL 与 DW 可行概率范围对比图

最新统一排版设置以 `../README.md` 为准：正文与插图主要文字约为 10.95 pt，字体为 Latin Modern；用户当前宽度比例和数值校准见上一级说明。

已插入当前 `V1 Pro/manuscript.tex` 第 3 节，作为 Figure 1 显示于 PDF 第 4 页；全文为 19 页。段落修改、术语和核验说明见 `insertion_notes.md`，文中效果见 `manuscript_page_preview.png`。

已绘制“全概率尺度主图 + 左尾局部放大图”。图中的颜色取自当前 `V1 Pro` 稿件的 `fig_response_threshold_band.png` 和 `fig_joint_partition.png`：浅蓝 `#D5E6F1`、浅金黄 `#F7E6AF`、深灰 `#253139`。蓝色实线为 KL 边界，金黄色虚线为 DW 边界，深灰点线表示 p=q。

主图不显示面板标记或 “Full probability scale”；放大图标题只保留 “Left-tail detail”。底部图例为同一行，顺序为 KL feasible、DW only、蓝色色块 + 金黄色块 = DW feasible、p=q。

- 蓝色：满足 KL 约束的候选概率。
- 金黄色：满足 DW 约束、但不满足 KL 约束的额外候选概率。
- 蓝色与金黄色之和：满足 DW 约束的候选概率。

## 数学定义和参数

定义逐项采用 `../../manuscript.tex` 中的 Bernoulli KL 散度和 DW 修正：

\[
\phi(q,p)=q\log(q/p)+(1-q)\log[(1-q)/(1-p)],
\]

\[
\rho(v)=\log\log\frac{e}{4v(1-v)},\quad
\omega(v)=\log(1+\rho(v)^2),\quad
\psi(q,p)=\min_{v\in[\min(q,p),\max(q,p)]}[\rho(v)+\omega(v)].
\]

两种可行域分别为

\[
\mathcal A_{\rm KL}=\{(q,p):N^{\mathrm{te}}\phi(q,p)\le\theta\},\qquad
\mathcal A_{\rm DW}=\{(q,p):N^{\mathrm{te}}\phi(q,p)-\psi(q,p)\le\theta\}.
\]

本图使用示意参数 N^te=100、theta=3、s=nu=1。两种约束固定相同的 N^te 和 theta，以展示多尺度修正的作用。theta=3 未作置信水平校准。本图表示单个阈值处的概率接受范围；完整的分布模糊集要求所有残差阈值同时满足对应约束。

横轴连续显示 q 的接受包络，以便阅读；固定样本量时，经验 CDF 实际取值为 j/N^te。局部放大范围为 q∈[0,0.03]、p∈[0,0.11]，与主图左下角的虚线矩形完全一致。

## 数值计算和核验

所有非退化边界通过 Brent 法数值求解完整约束方程，不使用二次近似；求解变量为 logit(p)，以提高尾部计算的稳定性。概率端点采用原稿中的边界约定。右半区使用约束在 (q,p)→(1−q,1−p) 下的对称性，由左半区数值根反射得到。

共输出 3,441 个 q 网格点，检查包括：边界方程残差、KL 可行域包含于 DW 可行域、独立计算的 q=0 与 q=1/2 KL 闭式端点，以及修正项区间最小值的密集网格核验。当前最大边界方程残差约为 2.95×10^−12。

在 q=0 处，KL 的候选概率上界约为 0.02955447，DW 的上界约为 0.04599864。在 q=1/2 处，两种约束的边界一致。

CSV 同时保留边界概率及其自然对数；极小概率在普通浮点概率列中可能下溢为 0，其有限对数值保留在对应的 log 列。JSON 记录原稿哈希、参数、软件版本、配色和数值核验结果。

## 文件

- `fig_kl_dw_ambiguity_comparison.pdf`：矢量 PDF，适合 LaTeX 插图，TrueType 字体已嵌入。
- `fig_kl_dw_ambiguity_comparison.svg`：矢量 SVG；编辑文字建议使用 Python 源文件。
- `fig_kl_dw_ambiguity_comparison.png`：600 dpi PNG，宽 4440 像素，上下空白已裁切。
- `preview.png`：180 dpi 预览。
- `fig_kl_dw_ambiguity_comparison.csv`：数值边界。
- `fig_kl_dw_ambiguity_comparison.json`：计算与导出记录。
- `plot_kl_dw_comparison.py`：可复现的计算和绘图代码。

原画布为 7.4×6.4 英寸，导出时仅裁切上下多余空白，保留约 0.07 英寸边距；宽度及图内内容、字号和相对位置保持不变，最终尺寸见 JSON。图片按一般论文插图制作，未按某一特定期刊要求验证。已将本图插入稿件并补充说明；图形文件及其他现有图片保持不变。

重新生成（需要 NumPy、SciPy、Matplotlib 和 Pillow）：

```powershell
python .\plot_kl_dw_comparison.py
```

修改示意参数的示例：

```powershell
python .\plot_kl_dw_comparison.py --n 200 --theta 3 --outdir .\N200
```

## Suggested English caption

Comparison of KL- and DW-based pointwise probability acceptance regions for common illustrative N^te=100, theta=3, and s=nu=1. The inset magnifies the left tail. Blue shading denotes probabilities satisfying the KL constraint, whereas gold shading denotes additional probabilities accepted by the DW constraint but excluded by the KL constraint. The union of the blue and gold regions is the DW acceptance region. Solid blue and dashed gold curves are obtained by numerical inversion of the corresponding constraint equations; the dotted line indicates p=q. A common illustrative threshold is used to isolate the effect of the multiscale correction.

## 中文图注

KL 型与 DW 型逐点概率接受域对比，示意参数为 N^te=100、theta=3、s=nu=1。主图展示全概率尺度下的可行域，放大图展示左尾小概率区域。蓝色区域为 KL 型约束允许的概率范围；金黄色区域为 DW 型约束额外接受、但被 KL 型约束排除的概率范围。蓝色与金黄色区域的并集为 DW 型约束允许的概率范围。蓝色实线和金黄色虚线分别通过数值求解相应约束方程获得，深灰点线表示 p=q。两类约束使用相同的示意阈值，以展示多尺度修正的作用。

## LaTeX 插图示例

```latex
\begin{figure}[!htbp]
  \centering
  \includegraphics[width=0.65\columnwidth]{figures/kl_dw_comparison/fig_kl_dw_ambiguity_comparison.pdf}
  \caption{Comparison of KL- and DW-based pointwise probability acceptance regions. Blue shading denotes the KL region, and gold shading denotes the additional DW region. The union of both colors gives the DW region. The inset magnifies the left tail. Boundaries are obtained by numerical inversion with common illustrative parameters $N^{\mathrm{te}}=100$, $\theta=3$, and $s=\nu=1$.}
  \label{fig-kl-dw-comparison}
\end{figure}
```

## Alt text

A probability-versus-probability plot shows a blue KL acceptance band around the diagonal p=q, with a surrounding narrow gold region added by the DW multiscale correction. The bands coincide near the center and differ most clearly near the probability boundaries. An inset magnifies q from zero to 0.03 and p from zero to 0.11, showing that the DW upper endpoint exceeds the KL upper endpoint in the left tail.
