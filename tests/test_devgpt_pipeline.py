from backend.app.benchmark.benchmark_service import BenchmarkService
from backend.app.scanners.scanner_manager import scanner_manager


def test_dataset_case_is_real():
    case = BenchmarkService().get_case_detail("File_01")
    assert case is not None
    assert "original_code" in case
    assert len(case["findings"]) > 0
    assert case["target_file"]


def test_scanner_manager_handles_local_scan():
    result = scanner_manager.scan_code(
        "#include <string.h>\nint main(){char b[8]; strcpy(b, \"hello\"); return 0;}\n",
        "c",
        filename="sample.c"
    )
    assert result.language == "c"
    assert result.filename.endswith(".c")
    assert result.scanners_executed or result.scanners_unavailable


def test_benchmark_listing_contains_real_cases():
    cases = BenchmarkService().get_all_cases()
    assert len(cases) >= 1
    assert any(item["case_id"] == "File_01" for item in cases)
