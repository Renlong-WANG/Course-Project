# Current manuscript figures — 2026-11-26

新增 Figure 1：训练与独立校准采样的单坐标系示意图。蓝色方形表示空间设计与边界附近主动选取的训练点；绿色圆点表示从示意输入分布独立同分布抽取的校准点。虚线为输入密度等高线，红线为极限状态边界，浅红区域为失效域。图件为概念示意，不对应数值实验结果。

Figure 1 最新样式与其余图件统一：浅灰圆角外框、横向细分隔线、居中的单行图例及带箭头的两条坐标轴。按正文实际插入尺寸，图内标注约 7.53 pt，轴标签约 8.07 pt，图例约 6.81 pt（其余图例为 6.80–6.92 pt）。已检查整页和实际尺寸预览。示意点、密度和失效边界不变；文章插入比例仍为 0.70。

五幅图均采用常规字重的简洁英文标题和必要说明，图注中不使用加粗格式；当前图注见 captions.md。图片及插入宽度保持不变。主稿已编译为 20 页，图件、图注及交叉引用已检查。

## 当前文章插入比例与页码

| Figure | 内容 | 正文宽度比例 | PDF 页码 |
|---|---|---:|---:|
| 1 | 训练与独立校准采样 | 0.70 | 2 |
| 2 | KL–DW 比较 | 0.65 | 5 |
| 3 | 响应阈值置信带 | 0.50 | 8 |
| 4 | 残差与输入阈值划分 | 0.60 | 9 |
| 5 | 联合划分 | 0.60 | 11 |

## 可编辑源文件与重建

- Figure 1：training_calibration_sampling/plot_training_calibration_sampling.py。
- Figure 2：kl_dw_comparison/plot_kl_dw_comparison.py。
- Figure 3：response_threshold_band_optimized/fig_response_threshold_band.tex。
- Figure 4：residual_input_cells_optimized/fig_residual_input_cells.tex。
- Figure 5：joint_partition_optimized/fig_joint_partition.tex。

可用 rebuild_figures.ps1 重建五幅图。新增采样图提供 PDF、可编辑 SVG、600 dpi PNG/TIFF、预览图、概念点坐标及绘图参数。绘图脚本按固定参数生成示意分布和点位，并完整导出所有点。

## 字体与核验

新增图沿用既有图件的 Times New Roman/STIX 字体。独立 PDF 最小字形为 6.3 pt，正文实际插入后约 5.65 pt，已通过字形大小及渲染碰撞检查。单面板无需多面板对齐检查；核验记录见新增图目录的 QA_NOTES.md 和 typography_calibration.json。

four_figure_style_review.pdf 保留原四幅图（现 Figure 2–5）的排版对照，未包含新增采样图。新增图在主稿中的页面预览保存在其目录下的 manuscript_page_preview.png。

