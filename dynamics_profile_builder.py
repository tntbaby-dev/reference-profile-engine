import json
import os

import numpy as np


INPUT_FILE = (
    "output/dynamics_reference_measurements.json"
)

OUTPUT_FILE = (
    "output/dynamics_reference_profile.json"
)


# ---------------------------------------------------------
# Load measurements
# ---------------------------------------------------------

def load_measurements():
    """
    Load dynamics measurements from the
    dynamics reference analyzer.
    """

    if not os.path.exists(
        INPUT_FILE
    ):
        raise FileNotFoundError(
            f"Measurement file not found: "
            f"{INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if "references" not in data:
        raise ValueError(
            "Dynamics measurement file does not "
            "contain a 'references' list."
        )

    measurements = data[
        "references"
    ]

    if not measurements:
        raise ValueError(
            "No dynamics measurements found."
        )

    return measurements


# ---------------------------------------------------------
# Calculate statistics
# ---------------------------------------------------------

def calculate_statistics(
    values
):
    """
    Calculate statistical reference values
    for one dynamics parameter.
    """

    values = np.array(
        values,
        dtype=np.float64
    )

    return {
        "mean":
            float(
                np.mean(values)
            ),

        "median":
            float(
                np.median(values)
            ),

        "std_dev":
            float(
                np.std(values)
            ),

        "p10":
            float(
                np.percentile(
                    values,
                    10
                )
            ),

        "p25":
            float(
                np.percentile(
                    values,
                    25
                )
            ),

        "p75":
            float(
                np.percentile(
                    values,
                    75
                )
            ),

        "p90":
            float(
                np.percentile(
                    values,
                    90
                )
            )
    }


# ---------------------------------------------------------
# Build profile
# ---------------------------------------------------------

def build_profile(
    measurements
):
    """
    Build statistical profiles for all
    measured dynamics parameters.
    """

    parameters = [
        "peak_dbfs",
        "crest_factor_db",
        "rms_dynamic_variation_db",
        "rms_percentile_spread_db"
    ]

    profile = {}

    for parameter in parameters:

        values = [
            measurement[
                "dynamics"
            ][
                parameter
            ]
            for measurement in measurements
        ]

        profile[parameter] = (
            calculate_statistics(
                values
            )
        )

    return profile


# ---------------------------------------------------------
# Save profile
# ---------------------------------------------------------

def save_profile(
    profile,
    reference_count
):
    """
    Save the dynamics reference profile.
    """

    output = {
        "reference_count":
            reference_count,

        "measurement_type":
            "dynamic_range_metrics",

        "parameters":
            profile
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
# Print profile
# ---------------------------------------------------------

def print_profile(
    profile,
    reference_count
):
    """
    Display the dynamics reference profile.
    """

    print()
    print("========================================")
    print("DYNAMICS REFERENCE PROFILE")
    print("========================================")
    print()

    print(
        f"References analyzed: "
        f"{reference_count}"
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

    for parameter, statistics in (
        profile.items()
    ):

        print(
            display_names[
                parameter
            ]
        )

        print(
            f"  Mean:   "
            f"{statistics['mean']:.2f} dB"
        )

        print(
            f"  Median: "
            f"{statistics['median']:.2f} dB"
        )

        print(
            f"  Std:    "
            f"{statistics['std_dev']:.2f} dB"
        )

        print(
            f"  P10:    "
            f"{statistics['p10']:.2f} dB"
        )

        print(
            f"  P25:    "
            f"{statistics['p25']:.2f} dB"
        )

        print(
            f"  P75:    "
            f"{statistics['p75']:.2f} dB"
        )

        print(
            f"  P90:    "
            f"{statistics['p90']:.2f} dB"
        )

        print()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    measurements = load_measurements()

    profile = build_profile(
        measurements
    )

    save_profile(
        profile,
        len(measurements)
    )

    print_profile(
        profile,
        len(measurements)
    )

    print(
        "========================================"
    )

    print(
        f"Profile saved to: "
        f"{OUTPUT_FILE}"
    )

    print(
        "========================================"
    )

    print()


if __name__ == "__main__":
    main()