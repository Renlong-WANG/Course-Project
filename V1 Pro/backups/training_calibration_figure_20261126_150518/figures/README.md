# Current manuscript figures — 2026-11-26

图注最新调整：四图均采用“加粗的简短标题短语 + 精炼说明”。完整当前文字见 `captions.md`；图片、字号、图例和插入比例不变，已检查四幅图注的实际换行和页面效果。

最新调整：Figure 1 增加边框内的上下留白，重点留出底部图例空间，并在横坐标标题与图例之间加入浅灰细分隔线。主要绘图区、字号、图宽和 0.65\columnwidth 插入比例保持不变；仅略增加图高容纳留白。Figure 1 的文中第 4 页效果已核查。

本轮按用户反馈，将 Figure 1、3、4 恢复到上一轮整体放大字号之前的原始版本。PDF、PNG、SVG 及可编辑绘图源文件均从 `../backups/four_figure_typography_20261126_132535/figures/` 原样恢复；图形文件的字节一致性已核对。

Figure 2 单独参照这些图片修改，使用 Times New Roman 与 STIX Two Math，恢复适度的字体比例。源图正文标注为 12 pt，轴标题 12.8 pt，刻度 11.4 pt，图例 10.8 pt；不再采用上一轮的 17.33 pt 大字号。图例为单行整体居中，保留浅灰细框、浅蓝置信带和金黄色 c=0 区间，并适当压缩了上下留白。

## 当前文章插入比例与页码

| Figure | 内容 | 正文宽度比例 | PDF 页码 |
|---|---|---:|---:|
| 1 | KL–DW 比较 | 0.65 | 4 |
| 2 | 响应阈值置信带 | 0.50 | 7 |
| 3 | 残差与输入阈值划分 | 0.60 | 8 |
| 4 | 联合划分 | 0.60 | 10 |

四个插入宽度保持用户当前设置。当前主稿为 19 页，正文、公式和证明保持不变，图注已按最新要求精简；重新编译并检查了图片、图号、交叉引用和页面效果。

`four_figure_style_review.pdf` 是当前四图按文章实际比例排放的对照 PDF；各图片文件夹中的 `manuscript_page_preview.png` 为实际文章页面。

## 可编辑源文件

- Figure 1：`kl_dw_comparison/plot_kl_dw_comparison.py`。
- Figure 2：`response_threshold_band_optimized/fig_response_threshold_band.tex`。
- Figure 3：`residual_input_cells_optimized/fig_residual_input_cells.tex`。
- Figure 4：`joint_partition_optimized/fig_joint_partition.tex`。

可用 `rebuild_figures.ps1` 重建四图。三份当前 TikZ 文件都使用各自的 Times/STIX 字体设置。上一轮的“与正文同字号”设置已撤回，当前核验记录见 `typography_calibration.json`。

本轮开始时的完整备份：`../backups/restore_134_refine_2_20261126_134848/`。
