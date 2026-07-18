param(
    [string]$ResultsDirectory = (Join-Path $PSScriptRoot '..\benchmarks\results'),
    [int]$ExpectedRuns = 3
)

$ErrorActionPreference = 'Stop'

function Get-Median {
    param([object[]]$Values)

    $sorted = @($Values | ForEach-Object { [double]$_ } | Sort-Object)
    if ($sorted.Count -eq 0) {
        throw 'Cannot calculate a median for an empty collection.'
    }

    if (($sorted.Count % 2) -eq 1) {
        return [double]$sorted[[int]([math]::Floor($sorted.Count / 2))]
    }

    return ([double]$sorted[($sorted.Count / 2) - 1] + [double]$sorted[$sorted.Count / 2]) / 2
}

function Get-Range {
    param([object[]]$Values)

    $sorted = @($Values | ForEach-Object { [double]$_ } | Sort-Object)
    return @([double]$sorted[0], [double]$sorted[$sorted.Count - 1])
}

function Assert-Same {
    param(
        [object[]]$Values,
        [string]$Name
    )

    if (@($Values | Select-Object -Unique).Count -ne 1) {
        throw "Benchmark field '$Name' differs between runs."
    }
}

$resultPath = [System.IO.Path]::GetFullPath($ResultsDirectory)
$runFiles = @(Get-ChildItem -LiteralPath $resultPath -Filter 'run-*.json' -File | Sort-Object Name)
if ($runFiles.Count -ne $ExpectedRuns) {
    throw "Expected $ExpectedRuns raw benchmark files in '$resultPath', found $($runFiles.Count)."
}

$runs = @($runFiles | ForEach-Object {
    Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
})

Assert-Same ($runs | ForEach-Object { $_.project }) 'project'
Assert-Same ($runs | ForEach-Object { $_.metric }) 'metric'
Assert-Same ($runs | ForEach-Object { $_.environment.image_id }) 'environment.image_id'
Assert-Same ($runs | ForEach-Object { $_.environment.rows }) 'environment.rows'
Assert-Same ($runs | ForEach-Object { $_.proof.fixture_sha256 }) 'proof.fixture_sha256'
Assert-Same ($runs | ForEach-Object { $_.proof.accepted_sha256 }) 'proof.accepted_sha256'
Assert-Same ($runs | ForEach-Object { $_.proof.quarantine_sha256 }) 'proof.quarantine_sha256'

if (@($runs | Where-Object { $_.failures -ne 0 }).Count -ne 0) {
    throw 'At least one benchmark run reported failures.'
}

$throughputs = @($runs | ForEach-Object { $_.metrics.throughput_rows_per_second })
$durations = @($runs | ForEach-Object { $_.metrics.duration_seconds })
$first = $runs[0]
$aggregate = [ordered]@{
    run_count = $runs.Count
    f1 = Get-Median ($runs | ForEach-Object { $_.metrics.f1 })
    precision = Get-Median ($runs | ForEach-Object { $_.metrics.precision })
    recall = Get-Median ($runs | ForEach-Object { $_.metrics.recall })
    rejected_rows_percent = Get-Median ($runs | ForEach-Object { $_.metrics.rejected_rows_percent })
    reason_exact_match_rate = Get-Median ($runs | ForEach-Object { $_.metrics.reason_exact_match_rate })
    throughput_rows_per_second = Get-Median $throughputs
    throughput_range_rows_per_second = Get-Range $throughputs
    duration_seconds = Get-Median $durations
    duration_range_seconds = Get-Range $durations
}

$summary = [ordered]@{
    project = $first.project
    metric = $first.metric
    value = $aggregate.f1
    unit = $first.unit
    timestamp = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    command = 'docker run --rm -e IMAGE_ID=<image-id> -v <repo>/benchmarks/results:/app/benchmarks/results data-quality-checks:benchmark benchmark --rows 100000 --output /app/benchmarks/results/run-N.json'
    repeat = $runs.Count
    environment = $first.environment
    summary = $aggregate
    metrics = [ordered]@{
        true_positive = $first.metrics.true_positive
        false_positive = $first.metrics.false_positive
        true_negative = $first.metrics.true_negative
        false_negative = $first.metrics.false_negative
        precision = $aggregate.precision
        recall = $aggregate.recall
        f1 = $aggregate.f1
        rejected_rows_percent = $aggregate.rejected_rows_percent
        reason_exact_match_rate = $aggregate.reason_exact_match_rate
        throughput_rows_per_second = $aggregate.throughput_rows_per_second
        duration_seconds = $aggregate.duration_seconds
        reason_counts = $first.metrics.reason_counts
    }
    proof = $first.proof
    raw_outputs = @($runFiles | ForEach-Object { Join-Path 'benchmarks/results' $_.Name })
    runs = $runs
    failures = 0
}

$json = $summary | ConvertTo-Json -Depth 20
[System.IO.File]::WriteAllText(
    (Join-Path $resultPath 'summary.json'),
    $json + [Environment]::NewLine,
    (New-Object System.Text.UTF8Encoding($false))
)

Write-Output "Aggregated $($runs.Count) runs into $(Join-Path $resultPath 'summary.json')"
