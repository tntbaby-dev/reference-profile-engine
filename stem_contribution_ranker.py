import os
import json
import numpy as np
import soundfile as sf
from scipy.signal import stft


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

TARGET_FOLDER = "target"

MIX_FILE = "ditb.wav"

DEVIATION_FILE = (
    "output/deviation_report.json"
)

STEM_OUTPUT_FILE = (
    "output/stem_contribution_ranking.json"
)

FRAME_SIZE = 4096
HOP_SIZE = 2048

FREQUENCY_BANDS = {
    "sub": (20, 60),
    "bass": (60, 120),
    "low_mid": (120, 250),
    "mid": (250, 500),
    "upper_mid": (500, 2000),
    "presence": (2000, 4000),
    "brilliance": (4000, 8000),
    "air": (8000, 16000),
}


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
# Load audio
# ---------------------------------------------------------

def load_audio(file_path):
    """
    Load audio as float32.
    """

    audio, sample_rate = sf.read(
        file_path,
        always_2d=True
    )

    return (
        audio.astype(np.float32),
        sample_rate
    )


# ---------------------------------------------------------
# Calculate stereo-safe spectral power
# ---------------------------------------------------------

def calculate_stereo_power(
    audio,
    sample_rate
):
    """
    Calculate average spectral power across
    the available audio channels.
    """

    left = audio[:, 0]

    if audio.shape[1] >= 2:
        right = audio[:, 1]
    else:
        right = left

    nperseg = min(
        FRAME_SIZE,
        len(left)
    )

    if nperseg < 2:
        raise ValueError(
            "Audio file is too short for spectral analysis."
        )

    noverlap = min(
        nperseg - 1,
        max(
            0,
            nperseg - HOP_SIZE
        )
    )

    frequencies, _, left_stft = stft(
        left,
        fs=sample_rate,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        boundary=None,
        padded=False
    )

    _, _, right_stft = stft(
        right,
        fs=sample_rate,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        boundary=None,
        padded=False
    )

    left_power = (
        np.abs(left_stft) ** 2
    )

    right_power = (
        np.abs(right_stft) ** 2
    )

    stereo_power = (
        left_power + right_power
    ) / 2

    return (
        frequencies,
        stereo_power
    )


# ---------------------------------------------------------
# Calculate band power
# ---------------------------------------------------------

def calculate_band_power(
    frequencies,
    stereo_power
):
    """
    Calculate absolute spectral power
    within each frequency band.
    """

    band_power = {}

    for band_name, (
        lower_frequency,
        upper_frequency
    ) in FREQUENCY_BANDS.items():

        band_mask = (
            (frequencies >= lower_frequency)
            & (frequencies < upper_frequency)
        )

        power = np.sum(
            stereo_power[band_mask, :]
        )

        band_power[band_name] = float(
            power
        )

    return band_power


# ---------------------------------------------------------
# Analyze one stem
# ---------------------------------------------------------

def analyze_stem(file_path):
    """
    Measure absolute spectral band power
    for one stem.
    """

    audio, sample_rate = load_audio(
        file_path
    )

    frequencies, stereo_power = (
        calculate_stereo_power(
            audio,
            sample_rate
        )
    )

    band_power = calculate_band_power(
        frequencies,
        stereo_power
    )

    return {
        "file": os.path.basename(file_path),
        "sample_rate": int(sample_rate),
        "channels": int(audio.shape[1]),
        "duration_seconds": float(
            len(audio) / sample_rate
        ),
        "band_power": band_power
    }


# ---------------------------------------------------------
# Find problematic bands
# ---------------------------------------------------------

def find_problem_bands(deviation_report):
    """
    Identify frequency bands with meaningful
    statistical deviation from the reference.
    """

    deviations = deviation_report["bands"]

    problem_bands = []

    for band, result in deviations.items():

        classification = result[
            "classification"
        ]

        if classification in {
            "moderate_deviation",
            "significant_deviation",
            "extreme_deviation"
        }:

            problem_bands.append(
                band
            )

    return problem_bands


# ---------------------------------------------------------
# Calculate contribution percentages
# ---------------------------------------------------------

def calculate_contributions(
    stem_results,
    bands
):
    """
    Calculate each stem's percentage contribution
    to the combined stem power within each band.

    This is a contribution index, not proof of causality.
    """

    contributions = {}

    for band in bands:

        total_power = sum(
            stem["band_power"][band]
            for stem in stem_results
        )

        if total_power <= 0:
            continue

        band_results = []

        for stem in stem_results:

            power = stem[
                "band_power"
            ][band]

            percentage = (
                power / total_power
            ) * 100

            band_results.append(
                {
                    "file": stem["file"],
                    "power": float(power),
                    "contribution_percent": float(
                        percentage
                    )
                }
            )

        band_results.sort(
            key=lambda item:
                item["contribution_percent"],
            reverse=True
        )

        contributions[band] = (
            band_results
        )

    return contributions


# ---------------------------------------------------------
# Build ranking
# ---------------------------------------------------------

def build_ranking(
    contributions,
    deviation_report
):
    """
    Rank stems according to their contribution
    to statistically problematic frequency bands.

    The statistical magnitude of the mix deviation
    is used as a weighting factor.
    """

    deviations = deviation_report[
        "bands"
    ]

    stem_scores = {}

    for band, results in (
        contributions.items()
    ):

        z_score = abs(
            deviations[band]["z_score"]
        )

        for result in results:

            file_name = result[
                "file"
            ]

            contribution = result[
                "contribution_percent"
            ]

            weighted_score = (
                contribution * z_score
            )

            if file_name not in stem_scores:
                stem_scores[file_name] = 0.0

            stem_scores[file_name] += (
                weighted_score
            )

    ranking = []

    for file_name, score in (
        stem_scores.items()
    ):

        ranking.append(
            {
                "file": file_name,
                "weighted_contribution_score":
                    float(score)
            }
        )

    ranking.sort(
        key=lambda item:
            item[
                "weighted_contribution_score"
            ],
        reverse=True
    )

    for index, result in enumerate(
        ranking,
        start=1
    ):

        result["rank"] = index

    return ranking


# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

def save_report(
    deviation_report,
    problem_bands,
    contributions,
    ranking
):
    """
    Save source-level contribution analysis.
    """

    output = {
        "mix_file": MIX_FILE,
        "problem_bands": problem_bands,
        "measurement_type": (
            "absolute_stem_spectral_power"
        ),
        "contribution_method": (
            "stem_band_power_share"
        ),
        "note": (
            "Contribution percentages describe each "
            "stem's share of combined measured stem "
            "power within a frequency band. They do "
            "not establish causality."
        ),
        "band_contributions": contributions,
        "overall_stem_ranking": ranking
    }

    with open(
        STEM_OUTPUT_FILE,
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
    problem_bands,
    contributions,
    ranking
):
    """
    Display the source-level contribution report.
    """

    print()
    print("========================================")
    print("STEM CONTRIBUTION RANKING")
    print("========================================")
    print()

    print(
        "Problematic bands:"
    )

    for band in problem_bands:
        print(
            f"  - {band}"
        )

    print()

    print(
        "BAND CONTRIBUTIONS"
    )

    print(
        "----------------------------------------"
    )

    for band in problem_bands:

        print()
        print(
            band.upper()
        )

        for result in (
            contributions[band]
        ):

            print(
                f"  {result['file']:<25}"
                f"{result['contribution_percent']:>7.2f}%"
            )

    print()
    print(
        "========================================"
    )

    print(
        "OVERALL STEM RANKING"
    )

    print(
        "========================================"
    )

    print()

    for result in ranking:

        print(
            f"{result['rank']}. "
            f"{result['file']:<25}"
            f"Score: "
            f"{result['weighted_contribution_score']:.2f}"
        )

    print()

    print(
        "========================================"
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    deviation_report = load_json(
        DEVIATION_FILE
    )

    problem_bands = find_problem_bands(
        deviation_report
    )

    if not problem_bands:

        print()
        print(
            "No statistically significant "
            "problem bands detected."
        )
        print()

        return

    stem_files = [
        file_name
        for file_name in os.listdir(
            TARGET_FOLDER
        )
        if file_name.lower().endswith(
            (".wav", ".aif", ".aiff")
        )
        and file_name != MIX_FILE
    ]

    stem_files.sort()

    if not stem_files:

        raise FileNotFoundError(
            "No stem files found in target folder."
        )

    print()
    print(
        "Analyzing stems..."
    )
    print()

    stem_results = []

    for file_name in stem_files:

        file_path = os.path.join(
            TARGET_FOLDER,
            file_name
        )

        print(
            f"  {file_name}"
        )

        result = analyze_stem(
            file_path
        )

        stem_results.append(
            result
        )

    contributions = (
        calculate_contributions(
            stem_results,
            problem_bands
        )
    )

    ranking = build_ranking(
        contributions,
        deviation_report
    )

    save_report(
        deviation_report,
        problem_bands,
        contributions,
        ranking
    )

    print_report(
        problem_bands,
        contributions,
        ranking
    )

    print()

    print(
        "Stem contribution report saved to:"
    )

    print(
        STEM_OUTPUT_FILE
    )

    print()


if __name__ == "__main__":
    main()