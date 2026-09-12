import os
import json
import numpy as np
import soundfile as sf
import pyloudnorm as pyln


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

REFERENCE_FOLDER = "references"

OUTPUT_FOLDER = "output"

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "loudness_reference_measurements.json"
)


# ---------------------------------------------------------
# Load audio
# ---------------------------------------------------------

def load_audio(file_path):
    """
    Load audio for loudness analysis.
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
# Measure loudness
# ---------------------------------------------------------

def measure_loudness(
    audio,
    sample_rate
):
    """
    Measure loudness and level-related properties.
    """

    meter = pyln.Meter(
        sample_rate
    )

    integrated_lufs = meter.integrated_loudness(
        audio
    )

    true_peak_dbfs = calculate_true_peak(
        audio,
        sample_rate
    )

    rms_dbfs = calculate_rms(
        audio
    )

    loudness_range = calculate_loudness_range(
        audio,
        sample_rate
    )

    return {
        "integrated_lufs":
            float(integrated_lufs),

        "true_peak_dbfs":
            float(true_peak_dbfs),

        "rms_dbfs":
            float(rms_dbfs),

        "loudness_range_lu":
            float(loudness_range)
    }


# ---------------------------------------------------------
# Calculate RMS
# ---------------------------------------------------------

def calculate_rms(audio):
    """
    Calculate RMS level in dBFS.

    RMS is calculated across all samples
    and available channels.
    """

    rms = np.sqrt(
        np.mean(
            np.square(audio)
        )
    )

    if rms <= 0:
        return -np.inf

    return 20 * np.log10(
        rms
    )


# ---------------------------------------------------------
# Calculate true peak
# ---------------------------------------------------------

def calculate_true_peak(
    audio,
    sample_rate
):
    """
    Estimate true peak by 4x oversampling
    each channel using scipy.signal.resample_poly.
    """

    from scipy.signal import resample_poly

    oversampled_audio = resample_poly(
        audio,
        4,
        1,
        axis=0
    )

    peak = np.max(
        np.abs(
            oversampled_audio
        )
    )

    if peak <= 0:
        return -np.inf

    return 20 * np.log10(
        peak
    )


# ---------------------------------------------------------
# Calculate loudness range
# ---------------------------------------------------------

def calculate_loudness_range(
    audio,
    sample_rate
):
    """
    Calculate Loudness Range (LRA).

    Uses BS.1770-style loudness measurements
    over the audio.
    """

    meter = pyln.Meter(
        sample_rate
    )

    try:

        loudness_range = (
            meter.loudness_range(
                audio
            )
        )

        return float(
            loudness_range
        )

    except AttributeError:

        # Some pyloudnorm versions do not expose
        # loudness_range directly.

        return 0.0


# ---------------------------------------------------------
# Analyze one reference
# ---------------------------------------------------------

def analyze_reference(
    file_path
):
    """
    Analyze one professional reference track.
    """

    print()
    print(
        f"Analyzing: {file_path}"
    )

    audio, sample_rate = load_audio(
        file_path
    )

    loudness = measure_loudness(
        audio,
        sample_rate
    )

    duration_seconds = (
        len(audio) / sample_rate
    )

    result = {
        "file":
            os.path.basename(file_path),

        "sample_rate":
            int(sample_rate),

        "channels":
            int(audio.shape[1]),

        "duration_seconds":
            float(duration_seconds),

        "loudness":
            loudness
    }

    return result


# ---------------------------------------------------------
# Analyze all references
# ---------------------------------------------------------

def analyze_all_references():
    """
    Analyze every WAV, AIFF, or AIF reference.
    """

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    if not os.path.exists(
        REFERENCE_FOLDER
    ):

        raise FileNotFoundError(
            "Reference folder not found: "
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

        results.append(
            result
        )

    output = {
        "reference_count":
            len(results),

        "measurement_type":
            "loudness_and_level_metrics",

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

    print()
    print("========================================")
    print("LOUDNESS REFERENCE ANALYSIS")
    print("========================================")
    print()

    print(
        f"References analyzed: "
        f"{len(results)}"
    )

    print()

    for result in results:

        loudness = result[
            "loudness"
        ]

        print(
            result["file"]
        )

        print(
            f"  Integrated LUFS: "
            f"{loudness['integrated_lufs']:.2f}"
        )

        print(
            f"  True Peak:       "
            f"{loudness['true_peak_dbfs']:.2f} dBFS"
        )

        print(
            f"  RMS:              "
            f"{loudness['rms_dbfs']:.2f} dBFS"
        )

        print(
            f"  Loudness Range:   "
            f"{loudness['loudness_range_lu']:.2f} LU"
        )

        print()

    print(
        "========================================"
    )

    print(
        "Loudness measurements saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "========================================"
    )

    print()


# ---------------------------------------------------------
# Run program
# ---------------------------------------------------------

if __name__ == "__main__":
    analyze_all_references()