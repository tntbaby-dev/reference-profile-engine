import json
import os


INPUT_FILE = (
    "output/stereo_deviation_report.json"
)

OUTPUT_FILE = (
    "output/stereo_engineering_diagnosis.json"
)


def load_json(file_path):
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


def diagnose_stereo(report):

    parameters = report[
        "parameters"
    ]

    diagnoses = []

    lr_balance = parameters[
        "lr_balance_db"
    ]

    phase = parameters[
        "phase_correlation"
    ]

    mid_side = parameters[
        "mid_side_ratio_db"
    ]

    mono = parameters[
        "mono_compatibility_db"
    ]

    # --------------------------------------------------
    # DIAGNOSIS 1
    # L/R imbalance
    # --------------------------------------------------

    if (
        lr_balance["classification"]
        in {
            "significant_deviation",
            "extreme_deviation"
        }
        or
        (
            lr_balance["classification"]
            == "moderate_deviation"
        )
    ):

        diagnoses.append({
            "diagnosis":
                "left_right_balance_deviation",

            "severity":
                "moderate",

            "confidence":
                "high",

            "evidence": [
                "L/R balance differs meaningfully from the reference profile."
            ],

            "interpretation":
                "The stereo image is measurably weighted toward one channel relative to the reference profile. Investigate channel balance, asymmetric source placement, panning, or unequal processing before making corrective changes."
        })

    # --------------------------------------------------
    # DIAGNOSIS 2
    # Phase
    # --------------------------------------------------

    if (
        phase["classification"]
        in {
            "significant_deviation",
            "extreme_deviation"
        }
    ):

        diagnoses.append({
            "diagnosis":
                "phase_relationship_deviation",

            "severity":
                "moderate",

            "confidence":
                "moderate",

            "evidence": [
                "Phase correlation differs substantially from the reference profile."
            ],

            "interpretation":
                "The relationship between the left and right channels differs substantially from the reference profile. Investigate stereo processing, polarity, time differences, or wide elements before applying corrective processing."
        })

    else:

        diagnoses.append({
            "diagnosis":
                "phase_relationship_within_reference",

            "severity":
                "none",

            "confidence":
                "high",

            "evidence": [
                "Phase correlation is within the reference profile."
            ],

            "interpretation":
                "The left/right phase relationship is not meaningfully different from the professional reference set."
        })

    # --------------------------------------------------
    # DIAGNOSIS 3
    # Mid/Side relationship
    # --------------------------------------------------

    if (
        mid_side["classification"]
        in {
            "significant_deviation",
            "extreme_deviation"
        }
    ):

        diagnoses.append({
            "diagnosis":
                "mid_side_energy_deviation",

            "severity":
                "moderate",

            "confidence":
                "moderate",

            "evidence": [
                "Mid/Side energy relationship differs substantially from the reference profile."
            ],

            "interpretation":
                "The balance between center and side energy differs substantially from the reference profile. Investigate stereo width, panning, side processing, and center-energy distribution before making corrective changes."
        })

    else:

        diagnoses.append({
            "diagnosis":
                "mid_side_relationship_within_reference",

            "severity":
                "none",

            "confidence":
                "high",

            "evidence": [
                "Mid/Side energy relationship is within the reference profile."
            ],

            "interpretation":
                "The center-to-side energy relationship is consistent with the professional reference set."
        })

    # --------------------------------------------------
    # DIAGNOSIS 4
    # Mono compatibility
    # --------------------------------------------------

    if (
        mono["classification"]
        in {
            "significant_deviation",
            "extreme_deviation"
        }
    ):

        diagnoses.append({
            "diagnosis":
                "mono_compatibility_deviation",

            "severity":
                "high",

            "confidence":
                "high",

            "evidence": [
                "Mono compatibility differs substantially from the reference profile."
            ],

            "interpretation":
                "Summing the stereo signal to mono produces a substantially different level relationship from the reference profile. Investigate phase interaction, stereo effects, polarity, and side-heavy elements."
        })

    else:

        diagnoses.append({
            "diagnosis":
                "mono_compatibility_within_reference",

            "severity":
                "none",

            "confidence":
                "high",

            "evidence": [
                "Mono compatibility is within the reference profile."
            ],

            "interpretation":
                "The stereo signal maintains a mono relationship consistent with the professional reference set."
        })

    return diagnoses


def prioritize_diagnoses(
    diagnoses
):

    priority_order = {
        "high": 1,
        "moderate": 2,
        "low": 3,
        "none": 4
    }

    return sorted(
        diagnoses,
        key=lambda item:
            priority_order.get(
                item["severity"],
                99
            )
    )


def save_output(
    report,
    diagnoses
):

    output = {
        "file":
            report["file"],

        "measurement_type":
            "stereo_engineering_diagnosis",

        "diagnoses":
            diagnoses
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


def print_report(
    report,
    diagnoses
):

    print()
    print(
        "========================================"
    )
    print(
        "STEREO ENGINEERING DIAGNOSIS"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"Target mix: "
        f"{report['file']}"
    )

    print()

    for index, diagnosis in enumerate(
        diagnoses,
        start=1
    ):

        print(
            f"{index}. "
            f"{diagnosis['diagnosis']}"
        )

        print(
            f"   Severity: "
            f"{diagnosis['severity']}"
        )

        print(
            f"   Confidence: "
            f"{diagnosis['confidence']}"
        )

        print(
            "   Interpretation:"
        )

        print(
            f"   {diagnosis['interpretation']}"
        )

        print()


def main():

    report = load_json(
        INPUT_FILE
    )

    diagnoses = diagnose_stereo(
        report
    )

    diagnoses = prioritize_diagnoses(
        diagnoses
    )

    save_output(
        report,
        diagnoses
    )

    print_report(
        report,
        diagnoses
    )

    print(
        "========================================"
    )

    print(
        "Stereo engineering diagnosis saved to:"
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