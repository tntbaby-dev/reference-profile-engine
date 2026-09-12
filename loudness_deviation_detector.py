import json
import os
import sys

from loudness_reference_analyzer import analyze_reference


PROFILE_FILE = (
    "output/loudness_reference_profile.json"
)

OUTPUT_FILE = (
    "output/loudness_deviation_report.json"
)


# ---------------------------------------------------------
# Load JSON
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Calculate z-score
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Classify deviation
# ---------------------------------------------------------

def classify_deviation(
    z_score
):
    """
    Classify the statistical size of a deviation.

    These classifications describe statistical
    distance, not engineering problems.
    """

    absolute_z = abs(
        z_score
    )

    if absolute_z < 1.0:
        return "within_reference"

    if absolute_z < 2.0:
        return "moderate_deviation"

    if absolute_z < 3.0:
        return "significant_deviation"

    return "extreme_deviation"


# ---------------------------------------------------------
# Determine direction
# ---------------------------------------------------------

def determine_direction(
    difference
):
    """
    Determine whether the target is above,
    below, or effectively at the reference.
    """

    if difference > 0:
        return "above_reference"

    if difference < 0:
        return "below_reference"

    return "balanced"


# ---------------------------------------------------------
# Extract target loudness
# ---------------------------------------------------------

def extract_loudness(
    measurement
):
    """
    Extract the loudness parameters measured
    for the target mix.
    """

    loudness = measurement[
        "loudness"
    ]

    return {
        "integrated_lufs":
            loudness[
                "integrated_lufs"
            ],

        "estimated_true_peak_dbtp":
            loudness[
                "true_peak_dbfs"
            ],

        "rms_dbfs":
            loudness[
                "rms_dbfs"
            ],

        "loudness_range_lu":
            loudness[
                "loudness_range_lu"
            ]
    }


# ---------------------------------------------------------
# Compare one parameter
# ---------------------------------------------------------

def compare_parameter(
    parameter,
    user_value,
    reference
):
    """
    Compare one target loudness parameter
    against the reference profile.
    """

    mean = reference[
        "mean"
    ]

    standard_deviation = reference[
        "std_dev"
    ]

    difference = (
        user_value
        - mean
    )

    z_score = calculate_z_score(
        user_value,
        mean,
        standard_deviation
    )

    classification = classify_deviation(
        z_score
    )

    direction = determine_direction(
        difference
    )

    return {
        "parameter":
            parameter,

        "user_value":
            float(user_value),

        "reference_mean":
            float(mean),

        "reference_std_dev":
            float(
                standard_deviation
            ),

        "difference":
            float(difference),

        "z_score":
            float(z_score),

        "direction":
            direction,

        "classification":
            classification
    }


# ---------------------------------------------------------
# Detect loudness deviations
# ---------------------------------------------------------

def detect_deviations(
    measurement,
    profile
):
    """
    Compare all target loudness parameters
    against the reference profile.
    """

    user_values = extract_loudness(
        measurement
    )

    reference_parameters = profile[
        "parameters"
    ]

    deviations = {}

    for parameter, user_value in (
        user_values.items()
    ):

        reference = (
            reference_parameters[
                parameter
            ]
        )

        deviations[parameter] = (
            compare_parameter(
                parameter,
                user_value,
                reference
            )
        )

    return deviations


# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

def save_report(
    measurement,
    profile,
    deviations
):
    """
    Save the loudness deviation report.
    """

    output = {
        "file":
            measurement["file"],

        "reference_count":
            profile["reference_count"],

        "measurement_type":
            "loudness_and_level_metrics",

        "parameters":
            deviations
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4
        )


# ---------------------------------------------------------
# Print report
# ---------------------------------------------------------

def print_report(
    measurement,
    deviations
):
    """
    Display the loudness deviation report.
    """

    print()
    print("========================================")
    print("LOUDNESS DEVIATION REPORT")
    print("========================================")
    print()

    print(
        f"Target mix: "
        f"{measurement['file']}"
    )

    print()

    display_names = {
        "integrated_lufs":
            "Integrated LUFS",

        "estimated_true_peak_dbtp":
            "Estimated True Peak",

        "rms_dbfs":
            "RMS",

        "loudness_range_lu":
            "Loudness Range"
    }

    units = {
        "integrated_lufs":
            "LUFS",

        "estimated_true_peak_dbtp":
            "dBTP",

        "rms_dbfs":
            "dBFS",

        "loudness_range_lu":
            "LU"
    }

    for parameter, result in (
        deviations.items()
    ):

        print(
            display_names[
                parameter
            ]
        )

        print(
            f"  User: "
            f"{result['user_value']:.2f} "
            f"{units[parameter]}"
        )

        print(
            f"  Ref:  "
            f"{result['reference_mean']:.2f} "
            f"{units[parameter]}"
        )

        print(
            f"  Diff: "
            f"{result['difference']:+.2f} "
            f"{units[parameter]}"
        )

        print(
            f"  Z:    "
            f"{result['z_score']:+.2f}"
        )

        print(
            f"  Direction: "
            f"{result['direction']}"
        )

        print(
            f"  Classification: "
            f"{result['classification']}"
        )

        print()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    if len(sys.argv) != 2:

        print()
        print(
            "Usage:"
        )

        print(
            "python loudness_deviation_detector.py "
            "target/your_file.wav"
        )

        print()

        raise SystemExit(1)

    target_file = sys.argv[1]

    if not os.path.exists(
        target_file
    ):

        raise FileNotFoundError(
            f"Target mix not found: "
            f"{target_file}"
        )

    profile = load_json(
        PROFILE_FILE
    )

    print()
    print("========================================")
    print("TARGET LOUDNESS ANALYSIS")
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
        "Loudness deviation report saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print("========================================")
    print()


if __name__ == "__main__":
    main()