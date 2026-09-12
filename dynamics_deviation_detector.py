import json
import os
import sys

from dynamics_reference_analyzer import analyze_reference


PROFILE_FILE = (
    "output/dynamics_reference_profile.json"
)

OUTPUT_FILE = (
    "output/dynamics_deviation_report.json"
)


# ---------------------------------------------------------
# Load JSON
# ---------------------------------------------------------

def load_json(file_path):
    """
    Load JSON data from a file.
    """

    if not os.path.exists(
        file_path
    ):
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
    Classify statistical deviation.

    These classifications describe statistical
    distance from the reference profile.

    They are NOT engineering diagnoses.
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
    below, or equal to the reference mean.
    """

    if difference > 0:
        return "above_reference"

    if difference < 0:
        return "below_reference"

    return "balanced"


# ---------------------------------------------------------
# Extract dynamics measurements
# ---------------------------------------------------------

def extract_dynamics(
    measurement
):
    """
    Extract dynamics parameters from
    the target measurement.
    """

    dynamics = measurement[
        "dynamics"
    ]

    return {
        "peak_dbfs":
            dynamics[
                "peak_dbfs"
            ],

        "crest_factor_db":
            dynamics[
                "crest_factor_db"
            ],

        "rms_dynamic_variation_db":
            dynamics[
                "rms_dynamic_variation_db"
            ],

        "rms_percentile_spread_db":
            dynamics[
                "rms_percentile_spread_db"
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
    Compare one dynamics parameter against
    the reference profile.
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
# Detect dynamics deviations
# ---------------------------------------------------------

def detect_deviations(
    measurement,
    profile
):
    """
    Compare all dynamics parameters against
    the reference profile.
    """

    user_values = extract_dynamics(
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
    Save the dynamics deviation report.
    """

    output = {
        "file":
            measurement[
                "file"
            ],

        "reference_count":
            profile[
                "reference_count"
            ],

        "measurement_type":
            "dynamic_range_metrics",

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
    Display the dynamics deviation report.
    """

    print()
    print("========================================")
    print("DYNAMICS DEVIATION REPORT")
    print("========================================")
    print()

    print(
        f"Target mix: "
        f"{measurement['file']}"
    )

    print()

    display_names = {
        "peak_dbfs":
            "Peak",

        "crest_factor_db":
            "Crest Factor",

        "rms_dynamic_variation_db":
            "RMS Dynamic Variation",

        "rms_percentile_spread_db":
            "RMS P90-P10 Spread"
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
            f"{result['user_value']:.2f} dB"
        )

        print(
            f"  Ref:  "
            f"{result['reference_mean']:.2f} dB"
        )

        print(
            f"  Diff: "
            f"{result['difference']:+.2f} dB"
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
            "python dynamics_deviation_detector.py "
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
    print("TARGET DYNAMICS ANALYSIS")
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
        "Dynamics deviation report saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print("========================================")
    print()


if __name__ == "__main__":
    main()