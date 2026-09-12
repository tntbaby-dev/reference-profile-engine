from recommendation_engine import generate_recommendation


# ---------------------------------------------------------
# Test helpers
# ---------------------------------------------------------

def build_source(
    stem,
    score,
    bands
):
    """
    Build a simplified source-level diagnosis entry.
    """

    return {
        "stem": stem,
        "weighted_score": score,
        "bands": bands
    }


def build_band(
    band,
    contribution_percent,
    direction,
    evidence_type
):
    """
    Build one source contribution record.
    """

    return {
        "band": band,
        "contribution_percent":
            contribution_percent,
        "z_score": 2.5,
        "deviation_direction":
            direction,
        "evidence_type":
            evidence_type
    }


def build_diagnosis(
    issue,
    ranked_sources
):
    """
    Build a simplified source-level diagnosis.
    """

    return {
        "issue": issue,
        "priority": "primary",
        "severity": "high",
        "confidence": "high",
        "diagnosis":
            "Controlled validation diagnosis.",
        "ranked_sources":
            ranked_sources
    }


# ---------------------------------------------------------
# Test 1
# Excess low-mid energy
# ---------------------------------------------------------

def test_low_mid_excess():

    diagnosis = build_diagnosis(
        "low_frequency_distribution_imbalance",
        [
            build_source(
                "test_drums.wav",
                700.0,
                [
                    build_band(
                        "low_mid",
                        70.0,
                        "above_reference",
                        "supports_excess_energy_diagnosis"
                    )
                ]
            ),
            build_source(
                "test_music.wav",
                250.0,
                [
                    build_band(
                        "low_mid",
                        25.0,
                        "above_reference",
                        "supports_excess_energy_diagnosis"
                    )
                ]
            )
        ]
    )

    result = generate_recommendation(
        diagnosis
    )

    expected_action = (
        "investigate_low_mid_excess"
    )

    passed = (
        result["action"]
        == expected_action
    )

    print(
        f"TEST 1 - LOW-MID EXCESS: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    if not passed:
        print(
            f"  Expected: {expected_action}"
        )

        print(
            f"  Received: {result['action']}"
        )

    return passed


# ---------------------------------------------------------
# Test 2
# Reduced high-frequency energy
# ---------------------------------------------------------

def test_high_frequency_deficiency():

    diagnosis = build_diagnosis(
        "reduced_high_frequency_energy",
        [
            build_source(
                "test_drums.wav",
                60.0,
                [
                    build_band(
                        "presence",
                        80.0,
                        "below_reference",
                        "available_energy_source"
                    ),
                    build_band(
                        "brilliance",
                        95.0,
                        "below_reference",
                        "available_energy_source"
                    )
                ]
            )
        ]
    )

    result = generate_recommendation(
        diagnosis
    )

    expected_action = (
        "investigate_high_frequency_deficiency"
    )

    passed = (
        result["action"]
        == expected_action
    )

    recommendation = (
        result["recommendation"]
    )

    correctly_avoids_causality = (
        "does not establish a specific stem"
        in recommendation
    )

    passed = (
        passed
        and correctly_avoids_causality
    )

    print(
        f"TEST 2 - HIGH-FREQUENCY DEFICIENCY: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    if not passed:

        print(
            f"  Expected action: "
            f"{expected_action}"
        )

        print(
            f"  Received action: "
            f"{result['action']}"
        )

        print(
            "  Causality warning was not preserved."
        )

    return passed


# ---------------------------------------------------------
# Test 3
# Reduced sub/bass
# ---------------------------------------------------------

def test_low_frequency_deficiency():

    diagnosis = build_diagnosis(
        "low_frequency_distribution_imbalance",
        [
            build_source(
                "test_drums.wav",
                300.0,
                [
                    build_band(
                        "sub",
                        100.0,
                        "below_reference",
                        "available_energy_source"
                    ),
                    build_band(
                        "bass",
                        100.0,
                        "below_reference",
                        "available_energy_source"
                    )
                ]
            )
        ]
    )

    result = generate_recommendation(
        diagnosis
    )

    expected_action = (
        "investigate_low_frequency_distribution"
    )

    passed = (
        result["action"]
        == expected_action
    )

    print(
        f"TEST 3 - LOW-FREQUENCY DEFICIENCY: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    if not passed:

        print(
            f"  Expected: {expected_action}"
        )

        print(
            f"  Received: {result['action']}"
        )

    return passed


# ---------------------------------------------------------
# Test 4
# Balanced / unknown diagnosis
# ---------------------------------------------------------

def test_generic_diagnosis():

    diagnosis = build_diagnosis(
        "unknown_engineering_issue",
        []
    )

    result = generate_recommendation(
        diagnosis
    )

    expected_action = (
        "investigate_engineering_cause"
    )

    passed = (
        result["action"]
        == expected_action
    )

    print(
        f"TEST 4 - GENERIC DIAGNOSIS: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    if not passed:

        print(
            f"  Expected: {expected_action}"
        )

        print(
            f"  Received: {result['action']}"
        )

    return passed


# ---------------------------------------------------------
# Run all tests
# ---------------------------------------------------------

def main():

    print()
    print("========================================")
    print("RECOMMENDATION ENGINE VALIDATION")
    print("========================================")
    print()

    results = [
        test_low_mid_excess(),
        test_high_frequency_deficiency(),
        test_low_frequency_deficiency(),
        test_generic_diagnosis()
    ]

    passed = sum(
        results
    )

    total = len(results)

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
            "RECOMMENDATION ENGINE: PASS"
        )

    else:

        print(
            "RECOMMENDATION ENGINE: FAIL"
        )

    print()


if __name__ == "__main__":
    main()