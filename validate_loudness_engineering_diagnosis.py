import json

from loudness_engineering_diagnosis import (
    run_diagnostics
)


# ---------------------------------------------------------
# Test helpers
# ---------------------------------------------------------

def build_parameter(
    z_score,
    direction,
    classification
):
    """
    Build a simplified loudness deviation parameter.
    """

    return {
        "user_value": 0.0,
        "reference_mean": 0.0,
        "reference_std_dev": 1.0,
        "difference": 0.0,
        "z_score": z_score,
        "direction": direction,
        "classification": classification
    }


def build_report(
    lufs,
    lufs_direction,
    lufs_classification,
    rms,
    rms_direction,
    rms_classification,
    peak,
    peak_direction,
    peak_classification,
    lra,
    lra_direction,
    lra_classification
):
    """
    Build a controlled loudness deviation report.
    """

    return {
        "parameters": {
            "integrated_lufs": build_parameter(
                lufs,
                lufs_direction,
                lufs_classification
            ),

            "estimated_true_peak_dbtp": build_parameter(
                peak,
                peak_direction,
                peak_classification
            ),

            "rms_dbfs": build_parameter(
                rms,
                rms_direction,
                rms_classification
            ),

            "loudness_range_lu": build_parameter(
                lra,
                lra_direction,
                lra_classification
            )
        }
    }


# ---------------------------------------------------------
# Test 1
# Overall level reduction
# ---------------------------------------------------------

def test_overall_level_reduction():

    report = build_report(
        -4.0,
        "below_reference",
        "extreme_deviation",

        -4.0,
        "below_reference",
        "extreme_deviation",

        -4.0,
        "below_reference",
        "extreme_deviation",

        0.2,
        "above_reference",
        "within_reference"
    )

    diagnoses = run_diagnostics(
        report
    )

    issues = {
        diagnosis["issue"]
        for diagnosis in diagnoses
    }

    passed = (
        "overall_level_reduction"
        in issues
    )

    print(
        "TEST 1 - OVERALL LEVEL REDUCTION: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    return passed


# ---------------------------------------------------------
# Test 2
# Reduced loudness range
# ---------------------------------------------------------

def test_reduced_loudness_range():

    report = build_report(
        0.0,
        "balanced",
        "within_reference",

        0.0,
        "balanced",
        "within_reference",

        0.0,
        "balanced",
        "within_reference",

        -2.0,
        "below_reference",
        "significant_deviation"
    )

    diagnoses = run_diagnostics(
        report
    )

    issues = {
        diagnosis["issue"]
        for diagnosis in diagnoses
    }

    passed = (
        "reduced_loudness_range"
        in issues
    )

    print(
        "TEST 2 - REDUCED LOUDNESS RANGE: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    return passed


# ---------------------------------------------------------
# Test 3
# Expanded loudness range
# ---------------------------------------------------------

def test_expanded_loudness_range():

    report = build_report(
        0.0,
        "balanced",
        "within_reference",

        0.0,
        "balanced",
        "within_reference",

        0.0,
        "balanced",
        "within_reference",

        2.0,
        "above_reference",
        "significant_deviation"
    )

    diagnoses = run_diagnostics(
        report
    )

    issues = {
        diagnosis["issue"]
        for diagnosis in diagnoses
    }

    passed = (
        "expanded_loudness_range"
        in issues
    )

    print(
        "TEST 3 - EXPANDED LOUDNESS RANGE: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    return passed


# ---------------------------------------------------------
# Test 4
# Elevated peak level
# ---------------------------------------------------------

def test_elevated_peak_level():

    report = build_report(
        0.0,
        "balanced",
        "within_reference",

        0.0,
        "balanced",
        "within_reference",

        2.5,
        "above_reference",
        "significant_deviation",

        0.0,
        "balanced",
        "within_reference"
    )

    diagnoses = run_diagnostics(
        report
    )

    issues = {
        diagnosis["issue"]
        for diagnosis in diagnoses
    }

    passed = (
        "elevated_peak_level"
        in issues
    )

    print(
        "TEST 4 - ELEVATED PEAK LEVEL: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    return passed


# ---------------------------------------------------------
# Run tests
# ---------------------------------------------------------

def main():

    print()
    print("========================================")
    print("LOUDNESS DIAGNOSIS VALIDATION")
    print("========================================")
    print()

    results = [
        test_overall_level_reduction(),
        test_reduced_loudness_range(),
        test_expanded_loudness_range(),
        test_elevated_peak_level()
    ]

    passed = sum(
        results
    )

    total = len(
        results
    )

    print()
    print("========================================")
    print("VALIDATION SUMMARY")
    print("========================================")
    print()

    print(
        f"Tests passed: {passed}/{total}"
    )

    print()

    if passed == total:

        print(
            "LOUDNESS ENGINEERING DIAGNOSIS: PASS"
        )

    else:

        print(
            "LOUDNESS ENGINEERING DIAGNOSIS: FAIL"
        )

    print()


if __name__ == "__main__":
    main()