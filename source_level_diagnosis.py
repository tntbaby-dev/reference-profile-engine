import json
import os


DEVIATION_FILE = "output/deviation_report.json"
DIAGNOSIS_FILE = "output/engineering_diagnosis.json"
PRIORITIZED_FILE = "output/prioritized_diagnosis.json"
CONTRIBUTION_FILE = "output/stem_contribution_ranking.json"

OUTPUT_FILE = "output/source_level_diagnosis.json"


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
# Contributor classification
# ---------------------------------------------------------

def classify_contributor(contribution_percent):
    """
    Classify the strength of a stem's contribution
    to a frequency band.

    These classifications describe contribution
    strength, not causality.
    """

    if contribution_percent >= 50.0:
        return "major_contributor"

    if contribution_percent >= 20.0:
        return "significant_contributor"

    if contribution_percent >= 5.0:
        return "minor_contributor"

    return "weak_contributor"


# ---------------------------------------------------------
# Determine source evidence type
# ---------------------------------------------------------

def determine_evidence_type(
    deviation_direction,
    contribution_percent
):
    """
    Determine how source contribution should be
    interpreted based on the direction of the
    mix-level deviation.

    Above-reference:
        A strong contributor can support an
        excess-energy diagnosis.

    Below-reference:
        A strong contributor does NOT establish
        causality. It only identifies a source
        currently supplying energy to the region.
    """

    if contribution_percent < 5.0:
        return "weak_source_evidence"

    if deviation_direction == "above_reference":

        return "supports_excess_energy_diagnosis"

    if deviation_direction == "below_reference":

        return "available_energy_source"

    return "neutral_source_evidence"


# ---------------------------------------------------------
# Determine whether contribution supports diagnosis
# ---------------------------------------------------------

def contribution_supports_diagnosis(
    deviation,
    contribution_percent
):
    """
    Determine whether source contribution provides
    useful evidence for the diagnosed deviation.

    Direction matters:

    ABOVE reference:
        Strong contribution is useful evidence
        for investigating excess energy.

    BELOW reference:
        Contribution is recorded as source context,
        but is NOT treated as evidence that the
        source caused the deficiency.
    """

    classification = deviation.get(
        "classification",
        "unknown"
    )

    direction = deviation.get(
        "direction",
        "balanced"
    )

    if classification == "within_reference":
        return False

    if contribution_percent < 5.0:
        return False

    if direction in {
        "above_reference",
        "below_reference"
    }:
        return True

    return False


# ---------------------------------------------------------
# Analyze one diagnosis
# ---------------------------------------------------------

def analyze_diagnosis(
    diagnosis,
    deviations,
    band_contributions
):
    """
    Connect a mix-level diagnosis with source-level
    evidence while respecting deviation direction.
    """

    issue = diagnosis["issue"]

    # -----------------------------------------------------
    # Determine relevant frequency bands
    # -----------------------------------------------------

    if issue == "low_frequency_distribution_imbalance":

        relevant_bands = [
            "sub",
            "bass",
            "low_mid"
        ]

    elif issue == "lower_mid_spectral_concentration":

        relevant_bands = [
            "low_mid",
            "mid"
        ]

    elif issue == "reduced_high_frequency_energy":

        relevant_bands = [
            "presence",
            "brilliance"
        ]

    else:

        relevant_bands = []

    evidence = []

    # -----------------------------------------------------
    # Analyze source contributions
    # -----------------------------------------------------

    for band in relevant_bands:

        if band not in band_contributions:
            continue

        deviation = deviations.get(
            band,
            {}
        )

        if not deviation:
            continue

        direction = deviation.get(
            "direction",
            "balanced"
        )

        for contribution in (
            band_contributions[band]
        ):

            contribution_percent = float(
                contribution[
                    "contribution_percent"
                ]
            )

            if not contribution_supports_diagnosis(
                deviation,
                contribution_percent
            ):
                continue

            evidence_type = (
                determine_evidence_type(
                    direction,
                    contribution_percent
                )
            )

            evidence.append(
                {
                    "band": band,
                    "stem": contribution["file"],
                    "contribution_percent":
                        contribution_percent,
                    "contributor_classification":
                        classify_contributor(
                            contribution_percent
                        ),
                    "deviation_direction":
                        direction,
                    "deviation_classification":
                        deviation[
                            "classification"
                        ],
                    "deviation_z_score":
                        float(
                            deviation["z_score"]
                        ),
                    "evidence_type":
                        evidence_type
                }
            )

    return evidence


# ---------------------------------------------------------
# Rank source evidence
# ---------------------------------------------------------

def rank_source_evidence(evidence):
    """
    Rank source evidence according to its relationship
    with the direction of the mix-level deviation.

    Above-reference:
        Contribution receives a positive diagnostic
        weighting because it may support investigation
        of excess energy.

    Below-reference:
        Contribution is retained as contextual evidence,
        but receives a lower diagnostic weighting because
        contribution alone does not explain a deficiency.
    """

    stem_scores = {}

    for item in evidence:

        stem = item["stem"]

        contribution = (
            item["contribution_percent"]
        )

        deviation_weight = abs(
            item["deviation_z_score"]
        )

        direction = item[
            "deviation_direction"
        ]

        # -------------------------------------------------
        # Direction-aware weighting
        # -------------------------------------------------

        if direction == "above_reference":

            score = (
                contribution
                * deviation_weight
            )

        elif direction == "below_reference":

            # Below-reference energy cannot be treated
            # as evidence that the source caused the
            # deficiency.
            #
            # Retain the source for context, but reduce
            # its diagnostic weight substantially.
            score = (
                contribution
                * deviation_weight
                * 0.25
            )

        else:

            score = 0.0

        if stem not in stem_scores:

            stem_scores[stem] = {
                "stem": stem,
                "weighted_score": 0.0,
                "bands": []
            }

        stem_scores[stem][
            "weighted_score"
        ] += score

        stem_scores[stem]["bands"].append(
            {
                "band": item["band"],
                "contribution_percent":
                    contribution,
                "z_score":
                    item["deviation_z_score"],
                "deviation_direction":
                    direction,
                "evidence_type":
                    item["evidence_type"]
            }
        )

    ranked = list(
        stem_scores.values()
    )

    ranked.sort(
        key=lambda item:
            item["weighted_score"],
        reverse=True
    )

    for index, item in enumerate(
        ranked,
        start=1
    ):

        item["rank"] = index

    return ranked


# ---------------------------------------------------------
# Build source-level diagnosis
# ---------------------------------------------------------

def build_source_level_diagnosis(
    diagnosis,
    deviations,
    band_contributions
):
    """
    Build source-level evidence for one
    engineering diagnosis.
    """

    evidence = analyze_diagnosis(
        diagnosis,
        deviations,
        band_contributions
    )

    ranked_sources = rank_source_evidence(
        evidence
    )

    return {
        "issue": diagnosis["issue"],
        "severity": diagnosis["severity"],
        "confidence": diagnosis["confidence"],
        "diagnosis": diagnosis["diagnosis"],
        "source_evidence": evidence,
        "ranked_sources": ranked_sources
    }


# ---------------------------------------------------------
# Build all source-level diagnoses
# ---------------------------------------------------------

def build_all_source_diagnoses(
    prioritized_report,
    deviation_report,
    contribution_report
):
    """
    Build source-level diagnoses for every
    prioritized diagnosis group.
    """

    deviations = deviation_report[
        "bands"
    ]

    band_contributions = (
        contribution_report[
            "band_contributions"
        ]
    )

    results = []

    for group in (
        prioritized_report[
            "prioritized_groups"
        ]
    ):

        primary = group[
            "primary_diagnosis"
        ]

        diagnosis = (
            build_source_level_diagnosis(
                primary,
                deviations,
                band_contributions
            )
        )

        diagnosis["priority"] = (
            group["priority"]
        )

        diagnosis[
            "supporting_diagnoses"
        ] = group[
            "supporting_diagnoses"
        ]

        results.append(
            diagnosis
        )

    return results


# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

def save_report(
    prioritized_report,
    contribution_report,
    source_diagnoses
):
    """
    Save direction-aware source-level diagnosis.
    """

    output = {
        "file": prioritized_report["file"],
        "reference_count": (
            prioritized_report[
                "reference_count"
            ]
        ),
        "measurement_type": (
            "source_level_spectral_contribution"
        ),
        "source_count": len(
            contribution_report.get(
                "overall_stem_ranking",
                []
            )
        ),
        "reasoning_model": (
            "direction_aware_source_evidence"
        ),
        "note": (
            "Source evidence distinguishes between "
            "sources supporting excess-energy diagnoses "
            "and sources merely providing available "
            "energy within deficient frequency regions. "
            "Contribution does not establish causality."
        ),
        "diagnoses": source_diagnoses
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
# Print report
# ---------------------------------------------------------

def print_report(
    source_diagnoses
):
    """
    Display direction-aware source-level diagnoses.
    """

    print()
    print("========================================")
    print("DIRECTION-AWARE SOURCE DIAGNOSIS")
    print("========================================")
    print()

    if not source_diagnoses:

        print(
            "No source-level diagnoses generated."
        )

        print()

        return

    for index, diagnosis in enumerate(
        source_diagnoses,
        start=1
    ):

        print(
            f"DIAGNOSIS {index}"
        )

        print(
            f"Priority: "
            f"{diagnosis['priority']}"
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

        print(
            "Source evidence:"
        )

        ranked_sources = (
            diagnosis[
                "ranked_sources"
            ]
        )

        if not ranked_sources:

            print(
                "  No meaningful source "
                "evidence identified."
            )

        else:

            for source in ranked_sources:

                print(
                    f"  {source['rank']}. "
                    f"{source['stem']}"
                    f" | Score: "
                    f"{source['weighted_score']:.2f}"
                )

                for band in (
                    source["bands"]
                ):

                    print(
                        f"      "
                        f"{band['band']}: "
                        f"{band['contribution_percent']:.2f}% "
                        f"| "
                        f"{band['deviation_direction']}"
                        f" | "
                        f"{band['evidence_type']}"
                    )

        print()
        print("----------------------------------------")
        print()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    deviation_report = load_json(
        DEVIATION_FILE
    )

    diagnosis_report = load_json(
        DIAGNOSIS_FILE
    )

    prioritized_report = load_json(
        PRIORITIZED_FILE
    )

    contribution_report = load_json(
        CONTRIBUTION_FILE
    )

    source_diagnoses = (
        build_all_source_diagnoses(
            prioritized_report,
            deviation_report,
            contribution_report
        )
    )

    save_report(
        prioritized_report,
        contribution_report,
        source_diagnoses
    )

    print_report(
        source_diagnoses
    )

    print(
        "Direction-aware source diagnosis saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()


if __name__ == "__main__":
    main()