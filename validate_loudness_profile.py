import json
import os


INPUT_FILE = (
    "output/loudness_reference_measurements.json"
)

PROFILE_FILE = (
    "output/loudness_reference_profile.json"
)


EXPECTED_PARAMETERS = {
    "integrated_lufs",
    "estimated_true_peak_dbtp",
    "rms_dbfs",
    "loudness_range_lu"
}


STATISTICAL_FIELDS = {
    "mean",
    "median",
    "std_dev",
    "p10",
    "p25",
    "p75",
    "p90"
}


def load_json(file_path):
    """
    Load JSON data from a file.
    """

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


def validate_measurement_count(
    measurements,
    profile
):
    """
    Confirm that the profile contains the same
    reference count as the raw measurements.
    """

    actual_count = len(
        measurements.get(
            "references",
            []
        )
    )

    profile_count = profile.get(
        "reference_count",
        0
    )

    passed = (
        actual_count == profile_count
        and actual_count > 0
    )

    print(
        f"Reference count: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    print(
        f"  Measurements: {actual_count}"
    )

    print(
        f"  Profile:      {profile_count}"
    )

    print()

    return passed


def validate_parameters(profile):
    """
    Confirm that every expected loudness parameter
    exists in the profile.
    """

    parameters = profile.get(
        "parameters",
        {}
    )

    actual_parameters = set(
        parameters.keys()
    )

    missing = (
        EXPECTED_PARAMETERS
        - actual_parameters
    )

    passed = not missing

    print(
        f"Parameter structure: "
        f"{'PASS' if passed else 'FAIL'}"
    )

    if missing:

        print(
            "  Missing:"
        )

        for parameter in sorted(
            missing
        ):
            print(
                f"    - {parameter}"
            )

    else:

        print(
            "  All expected parameters present."
        )

    print()

    return passed


def validate_statistics(profile):
    """
    Confirm that every parameter contains
    the required statistical fields.
    """

    parameters = profile.get(
        "parameters",
        {}
    )

    all_valid = True

    for parameter in sorted(
        EXPECTED_PARAMETERS
    ):

        statistics = parameters.get(
            parameter,
            {}
        )

        missing = (
            STATISTICAL_FIELDS
            - set(statistics.keys())
        )

        if missing:

            print(
                f"{parameter}: FAIL"
            )

            print(
                f"  Missing fields: "
                f"{', '.join(sorted(missing))}"
            )

            all_valid = False

        else:

            print(
                f"{parameter}: PASS"
            )

    print()

    return all_valid


def validate_reference_values(
    measurements
):
    """
    Confirm that raw loudness measurements contain
    valid numeric values.
    """

    all_valid = True

    for reference in measurements.get(
        "references",
        []
    ):

        loudness = reference.get(
            "loudness",
            {}
        )

        required_values = [
            "integrated_lufs",
            "true_peak_dbfs",
            "rms_dbfs",
            "loudness_range_lu"
        ]

        for parameter in required_values:

            value = loudness.get(
                parameter
            )

            if not isinstance(
                value,
                (int, float)
            ):

                print(
                    f"{reference['file']}: "
                    f"FAIL - {parameter}"
                )

                all_valid = False

    if all_valid:

        print(
            "Raw reference values: PASS"
        )

        print(
            "  All loudness measurements "
            "contain numeric values."
        )

    print()

    return all_valid


def validate_profile_values(
    profile
):
    """
    Confirm that profile statistics are numeric
    and internally sensible.
    """

    parameters = profile.get(
        "parameters",
        {}
    )

    all_valid = True

    for parameter in sorted(
        EXPECTED_PARAMETERS
    ):

        statistics = parameters.get(
            parameter,
            {}
        )

        for field in STATISTICAL_FIELDS:

            value = statistics.get(
                field
            )

            if not isinstance(
                value,
                (int, float)
            ):

                print(
                    f"{parameter}: FAIL - "
                    f"{field} is not numeric"
                )

                all_valid = False

    if all_valid:

        print(
            "Profile statistics: PASS"
        )

        print(
            "  All statistical values are numeric."
        )

    print()

    return all_valid


def main():

    measurements = load_json(
        INPUT_FILE
    )

    profile = load_json(
        PROFILE_FILE
    )

    print()
    print("========================================")
    print("LOUDNESS PROFILE VALIDATION")
    print("========================================")
    print()

    count_valid = (
        validate_measurement_count(
            measurements,
            profile
        )
    )

    parameter_valid = (
        validate_parameters(
            profile
        )
    )

    statistics_valid = (
        validate_statistics(
            profile
        )
    )

    reference_values_valid = (
        validate_reference_values(
            measurements
        )
    )

    profile_values_valid = (
        validate_profile_values(
            profile
        )
    )

    print("========================================")
    print("VALIDATION SUMMARY")
    print("========================================")
    print()

    if all([
        count_valid,
        parameter_valid,
        statistics_valid,
        reference_values_valid,
        profile_values_valid
    ]):

        print(
            "LOUDNESS REFERENCE PROFILE: PASS"
        )

    else:

        print(
            "LOUDNESS REFERENCE PROFILE: FAIL"
        )

    print()


if __name__ == "__main__":
    main()