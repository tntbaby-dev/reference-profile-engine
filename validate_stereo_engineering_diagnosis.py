import json
import os


INPUT_FILE = (
    "output/stereo_engineering_diagnosis.json"
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

    return isinstance(
        data["diagnoses"],
        list
    )


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


def get_diagnosis_names(
    diagnoses
):

    return {
        diagnosis["diagnosis"]
        for diagnosis in diagnoses
    }


def validate_balance_diagnosis(
    diagnoses
):

    names = get_diagnosis_names(
        diagnoses
    )

    return (
        "left_right_balance_deviation"
        in names
    )


def validate_normal_stereo_domains(
    diagnoses
):

    names = get_diagnosis_names(
        diagnoses
    )

    expected = {
        "phase_relationship_within_reference",
        "mid_side_relationship_within_reference",
        "mono_compatibility_within_reference"
    }

    return expected.issubset(
        names
    )


def validate_normal_domains_are_cleared(
    diagnoses
):

    for diagnosis in diagnoses:

        if diagnosis[
            "diagnosis"
        ] in {
            "phase_relationship_within_reference",
            "mid_side_relationship_within_reference",
            "mono_compatibility_within_reference"
        }:

            if diagnosis[
                "severity"
            ] != "none":

                return False

            if diagnosis[
                "confidence"
            ] != "high":

                return False

    return True


def validate_balance_severity(
    diagnoses
):

    for diagnosis in diagnoses:

        if (
            diagnosis["diagnosis"]
            ==
            "left_right_balance_deviation"
        ):

            return (
                diagnosis["severity"]
                == "moderate"
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

    results.append({
        "name":
            "FILE STRUCTURE",

        "passed":
            validate_file_structure(
                data
            )
    })

    results.append({
        "name":
            "DIAGNOSIS STRUCTURE",

        "passed":
            validate_diagnosis_structure(
                diagnoses
            )
    })

    results.append({
        "name":
            "L/R BALANCE DIAGNOSIS",

        "passed":
            validate_balance_diagnosis(
                diagnoses
            )
    })

    results.append({
        "name":
            "NORMAL STEREO DOMAINS",

        "passed":
            validate_normal_stereo_domains(
                diagnoses
            )
    })

    results.append({
        "name":
            "NORMAL DOMAINS CLEARED",

        "passed":
            validate_normal_domains_are_cleared(
                diagnoses
            )
    })

    results.append({
        "name":
            "BALANCE SEVERITY",

        "passed":
            validate_balance_severity(
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
        "STEREO ENGINEERING DIAGNOSIS VALIDATION"
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
            "STEREO ENGINEERING DIAGNOSIS: PASS"
        )

    else:

        print(
            "STEREO ENGINEERING DIAGNOSIS: FAIL"
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