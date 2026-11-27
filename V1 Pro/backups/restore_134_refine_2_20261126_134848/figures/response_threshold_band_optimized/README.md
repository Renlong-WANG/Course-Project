# Figure 2: Response-threshold confidence band

本图根据用户提供的 `E:/网页下载/fig_response_threshold_band.tex` 优化，下载目录中的原始文件保持不变。统一的四图设置见上一级 `README.md`。

采用与其余三图一致的 Latin Modern 字体、浅灰细框、深灰文字、浅蓝置信带及金黄色区间。底部三项图例分为三个居中列，文字换行以适应用户当前设定的 `0.50\columnwidth`，主要文字插入后约为正文的 10.95 pt。

保留原有示意曲线：

\[
U(c)=\frac{1}{1+e^{-1.35(c+1.1)}},\quad
F(c)=\frac{1}{1+e^{-1.35c}},\quad
L(c)=\frac{1}{1+e^{-1.35(c-1.1)}}.
\]

三者均单调，且对每个 c 满足 L(c)≤F(c)≤U(c)。金黄色竖向区间为 c=0 处的精确切片。曲线仅用于示意，不表示新增的实证结果。

主稿引用：

```latex
\includegraphics[width=0.5\columnwidth]{figures/response_threshold_band_optimized/fig_response_threshold_band.pdf}
```

当前插入位置为 PDF 第 7 页。PDF 是矢量图，已替换主稿中的旧 PNG；图注保持不变。

`fig_response_threshold_band.tex` 为可编辑源文件，依赖上一级的 `manuscript_figure_style.tex`。其他交付包括 PDF、SVG、600 dpi PNG、`preview.png` 和实际文章页面的 `manuscript_page_preview.png`。SVG 中字形为路径；编辑文字请使用 TeX 源文件。

统一重建脚本：上一级 `rebuild_figures.ps1`。

Alt text: A monotone response CDF lies inside a blue simultaneous confidence band. Upper and lower boundaries are labeled directly. A gold vertical segment at c=0 shows the original scalar probability interval. A centered three-column legend identifies the band, true CDF, and scalar interval.
