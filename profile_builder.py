import json
import os
import numpy as np


INPUT_FILE = "output/reference_measurements.json"
OUTPUT_FILE = "output/reference_profile.json"


def load_measurements():
    """
    Load spectral measurements from the reference analyzer.
    """

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"Measurement file not found: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def build_profile(measurements):
    """
    Calculate statistical reference values
    for each frequency band.
    """

    if not measurements:
        raise ValueError(
            "No reference measurements found."
        )

    bands = measurements[0]["bands"].keys()

    profile = {}

    for band in bands:

        values = np.array(
            [
                measurement["bands"][band]
                for measurement in measurements
            ],
            dtype=np.float64
        )

        profile[band] = {
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std_dev": float(np.std(values)),
            "p10": float(np.percentile(values, 10)),
            "p25": float(np.percentile(values, 25)),
            "p75": float(np.percentile(values, 75)),
            "p90": float(np.percentile(values, 90))
        }

    return profile


def save_profile(profile, reference_count):
    """
    Save the statistical reference profile as JSON.
    """

    output = {
        "reference_count": reference_count,
        "measurement_type": "relative_spectral_energy_percent",
        "bands": profile
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


def print_profile(profile, reference_count):
    """
    Display the reference profile in the terminal.
    """

    print()
    print("========================================")
    print("REFERENCE PROFILE")
    print("========================================")
    print()

    print(
        f"References analyzed: {reference_count}"
    )

    print(
        "Measurement: Relative spectral energy"
    )

    print()

    for band, statistics in profile.items():

        print(f"{band.upper()}")

        print(
            f"  Mean:   {statistics['mean']:.2f}%"
        )

        print(
            f"  Median: {statistics['median']:.2f}%"
        )

        print(
            f"  Std:    {statistics['std_dev']:.2f}%"
        )

        print(
            f"  P10:    {statistics['p10']:.2f}%"
        )

        print(
            f"  P25:    {statistics['p25']:.2f}%"
        )

        print(
            f"  P75:    {statistics['p75']:.2f}%"
        )

        print(
            f"  P90:    {statistics['p90']:.2f}%"
        )

        print()


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

    print("========================================")
    print(
        f"Profile saved to: {OUTPUT_FILE}"
    )
    print("========================================")
    print()


if __name__ == "__main__":
    main()