import os
import subprocess
import sys


TARGET_DIRECTORY = "target"


MIX_PIPELINE = [

    (
        "Spectral deviation detection",
        "deviation_detector.py"
    ),

    (
        "Spectral engineering diagnosis",
        "engineering_diagnosis.py"
    ),

    (
        "Diagnosis prioritization",
        "diagnosis_prioritizer.py"
    ),

    (
        "Loudness deviation detection",
        "loudness_deviation_detector.py"
    ),

    (
        "Loudness engineering diagnosis",
        "loudness_engineering_diagnosis.py"
    ),

    (
        "Loudness diagnosis validation",
        "validate_loudness_engineering_diagnosis.py"
    ),

    (
        "Dynamics deviation detection",
        "dynamics_deviation_detector.py"
    ),

    (
        "Dynamics engineering diagnosis",
        "dynamics_engineering_diagnosis.py"
    ),

    (
        "Dynamics diagnosis validation",
        "validate_dynamics_engineering_diagnosis.py"
    ),

    (
        "Stereo deviation detection",
        "stereo_deviation_detector.py"
    ),

    (
        "Stereo engineering diagnosis",
        "stereo_engineering_diagnosis.py"
    ),

    (
        "Stereo diagnosis validation",
        "validate_stereo_engineering_diagnosis.py"
    ),
]


STEM_PIPELINE = [

    (
        "Stem contribution analysis",
        "stem_contribution_analyzer.py"
    ),

    (
        "Stem contribution ranking",
        "stem_contribution_ranker.py"
    ),

    (
        "Source-level diagnosis",
        "source_level_diagnosis.py"
    ),

    (
        "Engineering recommendation engine",
        "recommendation_engine.py"
    ),

    (
        "Recommendation engine validation",
        "validate_recommendation_engine.py"
    ),
]


FINAL_PIPELINE = [

    (
        "Cross-domain reasoning",
        "cross_domain_reasoning.py"
    ),

    (
        "File Handling Lead",
        "file_handling_lead.py"
    ),
]


def find_target_files():

    if not os.path.exists(
        TARGET_DIRECTORY
    ):

        print()
        print(
            "ERROR: target/ directory does not exist."
        )

        sys.exit(1)

    audio_files = [

        file_name
        for file_name
        in os.listdir(
            TARGET_DIRECTORY
        )
        if file_name.lower().endswith(
            (
                ".wav",
                ".aif",
                ".aiff"
            )
        )
    ]

    if not audio_files:

        print()
        print(
            "ERROR: No WAV, AIFF, or AIF files found in target/."
        )

        sys.exit(1)

    return audio_files


def identify_mix(
    audio_files
):

    mix_candidates = []

    for file_name in audio_files:

        base_name = os.path.splitext(
            file_name
        )[0]

        is_stem = False

        for other_file in audio_files:

            if other_file == file_name:
                continue

            other_base = os.path.splitext(
                other_file
            )[0]

            if other_base.startswith(
                base_name + "_"
            ):

                is_stem = True
                break

        if not is_stem:

            mix_candidates.append(
                file_name
            )

    if not mix_candidates:

        print()
        print(
            "ERROR: Could not identify the target mix."
        )

        print()
        print(
            "Expected a mix such as:"
        )

        print(
            "target/ditb.wav"
        )

        sys.exit(1)

    if len(mix_candidates) > 1:

        print()
        print(
            "ERROR: More than one possible target mix found."
        )

        print()

        for file_name in mix_candidates:

            print(
                f"- {file_name}"
            )

        print()

        print(
            "Keep one target mix and its associated stems in target/."
        )

        sys.exit(1)

    return mix_candidates[0]


def run_step(
    description,
    script,
    target_file=None
):

    print()
    print("=" * 50)
    print(description)
    print("=" * 50)

    command = [
        sys.executable,
        script
    ]

    if target_file is not None:

        command.append(
            os.path.join(
                TARGET_DIRECTORY,
                target_file
            )
        )

    result = subprocess.run(
        command
    )

    if result.returncode != 0:

        print()
        print(
            f"PIPELINE STOPPED: {script}"
        )

        print(
            f"Exit code: {result.returncode}"
        )

        sys.exit(
            result.returncode
        )


def main():

    audio_files = find_target_files()

    target_file = identify_mix(
        audio_files
    )

    target_base_name = os.path.splitext(
        target_file
    )[0]

    stem_files = [

        file_name
        for file_name
        in audio_files
        if file_name != target_file
        and os.path.splitext(
            file_name
        )[0].startswith(
            target_base_name + "_"
        )
    ]

    print()
    print(
        "========================================"
    )
    print(
        "TARGET ANALYSIS PIPELINE"
    )
    print(
        "========================================"
    )

    print()
    print(
        "Target mix:"
    )

    print(
        f"target/{target_file}"
    )

    print()

    if stem_files:

        print(
            "Stems detected:"
        )

        for stem_file in stem_files:

            print(
                f"- target/{stem_file}"
            )

    else:

        print(
            "No stems detected."
        )

    print()

    #
    # MIX ANALYSIS
    #

    for description, script in MIX_PIPELINE:

        run_step(
            description,
            script,
            target_file
        )

    #
    # STEM ANALYSIS
    #

    if stem_files:

        for description, script in STEM_PIPELINE:

            run_step(
                description,
                script
            )

    else:

        print()
        print("=" * 50)
        print(
            "STEM ANALYSIS"
        )
        print("=" * 50)

        print()
        print(
            "No stems found."
        )

        print(
            "Skipping stem contribution and source-level analysis."
        )

    #
    # FINAL REASONING
    #

    for description, script in FINAL_PIPELINE:

        run_step(
            description,
            script
        )

    print()
    print(
        "========================================"
    )
    print(
        "TARGET ANALYSIS COMPLETE"
    )
    print(
        "========================================"
    )

    print()

    print(
        f"Target analyzed: {target_file}"
    )

    print()

    if stem_files:

        print(
            f"Stems analyzed: {len(stem_files)}"
        )

    else:

        print(
            "Stems analyzed: 0"
        )

    print()

    print(
        "File Handling Lead results:"
    )

    print(
        "output/file_handling_lead.json"
    )

    print()


if __name__ == "__main__":

    main()