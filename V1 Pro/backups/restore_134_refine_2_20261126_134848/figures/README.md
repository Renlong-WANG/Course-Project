# Manuscript figure style — current version, 2026-11-26

四图按用户当前设定的页面比例优化，插入宽度保持 65%、50%、60%、60%，通过放大源图字号补偿缩放。正文实际栏宽为 495 TeX pt，正文正常字号为 10.95 TeX pt。

## 字号与尺寸核验

| Figure | 正文宽度比例 | 插入宽度 | 源图主要字号 | 插入后主要字号 |
|---|---:|---:|---:|---:|
| 1 | 0.65 | 113.08 mm | 18.20 pt | 10.950 pt |
| 2 | 0.50 | 86.99 mm | 17.33 pt | 10.949 pt |
| 3 | 0.60 | 104.38 mm | 14.44 pt | 10.951 pt |
| 4 | 0.60 | 104.38 mm | 14.44 pt | 10.951 pt |

主要文字及图例采用约 10.95 pt，与正文一致；Figure 1 放大图的刻度和内部辅助标注约为 9.5 pt。正文与四图均使用 Latin Modern 字体家族。字号既按 PDF 物理尺寸反算，也从文章 PDF 的字体记录核对。详细数值见 `typography_calibration.json`。

## 统一的视觉规则

- 四图均使用浅灰细框，最终线宽约 0.5 pt；图例保持居中。
- 深灰文字：`#253139`；蓝色边界/标题：`#52758A`；浅蓝：`#D5E6F1`；金黄色：`#F7E6AF`；浅红：`#EFC6C1`；细框：`#C9D2D8`。
- Figure 1 保留单行图例的既定顺序，蓝色色块与金黄色块相加的图示仍位于 DW only 与 p=q 之间。参数标注分行以保留正文大小的字体。
- Figure 2 保留原始示意函数，改为矢量 PDF，并使用居中的三列图例；较长的图例文字换行。
- Figure 3 端点图例整体居中，保留全部开闭端点含义。
- Figure 4 三类图例采用居中三列，将类别与索引条件分为两行，避免通过缩小字体挤进原宽度。

## 当前文章效果

当前主稿 `../manuscript.pdf` 为 19 页。Figure 1、2、3、4 分别位于第 4、7、8、10 页，图片、图注与后续正文的衔接已逐页检查，交叉引用已解析。

`four_figure_style_review.pdf` 将四图按文章中的实际插入宽度排放，并附正文大小的对照文字，便于横向比较。各文件夹的 `manuscript_page_preview.png` 显示实际文章页面。

## 科学内容和原稿

KL–DW 数值边界 CSV 与优化前逐字节一致。响应阈值置信带使用提供的原函数，单调性、上下界嵌套及 c=0 切片已核验。两张划分图的单元、端点和分类含义保持不变。

文章正文、公式、证明、引用文献和四幅图注保持原样；主稿仅将 Figure 2 的旧 PNG 引用替换为新 PDF。用户当前设置的四个插图宽度比例均保留。

本轮修改前的完整备份：`../backups/four_figure_typography_20261126_132535/`。

## 可编辑源文件与重建

- Figure 1：`kl_dw_comparison/plot_kl_dw_comparison.py`。
- Figure 2：`response_threshold_band_optimized/fig_response_threshold_band.tex`。
- Figure 3：`residual_input_cells_optimized/fig_residual_input_cells.tex`。
- Figure 4：`joint_partition_optimized/fig_joint_partition.tex`。
- 三份 TikZ 文件共用 `manuscript_figure_style.tex`；请保留文件夹结构。

运行 `rebuild_figures.ps1` 可重建四图的 PDF、SVG、600 dpi PNG 和预览。若以后改变正文栏宽或 includegraphics 的宽度比例，需要相应调整源图字号；当前校准针对上表比例。
