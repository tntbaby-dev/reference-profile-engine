import os
import json
import numpy as np
import soundfile as sf


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

REFERENCE_FOLDER = "references"

OUTPUT_FOLDER = "output"

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER,
    "dynamics_reference_measurements.json"
)

FRAME_DURATION_SECONDS = 0.100


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
# Convert to mono
# ---------------------------------------------------------

def convert_to_mono(audio):
    """
    Convert stereo or multichannel audio to mono
    by averaging channels.
    """

    return np.mean(
        audio,
        axis=1
    )


# ---------------------------------------------------------
# Calculate peak level
# ---------------------------------------------------------

def calculate_peak_dbfs(audio):
    """
    Calculate sample peak level in dBFS.
    """

    peak = np.max(
        np.abs(audio)
    )

    if peak <= 0:
        return -np.inf

    return float(
        20.0 * np.log10(peak)
    )


# ---------------------------------------------------------
# Calculate RMS
# ---------------------------------------------------------

def calculate_rms(audio):
    """
    Calculate RMS amplitude.
    """

    return float(
        np.sqrt(
            np.mean(
                np.square(audio)
            )
        )
    )


# ---------------------------------------------------------
# Calculate crest factor
# ---------------------------------------------------------

def calculate_crest_factor(
    audio
):
    """
    Calculate crest factor in dB.

    Crest factor describes the relationship
    between peak amplitude and RMS amplitude.
    """

    peak = np.max(
        np.abs(audio)
    )

    rms = calculate_rms(
        audio
    )

    if peak <= 0 or rms <= 0:
        return 0.0

    crest_factor_db = (
        20.0
        * np.log10(
            peak / rms
        )
    )

    return float(
        crest_factor_db
    )


# ---------------------------------------------------------
# Calculate frame RMS values
# ---------------------------------------------------------

def calculate_frame_rms(
    audio,
    sample_rate
):
    """
    Calculate RMS for consecutive short
    audio frames.
    """

    frame_size = int(
        sample_rate
        * FRAME_DURATION_SECONDS
    )

    if frame_size < 1:
        raise ValueError(
            "Invalid frame size."
        )

    frame_count = (
        len(audio)
        // frame_size
    )

    if frame_count < 2:
        raise ValueError(
            "Audio is too short for "
            "dynamic analysis."
        )

    frame_rms_values = []

    for index in range(
        frame_count
    ):

        start = (
            index
            * frame_size
        )

        end = (
            start
            + frame_size
        )

        frame = audio[
            start:end
        ]

        rms = calculate_rms(
            frame
        )

        if rms > 0:

            rms_dbfs = (
                20.0
                * np.log10(rms)
            )

            frame_rms_values.append(
                rms_dbfs
            )

    if len(
        frame_rms_values
    ) < 2:

        raise ValueError(
            "Insufficient measurable "
            "RMS frames."
        )

    return np.array(
        frame_rms_values,
        dtype=np.float64
    )


# ---------------------------------------------------------
# Calculate RMS dynamic variation
# ---------------------------------------------------------

def calculate_rms_dynamic_variation(
    frame_rms_values
):
    """
    Calculate statistical variation of short-term RMS.

    The metric is the standard deviation of
    100 ms RMS levels.
    """

    return float(
        np.std(
            frame_rms_values
        )
    )


# ---------------------------------------------------------
# Calculate RMS percentile spread
# ---------------------------------------------------------

def calculate_rms_percentile_spread(
    frame_rms_values
):
    """
    Calculate the difference between the
    90th and 10th percentile of short-term RMS.
    """

    p10 = np.percentile(
        frame_rms_values,
        10
    )

    p90 = np.percentile(
        frame_rms_values,
        90
    )

    return float(
        p90 - p10
    )


# ---------------------------------------------------------
# Analyze one reference
# ---------------------------------------------------------

def analyze_reference(
    file_path
):
    """
    Analyze the dynamic characteristics
    of one reference track.
    """

    print()
    print(
        f"Analyzing: {file_path}"
    )

    audio, sample_rate = load_audio(
        file_path
    )

    mono = convert_to_mono(
        audio
    )

    peak_dbfs = calculate_peak_dbfs(
        mono
    )

    crest_factor_db = (
        calculate_crest_factor(
            mono
        )
    )

    frame_rms_values = (
        calculate_frame_rms(
            mono,
            sample_rate
        )
    )

    rms_dynamic_variation_db = (
        calculate_rms_dynamic_variation(
            frame_rms_values
        )
    )

    rms_percentile_spread_db = (
        calculate_rms_percentile_spread(
            frame_rms_values
        )
    )

    return {
        "file":
            os.path.basename(file_path),

        "sample_rate":
            int(sample_rate),

        "channels":
            int(audio.shape[1]),

        "duration_seconds":
            float(
                len(audio)
                / sample_rate
            ),

        "dynamics": {
            "peak_dbfs":
                float(peak_dbfs),

            "crest_factor_db":
                float(
                    crest_factor_db
                ),

            "rms_dynamic_variation_db":
                float(
                    rms_dynamic_variation_db
                ),

            "rms_percentile_spread_db":
                float(
                    rms_percentile_spread_db
                )
        }
    }


# ---------------------------------------------------------
# Analyze all references
# ---------------------------------------------------------

def analyze_all_references():
    """
    Analyze every reference audio file.
    """

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    if not os.path.exists(
        REFERENCE_FOLDER
    ):

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

        results.append(
            result
        )

    output = {
        "reference_count":
            len(results),

        "measurement_type":
            "dynamic_range_metrics",

        "parameters": {
            "peak_dbfs":
                "sample_peak_level",

            "crest_factor_db":
                "peak_to_rms_ratio",

            "rms_dynamic_variation_db":
                "standard_deviation_of_100ms_rms",

            "rms_percentile_spread_db":
                "p90_minus_p10_of_100ms_rms"
        },

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
    print("DYNAMICS REFERENCE ANALYSIS COMPLETE")
    print("========================================")
    print()

    print(
        f"References analyzed: "
        f"{len(results)}"
    )

    print()

    for result in results:

        dynamics = result[
            "dynamics"
        ]

        print(
            result["file"]
        )

        print(
            f"  Peak: "
            f"{dynamics['peak_dbfs']:.2f} dBFS"
        )

        print(
            f"  Crest factor: "
            f"{dynamics['crest_factor_db']:.2f} dB"
        )

        print(
            f"  RMS variation: "
            f"{dynamics['rms_dynamic_variation_db']:.2f} dB"
        )

        print(
            f"  RMS P90-P10: "
            f"{dynamics['rms_percentile_spread_db']:.2f} dB"
        )

        print()

    print(
        "========================================"
    )

    print(
        "Dynamics measurements saved to:"
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