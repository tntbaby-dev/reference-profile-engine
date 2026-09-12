import json
import os
import sys

import numpy as np
import soundfile as sf


REFERENCES_FOLDER = "references"
OUTPUT_FILE = "output/stereo_reference_measurements.json"


def load_audio(file_path):
    data, sample_rate = sf.read(
        file_path,
        always_2d=True
    )

    data = data.astype(
        np.float64
    )

    return data, sample_rate


def calculate_rms(signal):
    return np.sqrt(
        np.mean(
            signal ** 2
        )
    )


def calculate_lr_balance(
    left,
    right
):
    left_rms = calculate_rms(left)
    right_rms = calculate_rms(right)

    left_db = (
        20 * np.log10(
            max(left_rms, 1e-12)
        )
    )

    right_db = (
        20 * np.log10(
            max(right_rms, 1e-12)
        )
    )

    return left_db - right_db


def calculate_mid_side_ratio(
    left,
    right
):
    mid = (
        left + right
    ) / np.sqrt(2)

    side = (
        left - right
    ) / np.sqrt(2)

    mid_rms = calculate_rms(
        mid
    )

    side_rms = calculate_rms(
        side
    )

    ratio_db = (
        20 * np.log10(
            max(side_rms, 1e-12)
            /
            max(mid_rms, 1e-12)
        )
    )

    return ratio_db


def calculate_phase_correlation(
    left,
    right
):
    left_centered = (
        left - np.mean(left)
    )

    right_centered = (
        right - np.mean(right)
    )

    numerator = np.sum(
        left_centered
        * right_centered
    )

    denominator = np.sqrt(
        np.sum(
            left_centered ** 2
        )
        *
        np.sum(
            right_centered ** 2
        )
    )

    if denominator <= 0:
        return 0.0

    return numerator / denominator


def calculate_mono_compatibility(
    left,
    right
):
    stereo_rms = np.sqrt(
        (
            np.mean(left ** 2)
            +
            np.mean(right ** 2)
        ) / 2
    )

    mono = (
        left + right
    ) / 2

    mono_rms = calculate_rms(
        mono
    )

    stereo_db = (
        20 * np.log10(
            max(stereo_rms, 1e-12)
        )
    )

    mono_db = (
        20 * np.log10(
            max(mono_rms, 1e-12)
        )
    )

    return mono_db - stereo_db


def analyze_file(file_path):
    print()
    print(
        f"Analyzing: {file_path}"
    )

    data, sample_rate = load_audio(
        file_path
    )

    if data.shape[1] < 2:
        raise ValueError(
            f"Stereo analysis requires "
            f"a stereo file: {file_path}"
        )

    left = data[:, 0]
    right = data[:, 1]

    lr_balance = (
        calculate_lr_balance(
            left,
            right
        )
    )

    phase_correlation = (
        calculate_phase_correlation(
            left,
            right
        )
    )

    mid_side_ratio = (
        calculate_mid_side_ratio(
            left,
            right
        )
    )

    mono_compatibility = (
        calculate_mono_compatibility(
            left,
            right
        )
    )

    return {
        "file":
            os.path.basename(
                file_path
            ),

        "sample_rate":
            int(sample_rate),

        "channels":
            int(data.shape[1]),

        "stereo": {
            "lr_balance_db":
                float(
                    lr_balance
                ),

            "phase_correlation":
                float(
                    phase_correlation
                ),

            "mid_side_ratio_db":
                float(
                    mid_side_ratio
                ),

            "mono_compatibility_db":
                float(
                    mono_compatibility
                )
        }
    }


def find_audio_files(
    folder
):
    extensions = {
        ".wav",
        ".aif",
        ".aiff"
    }

    files = []

    for filename in sorted(
        os.listdir(folder)
    ):

        file_path = os.path.join(
            folder,
            filename
        )

        if not os.path.isfile(
            file_path
        ):
            continue

        extension = (
            os.path.splitext(
                filename
            )[1].lower()
        )

        if extension in extensions:
            files.append(
                file_path
            )

    return files


def save_results(
    results
):
    os.makedirs(
        os.path.dirname(
            OUTPUT_FILE
        ),
        exist_ok=True
    )

    output = {
        "reference_count":
            len(results),

        "measurement_type":
            "stereo_metrics",

        "references":
            results
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


def main():

    if not os.path.exists(
        REFERENCES_FOLDER
    ):
        raise FileNotFoundError(
            f"References folder not found: "
            f"{REFERENCES_FOLDER}"
        )

    files = find_audio_files(
        REFERENCES_FOLDER
    )

    if not files:
        raise FileNotFoundError(
            "No audio files found in "
            f"{REFERENCES_FOLDER}"
        )

    results = []

    for file_path in files:

        result = analyze_file(
            file_path
        )

        results.append(
            result
        )

    save_results(
        results
    )

    print()
    print(
        "========================================"
    )
    print(
        "STEREO REFERENCE ANALYSIS COMPLETE"
    )
    print(
        "========================================"
    )

    print()

    print(
        f"References analyzed: "
        f"{len(results)}"
    )

    print()

    print(
        "Stereo metrics:"
    )

    print(
        "  L/R Balance"
    )

    print(
        "  Phase Correlation"
    )

    print(
        "  Mid/Side Ratio"
    )

    print(
        "  Mono Compatibility"
    )

    print()

    print(
        "Results saved to:"
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