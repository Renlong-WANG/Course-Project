# Residual and input-threshold partition figure

插入 KL–DW 比较图后，本图在最新稿件中编号为 Figure 3（原 Figure 2）；最新页码及插图位置已在下文同步。

## 设计调整

根据 `E:/网页下载/fig_a_residual_input_cells.tex` 和用户提供的稿件截图重新排版；下载目录中的原始 TeX 文件未修改。

- 使用 0.55 pt 浅灰细框归拢整张图，两条浅灰分隔线区分残差划分、输入阈值划分和端点图例。
- 采用横向布局，减少纵向空散感；删除原始文件中的总标题和面板编号。
- 标题沿用全文深蓝灰色，正文和轨道采用深灰色。字体为 Times New Roman 和 STIX Two Math。
- 三个残差切分点在两个区域中严格对齐；空心、实心端点和单点残差保持原有含义。各区间的左右开闭方式及 $w_i$ 标注未改变。
- 图例以“标记 + 文字”的完整组合居中，与 Figure 4 的居中方式一致。
- 插入稿件时使用 `0.86\columnwidth`，替换之前的 `0.5\columnwidth`，改善文字和端点的可读性。

示意图中的切分点等间距仅用于说明划分关系，不表示实际观测值的数值间距。

## 已更新的稿件

已更新 `../../manuscript.tex` 的 Figure 3 图片引用，并重新编译 `../../manuscript.pdf`。首次优化本图时，正文源文件只修改一行 `\includegraphics`；图注、浮动参数及科学内容保持原样。新版图片位于第 8 页，后接原有证明，整篇为 19 页，交叉引用已解析。

原稿备份：`../../backups/figure2_layout_20261126_125209/`。

Figure 3 图例居中及 Figure 4 同风格优化前的共同备份：`../../backups/figure3_style_and_centered_legends_20261126_125616/`。最新稿件中 Figure 3 仍位于第 8 页，Figure 4 位于第 10 页。

```latex
\includegraphics[width=0.86\columnwidth]{figures/residual_input_cells_optimized/fig_residual_input_cells.pdf}
```

## 交付文件

- `fig_residual_input_cells.tex`：可编辑 TikZ 源文件，使用 XeLaTeX 编译。
- `fig_residual_input_cells.pdf`：矢量 PDF，字体已嵌入，适合直接插入文章。
- `fig_residual_input_cells.svg`：矢量 SVG，字形为路径；编辑文字请使用 TeX 源文件。
- `fig_residual_input_cells.png`：600 dpi PNG，3251×1751 像素。
- `preview.png`：独立图片预览。
- `manuscript_page_preview.png`：实际稿件第 8 页预览。

PDF 图幅约为 137.6×74.1 mm，已包含紧凑边距。未按特定期刊规则进行格式认证。

## 重新生成

在本文件夹中运行：

```powershell
xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error fig_residual_input_cells.tex
pdftoppm -r 180 -singlefile -png fig_residual_input_cells.pdf preview
pdftoppm -r 600 -singlefile -png fig_residual_input_cells.pdf fig_residual_input_cells
pdftocairo -svg fig_residual_input_cells.pdf fig_residual_input_cells.svg
```

## Alt text

A framed diagram shows the residual partition above the input-threshold partition for three ordered test residuals. The upper track contains four open intervals and three singleton cells, for seven residual cells. The lower alternating tracks contain four input cells, with each finite interval including its left endpoint and excluding its right endpoint. Dashed vertical guides align the cut values. An open circle indicates an excluded endpoint; a filled circle indicates an included endpoint or singleton.
