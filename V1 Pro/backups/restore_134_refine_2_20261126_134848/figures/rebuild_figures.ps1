$ErrorActionPreference = 'Stop'
$taskManuscriptDir = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $taskManuscriptDir
try {
    python (Join-Path $PSScriptRoot 'kl_dw_comparison\plot_kl_dw_comparison.py')
    if ($LASTEXITCODE -ne 0) { throw 'KL–DW figure export failed.' }
    $taskFigures = @(
        @('response_threshold_band_optimized', 'fig_response_threshold_band'),
        @('residual_input_cells_optimized', 'fig_residual_input_cells'),
        @('joint_partition_optimized', 'fig_joint_partition')
    )
    foreach ($taskFigure in $taskFigures) {
        Push-Location -LiteralPath (Join-Path $PSScriptRoot $taskFigure[0])
        try {
            $taskStem = $taskFigure[1]
            xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error "$taskStem.tex"
            if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $taskStem" }
            pdftoppm -r 180 -singlefile -png "$taskStem.pdf" preview
            if ($LASTEXITCODE -ne 0) { throw "Preview failed: $taskStem" }
            pdftoppm -r 600 -singlefile -png "$taskStem.pdf" $taskStem
            if ($LASTEXITCODE -ne 0) { throw "PNG export failed: $taskStem" }
            pdftocairo -svg "$taskStem.pdf" "$taskStem.svg"
            if ($LASTEXITCODE -ne 0) { throw "SVG export failed: $taskStem" }
        }
        finally { Pop-Location }
    }
}
finally { Pop-Location }
