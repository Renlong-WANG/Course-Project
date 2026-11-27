# Figure 3: Joint partition

## 设计和数学含义

Figure 3 已重绘为与 Figure 2 一致的 TikZ 矢量图，采用相同的 13.6 cm 框宽、0.55 pt 浅灰细框、圆角、分隔线、Times New Roman 正文字体和 STIX Two Math 数学字体。两张图都以 `0.86\columnwidth` 插入稿件。

保持 4 个输入单元、7 个残差单元及全部 28 个联合单元的原有定义、方向和标记。每格质量为 $\pi_{ij}=\Pi(\mathcal X_i\times\Xi_j)$；横轴为 $i=0,\ldots,3$，纵轴向上递增为 $j=1,\ldots,7$。

- 浅蓝 `#D5E6F1`：Safe，$j\ge2i+2$，12 个单元。
- 浅金黄 `#F7E6AF`：Overlap，$j=2i+1$，4 个单元。
- 浅红 `#EFC6C1`：Failure，$j\le2i$，12 个单元。

分类严格采用稿件中 $\underline h_{ij}=\mathbf1_{\{j\le2i\}}$ 和 $\overline h_{ij}=\mathbf1_{\{j\le2i+1\}}$ 的定义。

图例以整个“色块 + 文字 + 公式”组合居中，居中基准为外框中心，不是逐项左对齐。Figure 2 的端点图例也已同步改为整体居中。

## 稿件中的效果

已将 `../../manuscript.tex` 的 Figure 3 图片路径替换为新 PDF，原图注和科学正文保持不变。重新编译并核查：Figure 2 在第 8 页、Figure 3 在第 9 页；图注和正文衔接正常，文字及图例未裁切，全文仍为 18 页，交叉引用已解析。

```latex
\includegraphics[width=0.86\columnwidth]{figures/joint_partition_optimized/fig_joint_partition.pdf}
```

修改前的稿件及 Figure 2 备份：`../../backups/figure3_style_and_centered_legends_20261126_125616/`。原始 `../../fig_joint_partition.png` 未覆盖。

## 交付文件

- `fig_joint_partition.tex`：可编辑 TikZ 源文件。
- `fig_joint_partition.pdf`：矢量 PDF，字体已嵌入。
- `fig_joint_partition.svg`：矢量 SVG，字形为路径；编辑文字请使用 TeX。
- `fig_joint_partition.png`：600 dpi PNG。
- `preview.png`：独立图片预览。
- `manuscript_page_preview.png`：稿件第 9 页的实际排版预览。

## 重新生成

```powershell
xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error fig_joint_partition.tex
pdftoppm -r 180 -singlefile -png fig_joint_partition.pdf preview
pdftoppm -r 600 -singlefile -png fig_joint_partition.pdf fig_joint_partition
pdftocairo -svg fig_joint_partition.pdf fig_joint_partition.svg
```

## Alt text

A framed matrix shows four input cells as columns and seven residual cells as rows, with row indices increasing upward. Each of the 28 cells displays its joint probability mass. Blue cells are uniformly safe, red cells are uniformly failing, and four gold cells form the overlap boundary where the failure status may vary. The three-item legend is centered beneath the matrix and states each class's index condition.
