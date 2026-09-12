import json
import os
import sys

from stereo_reference_analyzer import analyze_file


PROFILE_FILE = (
    "output/stereo_reference_profile.json"
)

OUTPUT_FILE = (
    "output/stereo_deviation_report.json"
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


def calculate_z_score(
    value,
    mean,
    standard_deviation
):
    if standard_deviation <= 0:
        return 0.0

    return (
        (value - mean)
        / standard_deviation
    )


def classify_deviation(
    z_score
):
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


def determine_direction(
    difference
):
    if difference > 0:
        return "above_reference"

    if difference < 0:
        return "below_reference"

    return "balanced"


def extract_stereo(
    measurement
):
    stereo = measurement[
        "stereo"
    ]

    return {
        "lr_balance_db":
            stereo[
                "lr_balance_db"
            ],

        "phase_correlation":
            stereo[
                "phase_correlation"
            ],

        "mid_side_ratio_db":
            stereo[
                "mid_side_ratio_db"
            ],

        "mono_compatibility_db":
            stereo[
                "mono_compatibility_db"
            ]
    }


def compare_parameter(
    parameter,
    user_value,
    reference
):
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


def detect_deviations(
    measurement,
    profile
):
    user_values = extract_stereo(
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


def save_report(
    measurement,
    profile,
    deviations
):
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
            "stereo_metrics",

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


def print_report(
    measurement,
    deviations
):
    print()
    print(
        "========================================"
    )
    print(
        "STEREO DEVIATION REPORT"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"Target mix: "
        f"{measurement['file']}"
    )

    print()

    display_names = {
        "lr_balance_db":
            "L/R Balance",

        "phase_correlation":
            "Phase Correlation",

        "mid_side_ratio_db":
            "Mid/Side Ratio",

        "mono_compatibility_db":
            "Mono Compatibility"
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
            f"{result['user_value']:.2f}"
        )

        print(
            f"  Ref:  "
            f"{result['reference_mean']:.2f}"
        )

        print(
            f"  Diff: "
            f"{result['difference']:+.2f}"
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


def main():

    if len(sys.argv) != 2:

        print()
        print(
            "Usage:"
        )

        print(
            "python stereo_deviation_detector.py "
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
    print(
        "========================================"
    )
    print(
        "TARGET STEREO ANALYSIS"
    )
    print(
        "========================================"
    )
    print()

    measurement = analyze_file(
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

    print(
        "========================================"
    )

    print(
        "Stereo deviation report saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "========================================"
    )
    print()


if __name__ == "__main__":
    main()