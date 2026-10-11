# Benchmark Methodology

## Dataset

The benchmark uses the real DevGPT dataset preserved in the repository under:

- MSc_DataEngineering_Results/DetectAndFix_Data/2025_09_24/DevGPT_v10_snapshot_20240514

## Scope

The current benchmark is based on real vulnerable source examples from the dataset. It includes recorded scanner information and historical repair outputs from LLMs.

## Metrics

- baseline findings
- remaining findings after repair
- findings reduced
- reduction rate
- cases improved
- compiler success
- repair attempts
- verification status

## Historical Results

The project keeps historical values for the following models:

- GPT-5
- GPT-4.1
- Claude Opus

These results are treated as historical benchmark values only. They are not presented as currently running local models.

## Local Benchmark

When local Ollama is installed and a coding model is available, the platform can execute a local benchmark pass and compare real results against the historical dataset.
