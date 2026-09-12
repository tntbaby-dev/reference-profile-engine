import json
import os


INPUT_FILE = "output/source_level_diagnosis.json"
OUTPUT_FILE = "output/engineering_recommendations.json"


# ---------------------------------------------------------
# Load source-level diagnosis
# ---------------------------------------------------------

def load_source_level_diagnosis():
    """
    Load direction-aware source-level diagnosis.
    """

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"Source-level diagnosis not found: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ---------------------------------------------------------
# Source helpers
# ---------------------------------------------------------

def get_top_sources(diagnosis):
    """
    Return ranked source evidence.
    """

    return diagnosis.get(
        "ranked_sources",
        []
    )


def get_source_evidence_types(diagnosis):
    """
    Return all evidence types found in the diagnosis.
    """

    evidence_types = set()

    for source in get_top_sources(diagnosis):

        for band in source.get(
            "bands",
            []
        ):

            evidence_types.add(
                band.get(
                    "evidence_type",
                    "unknown"
                )
            )

    return evidence_types


def get_excess_sources(diagnosis):
    """
    Return sources that provide evidence supporting
    an above-reference excess-energy diagnosis.
    """

    sources = []

    for source in get_top_sources(
        diagnosis
    ):

        excess_bands = []

        for band in source.get(
            "bands",
            []
        ):

            if band.get(
                "evidence_type"
            ) == "supports_excess_energy_diagnosis":

                excess_bands.append(
                    band
                )

        if excess_bands:

            sources.append(
                {
                    "stem": source["stem"],
                    "weighted_score":
                        source["weighted_score"],
                    "bands": excess_bands
                }
            )

    return sources


def get_available_energy_sources(diagnosis):
    """
    Return sources that currently provide energy
    inside a below-reference frequency region.

    These sources are contextual evidence only.
    They are NOT treated as causes of the deficiency.
    """

    sources = []

    for source in get_top_sources(
        diagnosis
    ):

        available_bands = []

        for band in source.get(
            "bands",
            []
        ):

            if band.get(
                "evidence_type"
            ) == "available_energy_source":

                available_bands.append(
                    band
                )

        if available_bands:

            sources.append(
                {
                    "stem": source["stem"],
                    "weighted_score":
                        source["weighted_score"],
                    "bands": available_bands
                }
            )

    return sources


# ---------------------------------------------------------
# Low-frequency recommendation
# ---------------------------------------------------------

def recommend_low_frequency_distribution(
    diagnosis
):
    """
    Generate a direction-aware recommendation
    for low-frequency distribution imbalance.
    """

    excess_sources = get_excess_sources(
        diagnosis
    )

    available_sources = (
        get_available_energy_sources(
            diagnosis
        )
    )

    evidence = []

    # -----------------------------------------------------
    # Above-reference sources
    # -----------------------------------------------------

    for source in excess_sources:

        evidence.append(
            {
                "stem": source["stem"],
                "weighted_score":
                    float(
                        source["weighted_score"]
                    ),
                "role":
                    "supports_excess_energy_investigation",
                "bands": [
                    {
                        "band": band["band"],
                        "contribution_percent":
                            float(
                                band[
                                    "contribution_percent"
                                ]
                            )
                    }
                    for band in source["bands"]
                ]
            }
        )

    # -----------------------------------------------------
    # Below-reference sources
    # -----------------------------------------------------

    available_energy = []

    for source in available_sources:

        available_energy.append(
            {
                "stem": source["stem"],
                "weighted_score":
                    float(
                        source["weighted_score"]
                    ),
                "role":
                    "available_energy_source",
                "bands": [
                    {
                        "band": band["band"],
                        "contribution_percent":
                            float(
                                band[
                                    "contribution_percent"
                                ]
                            )
                    }
                    for band in source["bands"]
                ]
            }
        )

    # -----------------------------------------------------
    # Build recommendation
    # -----------------------------------------------------

    if excess_sources:

        primary_source = excess_sources[0]

        recommendation = (
            f"Prioritize investigation of "
            f"{primary_source['stem']} for the "
            f"above-reference low-mid energy, because "
            f"its measured contribution supports the "
            f"excess-energy diagnosis. Also evaluate "
            f"other contributing sources for cumulative "
            f"energy buildup. The below-reference sub "
            f"and bass regions should be treated "
            f"separately; their available source "
            f"contributions do not establish causality."
        )

        action = (
            "investigate_low_mid_excess"
        )

    else:

        recommendation = (
            "Investigate the low-frequency distribution "
            "without assigning causality to individual "
            "sources. The measured sub and bass "
            "deficiencies should be evaluated alongside "
            "the elevated low-mid region, with attention "
            "to arrangement, masking, source balance, "
            "and processing."
        )

        action = (
            "investigate_low_frequency_distribution"
        )

    processing_guidance = [
        (
            "Inspect sources supporting the "
            "above-reference region first."
        ),
        (
            "Determine whether the elevated energy "
            "is intentional or an unintended buildup."
        ),
        (
            "Check cumulative overlap between sources "
            "occupying the same frequency region."
        ),
        (
            "Treat below-reference regions as a "
            "separate investigation rather than "
            "assuming the strongest contributor "
            "caused the deficiency."
        ),
        (
            "Apply corrective processing only after "
            "the source interaction or processing "
            "problem has been identified."
        )
    ]

    return {
        "action": action,
        "recommendation": recommendation,
        "source_evidence": evidence,
        "available_energy_sources":
            available_energy,
        "processing_guidance":
            processing_guidance
    }


# ---------------------------------------------------------
# High-frequency recommendation
# ---------------------------------------------------------

def recommend_reduced_high_frequency(
    diagnosis
):
    """
    Generate a direction-aware recommendation
    for below-reference high-frequency energy.
    """

    available_sources = (
        get_available_energy_sources(
            diagnosis
        )
    )

    source_context = []

    for source in available_sources:

        source_context.append(
            {
                "stem": source["stem"],
                "weighted_score":
                    float(
                        source["weighted_score"]
                    ),
                "role":
                    "available_energy_source",
                "bands": [
                    {
                        "band": band["band"],
                        "contribution_percent":
                            float(
                                band[
                                    "contribution_percent"
                                ]
                            )
                    }
                    for band in source["bands"]
                ]
            }
        )

    recommendation = (
        "The affected high-frequency regions are "
        "below the reference profile, so existing "
        "source contribution does not establish a "
        "specific stem as the cause of the deficiency. "
        "Investigate whether useful high-frequency "
        "content is being reduced by source balance, "
        "processing, arrangement, masking, or the "
        "absence of an appropriate source."
    )

    processing_guidance = [
        (
            "Inspect processing that may have reduced "
            "presence or brilliance energy."
        ),
        (
            "Check whether important sources are "
            "overly attenuated in the affected regions."
        ),
        (
            "Evaluate masking from competing sources "
            "before applying additional high-frequency "
            "boosting."
        ),
        (
            "Determine whether the arrangement contains "
            "an appropriate source capable of supplying "
            "the missing energy."
        ),
        (
            "Apply corrective processing only after "
            "the cause of the deficiency has been "
            "identified."
        )
    ]

    return {
        "action":
            "investigate_high_frequency_deficiency",
        "recommendation":
            recommendation,
        "source_evidence":
            source_context,
        "processing_guidance":
            processing_guidance
    }


# ---------------------------------------------------------
# Generic recommendation
# ---------------------------------------------------------

def recommend_generic(
    diagnosis
):
    """
    Generate a conservative recommendation for
    diagnoses without a specialized rule.
    """

    sources = get_top_sources(
        diagnosis
    )

    source_evidence = []

    for source in sources:

        source_evidence.append(
            {
                "stem": source["stem"],
                "weighted_score":
                    float(
                        source["weighted_score"]
                    )
            }
        )

    recommendation = (
        "Investigate the measured source evidence "
        "before applying corrective processing. "
        "Determine whether the deviation results "
        "from source balance, arrangement, processing, "
        "or interaction between sources."
    )

    processing_guidance = [
        (
            "Verify the measurement and deviation."
        ),
        (
            "Inspect the strongest relevant source "
            "evidence."
        ),
        (
            "Evaluate source interaction and masking."
        ),
        (
            "Apply corrective processing only after "
            "the engineering cause is established."
        )
    ]

    return {
        "action":
            "investigate_engineering_cause",
        "recommendation":
            recommendation,
        "source_evidence":
            source_evidence,
        "processing_guidance":
            processing_guidance
    }


# ---------------------------------------------------------
# Generate recommendation
# ---------------------------------------------------------

def generate_recommendation(
    diagnosis
):
    """
    Select the appropriate recommendation logic.
    """

    issue = diagnosis["issue"]

    if issue == (
        "low_frequency_distribution_imbalance"
    ):

        return (
            recommend_low_frequency_distribution(
                diagnosis
            )
        )

    if issue == (
        "reduced_high_frequency_energy"
    ):

        return (
            recommend_reduced_high_frequency(
                diagnosis
            )
        )

    return recommend_generic(
        diagnosis
    )


# ---------------------------------------------------------
# Build recommendations
# ---------------------------------------------------------

def build_recommendations(
    source_level_report
):
    """
    Generate engineering recommendations for
    all source-level diagnoses.
    """

    recommendations = []

    for diagnosis in (
        source_level_report[
            "diagnoses"
        ]
    ):

        result = generate_recommendation(
            diagnosis
        )

        recommendations.append(
            {
                "issue":
                    diagnosis["issue"],
                "priority":
                    diagnosis["priority"],
                "severity":
                    diagnosis["severity"],
                "confidence":
                    diagnosis["confidence"],
                "action":
                    result["action"],
                "recommendation":
                    result["recommendation"],
                "source_evidence":
                    result["source_evidence"],
                "available_energy_sources":
                    result.get(
                        "available_energy_sources",
                        []
                    ),
                "processing_guidance":
                    result["processing_guidance"]
            }
        )

    return recommendations


# ---------------------------------------------------------
# Save recommendations
# ---------------------------------------------------------

def save_recommendations(
    source_level_report,
    recommendations
):
    """
    Save engineering recommendations.
    """

    output = {
        "file":
            source_level_report["file"],
        "reference_count":
            source_level_report[
                "reference_count"
            ],
        "reasoning_model":
            "direction_aware_source_recommendation",
        "recommendations":
            recommendations
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
# Print recommendations
# ---------------------------------------------------------

def print_recommendations(
    source_level_report,
    recommendations
):
    """
    Display engineering recommendations.
    """

    print()
    print("========================================")
    print(
        "DIRECTION-AWARE ENGINEERING "
        "RECOMMENDATIONS"
    )
    print("========================================")
    print()

    print(
        f"Target mix: "
        f"{source_level_report['file']}"
    )

    print()

    if not recommendations:

        print(
            "No engineering recommendations generated."
        )

        print()

        return

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"RECOMMENDATION {index}"
        )

        print(
            f"Action: "
            f"{recommendation['action']}"
        )

        print(
            f"Priority: "
            f"{recommendation['priority']}"
        )

        print(
            f"Severity: "
            f"{recommendation['severity']}"
        )

        print(
            f"Confidence: "
            f"{recommendation['confidence']}"
        )

        print()

        print(
            "Recommendation:"
        )

        print(
            f"  "
            f"{recommendation['recommendation']}"
        )

        print()

        if recommendation[
            "source_evidence"
        ]:

            print(
                "Supporting source evidence:"
            )

            for source in (
                recommendation[
                    "source_evidence"
                ]
            ):

                print(
                    f"  - "
                    f"{source['stem']}"
                    f" | Score: "
                    f"{source['weighted_score']:.2f}"
                )

                for band in source[
                    "bands"
                ]:

                    print(
                        f"      "
                        f"{band['band']}: "
                        f"{band['contribution_percent']:.2f}%"
                    )

            print()

        if recommendation[
            "available_energy_sources"
        ]:

            print(
                "Available energy sources:"
            )

            for source in (
                recommendation[
                    "available_energy_sources"
                ]
            ):

                print(
                    f"  - "
                    f"{source['stem']}"
                    f" | Context only"
                )

                for band in source[
                    "bands"
                ]:

                    print(
                        f"      "
                        f"{band['band']}: "
                        f"{band['contribution_percent']:.2f}%"
                    )

            print()

        print(
            "Processing guidance:"
        )

        for guidance in (
            recommendation[
                "processing_guidance"
            ]
        ):

            print(
                f"  - {guidance}"
            )

        print()
        print("----------------------------------------")
        print()

    print(
        "========================================"
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    source_level_report = (
        load_source_level_diagnosis()
    )

    recommendations = (
        build_recommendations(
            source_level_report
        )
    )

    save_recommendations(
        source_level_report,
        recommendations
    )

    print_recommendations(
        source_level_report,
        recommendations
    )

    print()

    print(
        "Direction-aware engineering "
        "recommendations saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()


if __name__ == "__main__":
    main()