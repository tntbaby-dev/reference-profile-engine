import json
import os
import sys


INPUT_FILE = (
    "output/dynamics_deviation_report.json"
)

OUTPUT_FILE = (
    "output/dynamics_engineering_diagnosis.json"
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


def diagnose_dynamics(report):
    parameters = report[
        "parameters"
    ]

    diagnoses = []

    peak = parameters[
        "peak_dbfs"
    ]

    crest = parameters[
        "crest_factor_db"
    ]

    rms_variation = parameters[
        "rms_dynamic_variation_db"
    ]

    rms_spread = parameters[
        "rms_percentile_spread_db"
    ]

    # --------------------------------------------------
    # DIAGNOSIS 1
    # Overall peak reduction
    # --------------------------------------------------

    if (
        peak["direction"]
        == "below_reference"
        and peak["classification"]
        in {
            "significant_deviation",
            "extreme_deviation"
        }
    ):

        diagnoses.append({
            "diagnosis":
                "reduced_peak_level",

            "severity":
                "moderate",

            "confidence":
                "high",

            "evidence": [
                "Peak level is substantially below the reference profile."
            ],

            "interpretation":
                "This is consistent with the overall level reduction already detected by the loudness analysis and does not by itself establish a dynamics-processing problem."
        })

    # --------------------------------------------------
    # DIAGNOSIS 2
    # High crest factor
    # --------------------------------------------------

    if (
        crest["direction"]
        == "above_reference"
        and crest["classification"]
        in {
            "significant_deviation",
            "extreme_deviation"
        }
    ):

        diagnoses.append({
            "diagnosis":
                "elevated_peak_to_rms_ratio",

            "severity":
                "high",

            "confidence":
                "high",

            "evidence": [
                "Crest factor is substantially above the reference profile."
            ],

            "interpretation":
                "Peak energy is unusually high relative to average RMS energy. This can indicate relatively strong transient or peak energy, reduced sustained energy, or insufficient dynamic control, but the measurement alone does not establish the cause."
        })

    # --------------------------------------------------
    # DIAGNOSIS 3
    # Low RMS dynamic variation
    # --------------------------------------------------

    if (
        rms_variation["direction"]
        == "below_reference"
        and rms_variation["classification"]
        in {
            "significant_deviation",
            "extreme_deviation"
        }
    ):

        diagnoses.append({
            "diagnosis":
                "reduced_short_term_rms_variation",

            "severity":
                "moderate",

            "confidence":
                "moderate",

            "evidence": [
                "Short-term RMS variation is substantially below the reference profile."
            ],

            "interpretation":
                "The short-term energy envelope varies less than the reference profile. This may reflect a relatively stable sustained-energy level, arrangement characteristics, processing, or reduced contrast between sections."
        })

    # --------------------------------------------------
    # DIAGNOSIS 4
    # Normal RMS percentile spread
    # --------------------------------------------------

    if (
        rms_spread["classification"]
        == "within_reference"
    ):

        diagnoses.append({
            "diagnosis":
                "overall_rms_distribution_within_reference",

            "severity":
                "none",

            "confidence":
                "high",

            "evidence": [
                "RMS P90-P10 spread is within the reference profile."
            ],

            "interpretation":
                "The broader distribution of short-term RMS levels is not meaningfully different from the reference profile."
        })

    # --------------------------------------------------
    # DIAGNOSIS 5
    # Combined crest + RMS variation pattern
    # --------------------------------------------------

    if (
        crest["classification"]
        in {
            "significant_deviation",
            "extreme_deviation"
        }
        and crest["direction"]
        == "above_reference"
        and rms_variation["classification"]
        in {
            "significant_deviation",
            "extreme_deviation"
        }
        and rms_variation["direction"]
        == "below_reference"
    ):

        diagnoses.append({
            "diagnosis":
                "peak_sustained_energy_imbalance",

            "severity":
                "high",

            "confidence":
                "high",

            "evidence": [
                "Crest factor is substantially above reference.",
                "RMS dynamic variation is substantially below reference."
            ],

            "interpretation":
                "The mix shows unusually large separation between peak and RMS energy while short-term RMS variation is restrained. Investigate the balance between transient energy and sustained energy before applying dynamics processing."
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
            "dynamics_engineering_diagnosis",

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
        "DYNAMICS ENGINEERING DIAGNOSIS"
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

    diagnoses = diagnose_dynamics(
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
        "Dynamics engineering diagnosis saved to:"
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