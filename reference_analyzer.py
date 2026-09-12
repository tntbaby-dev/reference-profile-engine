import os
import json
import numpy as np
import soundfile as sf
from scipy.signal import stft


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

REFERENCE_FOLDER = "references"
OUTPUT_FOLDER = "output"
OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "reference_measurements.json"
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
    Load an audio file and return stereo-safe audio data.
    """

    audio, sample_rate = sf.read(
        file_path,
        always_2d=True
    )

    return audio.astype(np.float32), sample_rate


# ---------------------------------------------------------
# Calculate stereo spectral power
# ---------------------------------------------------------

def calculate_stereo_power(audio, sample_rate):
    """
    Calculate stereo spectral power using STFT.

    Returns:
        frequencies
        times
        stereo_power
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

    return frequencies, times, stereo_power


# ---------------------------------------------------------
# Calculate relative band energy
# ---------------------------------------------------------

def calculate_relative_band_energy(
    frequencies,
    stereo_power
):
    """
    Calculate the relative energy contribution
    of each frequency band.

    The result is expressed as a percentage
    of total measured spectral energy from
    20 Hz to 16 kHz.
    """

    analysis_mask = (
        (frequencies >= 20)
        & (frequencies < 16000)
    )

    total_power = np.sum(
        stereo_power[analysis_mask, :]
    )

    if total_power <= 0:
        raise ValueError(
            "Audio contains no measurable spectral energy."
        )

    band_percentages = {}

    for band_name, (
        lower_frequency,
        upper_frequency
    ) in FREQUENCY_BANDS.items():

        band_mask = (
            (frequencies >= lower_frequency)
            & (frequencies < upper_frequency)
        )

        band_power = np.sum(
            stereo_power[band_mask, :]
        )

        percentage = (
            band_power / total_power
        ) * 100

        band_percentages[band_name] = float(
            percentage
        )

    return band_percentages


# ---------------------------------------------------------
# Analyze one reference track
# ---------------------------------------------------------

def analyze_reference(file_path):
    """
    Analyze one reference WAV file.
    """

    print()
    print(f"Analyzing: {file_path}")

    audio, sample_rate = load_audio(file_path)

    frequencies, times, stereo_power = (
        calculate_stereo_power(
            audio,
            sample_rate
        )
    )

    band_percentages = (
        calculate_relative_band_energy(
            frequencies,
            stereo_power
        )
    )

    duration_seconds = (
        len(audio) / sample_rate
    )

    result = {
        "file": os.path.basename(file_path),
        "sample_rate": int(sample_rate),
        "channels": int(audio.shape[1]),
        "duration_seconds": float(
            duration_seconds
        ),
        "bands": band_percentages
    }

    return result


# ---------------------------------------------------------
# Analyze all references
# ---------------------------------------------------------

def analyze_all_references():
    """
    Analyze every WAV file in the references folder.
    """

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    if not os.path.exists(REFERENCE_FOLDER):
        raise FileNotFoundError(
            f"Reference folder not found: "
            f"{REFERENCE_FOLDER}"
        )

    reference_files = [
        file_name
        for file_name in os.listdir(
            REFERENCE_FOLDER
        )
        if file_name.lower().endswith(
            (".wav", ".aif", ".aiff")
        )
    ]

    reference_files.sort()

    if not reference_files:
        raise FileNotFoundError(
            "No reference audio files found "
            "inside the references folder."
        )

    results = []

    for file_name in reference_files:

        file_path = os.path.join(
            REFERENCE_FOLDER,
            file_name
        )

        result = analyze_reference(
            file_path
        )

        results.append(result)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print()
    print("========================================")
    print("REFERENCE ANALYSIS COMPLETE")
    print("========================================")
    print()
    print(f"References analyzed: {len(results)}")
    print(f"Output: {OUTPUT_FILE}")
    print()

    for result in results:

        print(result["file"])

        for band, percentage in (
            result["bands"].items()
        ):
            print(
                f"  {band:<12} "
                f"{percentage:>6.2f}%"
            )

        print()


# ---------------------------------------------------------
# Run program
# ---------------------------------------------------------

if __name__ == "__main__":
    analyze_all_references()