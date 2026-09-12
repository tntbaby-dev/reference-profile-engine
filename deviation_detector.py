import json
import os
import sys

from reference_analyzer import analyze_reference


PROFILE_FILE = "output/reference_profile.json"
OUTPUT_FILE = "output/deviation_report.json"


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


def calculate_z_score(
    value,
    mean,
    standard_deviation
):
    """
    Calculate how many standard deviations
    a value is from the reference mean.
    """

    if standard_deviation <= 0:
        return 0.0

    return (
        (value - mean)
        / standard_deviation
    )


def classify_deviation(z_score):
    """
    Classify statistical deviation.

    These classifications describe the size
    of the statistical difference.

    They are NOT engineering diagnoses.
    """

    absolute_z = abs(z_score)

    if absolute_z < 1.0:
        return "within_reference"

    if absolute_z < 2.0:
        return "moderate_deviation"

    if absolute_z < 3.0:
        return "significant_deviation"

    return "extreme_deviation"


def detect_deviations(
    measurement,
    profile
):
    """
    Compare one target mix against the
    professional reference profile.
    """

    deviations = {}

    for band, value in measurement["bands"].items():

        reference = profile["bands"][band]

        mean = reference["mean"]
        standard_deviation = reference["std_dev"]

        difference = value - mean

        z_score = calculate_z_score(
            value,
            mean,
            standard_deviation
        )

        classification = classify_deviation(
            z_score
        )

        direction = "balanced"

        if z_score > 0:
            direction = "above_reference"

        elif z_score < 0:
            direction = "below_reference"

        deviations[band] = {
            "user_value_percent": float(value),
            "reference_mean_percent": float(mean),
            "reference_std_dev_percent": float(
                standard_deviation
            ),
            "difference_percent": float(
                difference
            ),
            "z_score": float(z_score),
            "direction": direction,
            "classification": classification
        }

    return deviations


def print_report(
    measurement,
    deviations
):
    """
    Display the deviation report.
    """

    print()
    print("========================================")
    print("DEVIATION REPORT")
    print("========================================")
    print()

    print(
        f"Target mix: {measurement['file']}"
    )

    print()

    for band, result in deviations.items():

        print(
            f"{band.upper():<12}"
            f" User: {result['user_value_percent']:>6.2f}%"
            f"  Ref: {result['reference_mean_percent']:>6.2f}%"
            f"  Z: {result['z_score']:>6.2f}"
        )

        print(
            f"{'':<12}"
            f" {result['direction']}"
            f" | {result['classification']}"
        )

        print()


def save_report(
    measurement,
    profile,
    deviations
):
    """
    Save the deviation report.
    """

    report = {
        "file": measurement["file"],
        "reference_count": profile["reference_count"],
        "measurement_type": (
            "relative_spectral_energy_percent"
        ),
        "bands": deviations
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )


def main():

    if len(sys.argv) != 2:
        print(
            "ERROR: Target mix path is required."
        )
        print()
        print(
            "Usage:"
        )
        print(
            "python deviation_detector.py target/your_file.wav"
        )
        print()
        sys.exit(1)

    target_file = sys.argv[1]

    if not os.path.exists(target_file):
        print(
            f"ERROR: Target file not found: {target_file}"
        )
        sys.exit(1)

    profile = load_json(
        PROFILE_FILE
    )

    print()
    print("========================================")
    print("TARGET MIX ANALYSIS")
    print("========================================")
    print()

    measurement = analyze_reference(
        target_file
    )

    deviations = detect_deviations(
        measurement,
        profile
    )

    save_report(
        measurement,
        profile,
        deviations
    )

    print_report(
        measurement,
        deviations
    )

    print("========================================")
    print(
        "Deviation report saved to:"
    )
    print(
        OUTPUT_FILE
    )
    print("========================================")
    print()


if __name__ == "__main__":
    main()