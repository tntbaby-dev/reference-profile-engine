import json
import os


INPUT_FILE = (
    "output/dynamics_engineering_diagnosis.json"
)


def load_json(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def validate_file_structure(data):
    required_keys = [
        "file",
        "measurement_type",
        "diagnoses"
    ]

    for key in required_keys:

        if key not in data:
            return False

    if not isinstance(
        data["diagnoses"],
        list
    ):
        return False

    return True


def validate_diagnosis_structure(
    diagnoses
):
    required_keys = [
        "diagnosis",
        "severity",
        "confidence",
        "evidence",
        "interpretation"
    ]

    valid_severities = {
        "high",
        "moderate",
        "low",
        "none"
    }

    valid_confidence = {
        "high",
        "moderate",
        "low"
    }

    for diagnosis in diagnoses:

        for key in required_keys:

            if key not in diagnosis:
                return False

        if diagnosis[
            "severity"
        ] not in valid_severities:
            return False

        if diagnosis[
            "confidence"
        ] not in valid_confidence:
            return False

        if not isinstance(
            diagnosis["evidence"],
            list
        ):
            return False

        if not isinstance(
            diagnosis["interpretation"],
            str
        ):
            return False

    return True


def validate_expected_diagnoses(
    diagnoses
):
    diagnosis_names = {
        diagnosis["diagnosis"]
        for diagnosis in diagnoses
    }

    expected = {
        "elevated_peak_to_rms_ratio",
        "peak_sustained_energy_imbalance",
        "reduced_peak_level",
        "reduced_short_term_rms_variation",
        "overall_rms_distribution_within_reference"
    }

    return expected.issubset(
        diagnosis_names
    )


def validate_peak_rms_relationship(
    diagnoses
):
    diagnosis_names = {
        diagnosis["diagnosis"]
        for diagnosis in diagnoses
    }

    return (
        "elevated_peak_to_rms_ratio"
        in diagnosis_names
        and
        "peak_sustained_energy_imbalance"
        in diagnosis_names
    )


def validate_normal_parameter(
    diagnoses
):
    for diagnosis in diagnoses:

        if (
            diagnosis["diagnosis"]
            ==
            "overall_rms_distribution_within_reference"
        ):

            return (
                diagnosis["severity"]
                == "none"
                and
                diagnosis["confidence"]
                == "high"
            )

    return False


def run_tests(data):

    diagnoses = data[
        "diagnoses"
    ]

    results = []

    # TEST 1
    results.append({
        "name":
            "FILE STRUCTURE",

        "passed":
            validate_file_structure(
                data
            )
    })

    # TEST 2
    results.append({
        "name":
            "DIAGNOSIS STRUCTURE",

        "passed":
            validate_diagnosis_structure(
                diagnoses
            )
    })

    # TEST 3
    results.append({
        "name":
            "EXPECTED DIAGNOSES",

        "passed":
            validate_expected_diagnoses(
                diagnoses
            )
    })

    # TEST 4
    results.append({
        "name":
            "PEAK/RMS RELATIONSHIP",

        "passed":
            validate_peak_rms_relationship(
                diagnoses
            )
    })

    # TEST 5
    results.append({
        "name":
            "NORMAL RMS PARAMETER",

        "passed":
            validate_normal_parameter(
                diagnoses
            )
    })

    return results


def print_results(results):

    print()
    print(
        "========================================"
    )

    print(
        "DYNAMICS ENGINEERING DIAGNOSIS VALIDATION"
    )

    print(
        "========================================"
    )

    print()

    passed_count = 0

    for index, result in enumerate(
        results,
        start=1
    ):

        status = (
            "PASS"
            if result["passed"]
            else
            "FAIL"
        )

        print(
            f"TEST {index} - "
            f"{result['name']}: "
            f"{status}"
        )

        if result["passed"]:
            passed_count += 1

    print()

    print(
        f"Tests passed: "
        f"{passed_count}/"
        f"{len(results)}"
    )

    print()

    if passed_count == len(results):

        print(
            "DYNAMICS ENGINEERING DIAGNOSIS: PASS"
        )

    else:

        print(
            "DYNAMICS ENGINEERING DIAGNOSIS: FAIL"
        )

    print()

    print(
        "========================================"
    )


def main():

    data = load_json(
        INPUT_FILE
    )

    results = run_tests(
        data
    )

    print_results(
        results
    )


if __name__ == "__main__":
    main()