import json
import os


INPUT_FILE = (
    "output/loudness_deviation_report.json"
)

OUTPUT_FILE = (
    "output/loudness_engineering_diagnosis.json"
)


# ---------------------------------------------------------
# Load report
# ---------------------------------------------------------

def load_report():
    """
    Load the loudness deviation report.
    """

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"Loudness deviation report not found: "
            f"{INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def get_parameter(
    parameters,
    name
):
    """
    Return one loudness parameter result.
    """

    return parameters.get(
        name,
        {}
    )


def is_below(
    parameters,
    name,
    minimum_z
):
    """
    Check whether a parameter is below
    the reference by at least the given
    z-score.
    """

    result = get_parameter(
        parameters,
        name
    )

    return (
        result.get("z_score", 0)
        <= -minimum_z
    )


def is_above(
    parameters,
    name,
    minimum_z
):
    """
    Check whether a parameter is above
    the reference by at least the given
    z-score.
    """

    result = get_parameter(
        parameters,
        name
    )

    return (
        result.get("z_score", 0)
        >= minimum_z
    )


# ---------------------------------------------------------
# Diagnose overall level reduction
# ---------------------------------------------------------

def diagnose_overall_level_reduction(
    parameters
):
    """
    Detect simultaneous reductions in integrated
    loudness, RMS, and estimated true peak.

    This pattern is treated as evidence of a
    broad level/gain-state difference.

    It is NOT automatically classified as a
    mixing problem.
    """

    lufs_low = is_below(
        parameters,
        "integrated_lufs",
        2.0
    )

    rms_low = is_below(
        parameters,
        "rms_dbfs",
        2.0
    )

    true_peak_low = is_below(
        parameters,
        "estimated_true_peak_dbtp",
        2.0
    )

    if (
        lufs_low
        and rms_low
        and true_peak_low
    ):

        return {
            "issue":
                "overall_level_reduction",

            "severity":
                "high",

            "confidence":
                "high",

            "evidence": [
                "Integrated loudness is substantially below the reference profile.",
                "RMS level is substantially below the reference profile.",
                "Estimated true peak is substantially below the reference profile."
            ],

            "diagnosis":
                "The target mix has a substantially lower "
                "overall level than the professional reference "
                "profile across integrated loudness, RMS, and "
                "estimated true peak.",

            "interpretation":
                "This pattern is consistent with a broad "
                "gain or level difference. It does not by "
                "itself establish that the mix has incorrect "
                "dynamics or requires compression."
        }

    return None


# ---------------------------------------------------------
# Diagnose dynamics relationship
# ---------------------------------------------------------

def diagnose_loudness_range(
    parameters
):
    """
    Interpret Loudness Range relative to the
    reference profile.

    LRA is considered separately from overall level.
    """

    result = get_parameter(
        parameters,
        "loudness_range_lu"
    )

    classification = result.get(
        "classification",
        "unknown"
    )

    direction = result.get(
        "direction",
        "balanced"
    )

    if classification == "within_reference":

        return {
            "issue":
                "loudness_range_within_reference",

            "severity":
                "none",

            "confidence":
                "high",

            "evidence": [
                "Loudness Range is within the reference profile."
            ],

            "diagnosis":
                "The target mix's loudness variation "
                "falls within the observed reference range.",

            "interpretation":
                "There is no strong statistical evidence "
                "from LRA alone that the mix has unusually "
                "restricted or unusually expanded loudness "
                "variation."
        }

    if direction == "below_reference":

        return {
            "issue":
                "reduced_loudness_range",

            "severity":
                "moderate",

            "confidence":
                "moderate",

            "evidence": [
                "Loudness Range is below the reference profile."
            ],

            "diagnosis":
                "The target mix exhibits less loudness "
                "variation than the reference profile.",

            "interpretation":
                "This may indicate greater dynamic constraint, "
                "but additional dynamics measurements are "
                "required before identifying compression or "
                "limiting as the cause."
        }

    if direction == "above_reference":

        return {
            "issue":
                "expanded_loudness_range",

            "severity":
                "moderate",

            "confidence":
                "moderate",

            "evidence": [
                "Loudness Range is above the reference profile."
            ],

            "diagnosis":
                "The target mix exhibits more loudness "
                "variation than the reference profile.",

            "interpretation":
                "This may reflect greater musical dynamics, "
                "arrangement differences, or reduced dynamic "
                "control. Additional dynamics measurements "
                "are required before identifying the cause."
        }

    return None


# ---------------------------------------------------------
# Diagnose peak relationship
# ---------------------------------------------------------

def diagnose_peak_level(
    parameters
):
    """
    Interpret estimated true peak independently
    from overall loudness.
    """

    result = get_parameter(
        parameters,
        "estimated_true_peak_dbtp"
    )

    z_score = result.get(
        "z_score",
        0
    )

    if abs(z_score) < 1.0:

        return None

    if z_score < 0:

        return {
            "issue":
                "low_peak_level",

            "severity":
                "moderate",

            "confidence":
                "high",

            "evidence": [
                "Estimated true peak is below the reference profile."
            ],

            "diagnosis":
                "The target mix reaches a substantially "
                "lower peak level than the reference tracks.",

            "interpretation":
                "This is consistent with the overall level "
                "reduction and should not be interpreted as "
                "evidence of insufficient compression by itself."
        }

    return {
        "issue":
            "elevated_peak_level",

        "severity":
            "moderate",

        "confidence":
            "high",

        "evidence": [
            "Estimated true peak is above the reference profile."
        ],

        "diagnosis":
            "The target mix reaches a higher peak level "
            "than the reference tracks.",

        "interpretation":
            "Peak level should be evaluated alongside "
            "delivery requirements and dynamics measurements."
    }


# ---------------------------------------------------------
# Run diagnostics
# ---------------------------------------------------------

def run_diagnostics(
    report
):
    """
    Run all loudness engineering diagnosis rules.
    """

    parameters = report[
        "parameters"
    ]

    diagnoses = []

    diagnosis = (
        diagnose_overall_level_reduction(
            parameters
        )
    )

    if diagnosis:
        diagnoses.append(
            diagnosis
        )

    diagnosis = (
        diagnose_loudness_range(
            parameters
        )
    )

    if diagnosis:
        diagnoses.append(
            diagnosis
        )

    diagnosis = (
        diagnose_peak_level(
            parameters
        )
    )

    if diagnosis:
        diagnoses.append(
            diagnosis
        )

    return diagnoses


# ---------------------------------------------------------
# Save diagnosis
# ---------------------------------------------------------

def save_diagnosis(
    report,
    diagnoses
):
    """
    Save loudness engineering diagnosis.
    """

    output = {
        "file":
            report["file"],

        "reference_count":
            report["reference_count"],

        "measurement_type":
            report["measurement_type"],

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


# ---------------------------------------------------------
# Print diagnosis
# ---------------------------------------------------------

def print_diagnosis(
    report,
    diagnoses
):
    """
    Display loudness engineering diagnosis.
    """

    print()
    print("========================================")
    print("LOUDNESS ENGINEERING DIAGNOSIS")
    print("========================================")
    print()

    print(
        f"Target mix: "
        f"{report['file']}"
    )

    print()

    if not diagnoses:

        print(
            "No loudness diagnostic patterns detected."
        )

        print()

        return

    for index, diagnosis in enumerate(
        diagnoses,
        start=1
    ):

        print(
            f"DIAGNOSIS {index}"
        )

        print(
            f"Issue: "
            f"{diagnosis['issue']}"
        )

        print(
            f"Severity: "
            f"{diagnosis['severity']}"
        )

        print(
            f"Confidence: "
            f"{diagnosis['confidence']}"
        )

        print()

        print("Evidence:")

        for evidence in (
            diagnosis["evidence"]
        ):

            print(
                f"  - {evidence}"
            )

        print()

        print("Diagnosis:")

        print(
            f"  {diagnosis['diagnosis']}"
        )

        print()

        print("Interpretation:")

        print(
            f"  {diagnosis['interpretation']}"
        )

        print()
        print("----------------------------------------")
        print()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    report = load_report()

    diagnoses = run_diagnostics(
        report
    )

    save_diagnosis(
        report,
        diagnoses
    )

    print_diagnosis(
        report,
        diagnoses
    )

    print(
        "Loudness engineering diagnosis saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()


if __name__ == "__main__":
    main()