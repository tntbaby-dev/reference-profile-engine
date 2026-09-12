import json
import os


INPUT_FILE = (
    "output/stereo_reference_measurements.json"
)

OUTPUT_FILE = (
    "output/stereo_reference_profile.json"
)


PARAMETERS = [
    "lr_balance_db",
    "phase_correlation",
    "mid_side_ratio_db",
    "mono_compatibility_db"
]


def load_measurements(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data


def calculate_percentile(
    values,
    percentile
):
    return float(
        __import__("numpy").percentile(
            values,
            percentile
        )
    )


def build_parameter_profile(
    values
):
    numpy = __import__("numpy")

    values = numpy.array(
        values,
        dtype=float
    )

    return {
        "mean":
            float(
                numpy.mean(values)
            ),

        "median":
            float(
                numpy.median(values)
            ),

        "std_dev":
            float(
                numpy.std(values)
            ),

        "p10":
            calculate_percentile(
                values,
                10
            ),

        "p25":
            calculate_percentile(
                values,
                25
            ),

        "p75":
            calculate_percentile(
                values,
                75
            ),

        "p90":
            calculate_percentile(
                values,
                90
            )
    }


def build_profile(
    data
):

    references = data[
        "references"
    ]

    profile = {
        "reference_count":
            len(references),

        "measurement_type":
            "stereo_metrics",

        "parameters": {}
    }

    for parameter in PARAMETERS:

        values = []

        for reference in references:

            value = reference[
                "stereo"
            ][
                parameter
            ]

            values.append(
                value
            )

        profile[
            "parameters"
        ][
            parameter
        ] = build_parameter_profile(
            values
        )

    return profile


def save_profile(
    profile
):

    os.makedirs(
        os.path.dirname(
            OUTPUT_FILE
        ),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=4
        )


def print_profile(
    profile
):

    print()
    print(
        "========================================"
    )
    print(
        "STEREO REFERENCE PROFILE"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"References: "
        f"{profile['reference_count']}"
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

    for parameter, stats in (
        profile[
            "parameters"
        ].items()
    ):

        print(
            display_names[
                parameter
            ]
        )

        print(
            f"  Mean:   "
            f"{stats['mean']:.2f}"
        )

        print(
            f"  Median: "
            f"{stats['median']:.2f}"
        )

        print(
            f"  Std:    "
            f"{stats['std_dev']:.2f}"
        )

        print(
            f"  P10:    "
            f"{stats['p10']:.2f}"
        )

        print(
            f"  P25:    "
            f"{stats['p25']:.2f}"
        )

        print(
            f"  P75:    "
            f"{stats['p75']:.2f}"
        )

        print(
            f"  P90:    "
            f"{stats['p90']:.2f}"
        )

        print()


def main():

    data = load_measurements(
        INPUT_FILE
    )

    profile = build_profile(
        data
    )

    save_profile(
        profile
    )

    print_profile(
        profile
    )

    print(
        "========================================"
    )

    print(
        "Stereo reference profile saved to:"
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