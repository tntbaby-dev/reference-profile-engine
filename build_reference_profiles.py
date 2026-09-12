import subprocess
import sys


REFERENCE_PIPELINE = [
    (
        "Spectral reference analysis",
        "reference_analyzer.py"
    ),
    (
        "Spectral profile building",
        "profile_builder.py"
    ),
    (
        "Spectral profile validation",
        "validate_profile.py"
    ),
    (
        "Loudness reference analysis",
        "loudness_reference_analyzer.py"
    ),
    (
        "Loudness profile building",
        "loudness_profile_builder.py"
    ),
    (
        "Loudness profile validation",
        "validate_loudness_profile.py"
    ),
    (
        "Dynamics reference analysis",
        "dynamics_reference_analyzer.py"
    ),
    (
        "Dynamics profile building",
        "dynamics_profile_builder.py"
    ),
    (
        "Stereo reference analysis",
        "stereo_reference_analyzer.py"
    ),
    (
        "Stereo profile building",
        "stereo_profile_builder.py"
    ),
]


def run_step(
    description,
    script
):

    print()
    print("=" * 50)
    print(description)
    print("=" * 50)

    result = subprocess.run(
        [
            sys.executable,
            script
        ]
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

    print()
    print(
        "========================================"
    )
    print(
        "REFERENCE PROFILE PIPELINE"
    )
    print(
        "========================================"
    )

    print()
    print(
        "Building reference profiles from:"
    )

    print(
        "references/"
    )

    for description, script in (
        REFERENCE_PIPELINE
    ):

        run_step(
            description,
            script
        )

    print()
    print(
        "========================================"
    )
    print(
        "REFERENCE PIPELINE COMPLETE"
    )
    print(
        "========================================"
    )

    print()
    print(
        "Reference profiles are ready."
    )

    print()


if __name__ == "__main__":

    main()
