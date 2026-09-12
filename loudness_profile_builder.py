import json
import os
import numpy as np


INPUT_FILE = (
    "output/loudness_reference_measurements.json"
)

OUTPUT_FILE = (
    "output/loudness_reference_profile.json"
)


# ---------------------------------------------------------
# Load measurements
# ---------------------------------------------------------

def load_measurements():
    """
    Load loudness measurements from the
    loudness reference analyzer.
    """

    if not os.path.exists(INPUT_FILE):

        raise FileNotFoundError(
            "Loudness measurement file not found: "
            f"{INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ---------------------------------------------------------
# Calculate statistics
# ---------------------------------------------------------

def calculate_statistics(values):
    """
    Calculate statistical reference values
    for one loudness parameter.
    """

    values = np.array(
        values,
        dtype=np.float64
    )

    return {
        "mean": float(
            np.mean(values)
        ),

        "median": float(
            np.median(values)
        ),

        "std_dev": float(
            np.std(values)
        ),

        "p10": float(
            np.percentile(values, 10)
        ),

        "p25": float(
            np.percentile(values, 25)
        ),

        "p75": float(
            np.percentile(values, 75)
        ),

        "p90": float(
            np.percentile(values, 90)
        )
    }


# ---------------------------------------------------------
# Build profile
# ---------------------------------------------------------

def build_profile(data):
    """
    Build statistical reference profiles for:

        Integrated LUFS
        Estimated True Peak
        RMS
        Loudness Range
    """

    references = data.get(
        "references",
        []
    )

    if not references:

        raise ValueError(
            "No loudness reference measurements found."
        )

    integrated_lufs = []
    true_peak_dbtp = []
    rms_dbfs = []
    loudness_range_lu = []

    for reference in references:

        loudness = reference[
            "loudness"
        ]

        integrated_lufs.append(
            loudness[
                "integrated_lufs"
            ]
        )

        true_peak_dbtp.append(
            loudness[
                "true_peak_dbfs"
            ]
        )

        rms_dbfs.append(
            loudness[
                "rms_dbfs"
            ]
        )

        loudness_range_lu.append(
            loudness[
                "loudness_range_lu"
            ]
        )

    profile = {

        "integrated_lufs":
            calculate_statistics(
                integrated_lufs
            ),

        "estimated_true_peak_dbtp":
            calculate_statistics(
                true_peak_dbtp
            ),

        "rms_dbfs":
            calculate_statistics(
                rms_dbfs
            ),

        "loudness_range_lu":
            calculate_statistics(
                loudness_range_lu
            )
    }

    return profile


# ---------------------------------------------------------
# Save profile
# ---------------------------------------------------------

def save_profile(
    profile,
    reference_count
):
    """
    Save the statistical loudness profile.
    """

    output = {

        "reference_count":
            reference_count,

        "measurement_type":
            "loudness_and_level_metrics",

        "parameters": profile
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
    Display the loudness reference profile.
    """

    print()
    print("========================================")
    print("LOUDNESS REFERENCE PROFILE")
    print("========================================")
    print()

    print(
        f"References analyzed: "
        f"{reference_count}"
    )

    print()

    parameters = [
        (
            "Integrated LUFS",
            "integrated_lufs",
            "LUFS"
        ),
        (
            "Estimated True Peak",
            "estimated_true_peak_dbtp",
            "dBTP"
        ),
        (
            "RMS",
            "rms_dbfs",
            "dBFS"
        ),
        (
            "Loudness Range",
            "loudness_range_lu",
            "LU"
        )
    ]

    for label, key, unit in parameters:

        statistics = profile[key]

        print(
            label
        )

        print(
            f"  Mean:   "
            f"{statistics['mean']:.2f} {unit}"
        )

        print(
            f"  Median: "
            f"{statistics['median']:.2f} {unit}"
        )

        print(
            f"  Std:    "
            f"{statistics['std_dev']:.2f} {unit}"
        )

        print(
            f"  P10:    "
            f"{statistics['p10']:.2f} {unit}"
        )

        print(
            f"  P25:    "
            f"{statistics['p25']:.2f} {unit}"
        )

        print(
            f"  P75:    "
            f"{statistics['p75']:.2f} {unit}"
        )

        print(
            f"  P90:    "
            f"{statistics['p90']:.2f} {unit}"
        )

        print()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    data = load_measurements()

    profile = build_profile(
        data
    )

    reference_count = data[
        "reference_count"
    ]

    save_profile(
        profile,
        reference_count
    )

    print_profile(
        profile,
        reference_count
    )

    print("========================================")
    print(
        "Loudness profile saved to:"
    )
    print(
        OUTPUT_FILE
    )
    print("========================================")
    print()


if __name__ == "__main__":
    main()