import os
import json
import numpy as np
import soundfile as sf
from scipy.signal import stft


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

TARGET_FOLDER = "target"
OUTPUT_FOLDER = "output"
OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "stem_contributions.json"
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
# Load audio
# ---------------------------------------------------------

def load_audio(file_path):
    """
    Load an audio file as float32 audio.
    """

    audio, sample_rate = sf.read(
        file_path,
        always_2d=True
    )

    return audio.astype(np.float32), sample_rate


# ---------------------------------------------------------
# Calculate stereo-safe spectral power
# ---------------------------------------------------------

def calculate_stereo_power(
    audio,
    sample_rate
):
    """
    Calculate average spectral power across channels.
    """

    left = audio[:, 0]

    if audio.shape[1] >= 2:
        right = audio[:, 1]
    else:
        right = left

    frequencies, times, left_stft = stft(
        left,
        fs=sample_rate,
        window="hann",
        nperseg=FRAME_SIZE,
        noverlap=FRAME_SIZE - HOP_SIZE,
        boundary=None,
        padded=False
    )

    _, _, right_stft = stft(
        right,
        fs=sample_rate,
        window="hann",
        nperseg=FRAME_SIZE,
        noverlap=FRAME_SIZE - HOP_SIZE,
        boundary=None,
        padded=False
    )

    left_power = np.abs(left_stft) ** 2
    right_power = np.abs(right_stft) ** 2

    stereo_power = (
        left_power + right_power
    ) / 2

    return frequencies, stereo_power


# ---------------------------------------------------------
# Calculate band power
# ---------------------------------------------------------

def calculate_band_power(
    frequencies,
    stereo_power
):
    """
    Calculate total spectral power for each
    frequency band.
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
# Calculate relative contribution
# ---------------------------------------------------------

def calculate_relative_contribution(
    band_power
):
    """
    Calculate the percentage of the stem's total
    measured spectral energy contained in each band.
    """

    total_power = sum(
        band_power.values()
    )

    if total_power <= 0:
        raise ValueError(
            "Stem contains no measurable spectral energy."
        )

    contribution = {}

    for band, power in band_power.items():

        contribution[band] = float(
            (power / total_power) * 100
        )

    return contribution


# ---------------------------------------------------------
# Analyze one stem
# ---------------------------------------------------------

def analyze_stem(file_path):
    """
    Analyze one stem.
    """

    print(
        f"Analyzing stem: {file_path}"
    )

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

    relative_contribution = (
        calculate_relative_contribution(
            band_power
        )
    )

    duration_seconds = (
        len(audio) / sample_rate
    )

    return {
        "file": os.path.basename(file_path),
        "sample_rate": int(sample_rate),
        "channels": int(audio.shape[1]),
        "duration_seconds": float(
            duration_seconds
        ),
        "band_energy_percent": (
            relative_contribution
        )
    }


# ---------------------------------------------------------
# Analyze all stems
# ---------------------------------------------------------

def analyze_all_stems():
    """
    Analyze every WAV, AIFF, or AIF file
    inside the target folder.
    """

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    if not os.path.exists(TARGET_FOLDER):
        raise FileNotFoundError(
            f"Target folder not found: {TARGET_FOLDER}"
        )

    stem_files = [
        file_name
        for file_name in os.listdir(
            TARGET_FOLDER
        )
        if file_name.lower().endswith(
            (".wav", ".aif", ".aiff")
        )
    ]

    stem_files.sort()

    if not stem_files:
        raise FileNotFoundError(
            "No stem audio files found inside "
            "the target folder."
        )

    results = []

    for file_name in stem_files:

        file_path = os.path.join(
            TARGET_FOLDER,
            file_name
        )

        result = analyze_stem(
            file_path
        )

        results.append(result)

    output = {
        "stem_count": len(results),
        "measurement_type": (
            "relative_spectral_energy_percent"
        ),
        "stems": results
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

    print()
    print("========================================")
    print("STEM CONTRIBUTION ANALYSIS")
    print("========================================")
    print()

    print(
        f"Stems analyzed: {len(results)}"
    )

    print()

    for result in results:

        print(
            result["file"]
        )

        for band, percentage in (
            result[
                "band_energy_percent"
            ].items()
        ):

            print(
                f"  {band:<12}"
                f"{percentage:>7.2f}%"
            )

        print()

    print("========================================")
    print(
        "Stem contribution report saved to:"
    )
    print(
        OUTPUT_FILE
    )
    print("========================================")
    print()


# ---------------------------------------------------------
# Run program
# ---------------------------------------------------------

if __name__ == "__main__":
    analyze_all_stems()