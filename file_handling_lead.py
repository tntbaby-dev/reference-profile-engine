import json
import os


CROSS_DOMAIN_FILE = (
    "output/cross_domain_reasoning.json"
)

RECOMMENDATION_FILE = (
    "output/engineering_recommendations.json"
)

SOURCE_DIAGNOSIS_FILE = (
    "output/source_level_diagnosis.json"
)

SOURCE_RANKING_FILE = (
    "output/stem_contribution_ranking.json"
)

OUTPUT_FILE = (
    "output/file_handling_lead.json"
)


def load_json(file_path):

    if not os.path.exists(
        file_path
    ):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def build_engineering_summary(
    cross_domain
):

    primary = (
        cross_domain[
            "priority_groups"
        ][
            "primary"
        ]
    )

    supporting = (
        cross_domain[
            "priority_groups"
        ][
            "supporting"
        ]
    )

    secondary = (
        cross_domain[
            "priority_groups"
        ][
            "secondary"
        ]
    )

    independent = (
        cross_domain[
            "priority_groups"
        ][
            "independent"
        ]
    )

    return {
        "primary_findings":
            primary,

        "supporting_findings":
            supporting,

        "secondary_findings":
            secondary,

        "independent_findings":
            independent
    }


def build_production_recommendations(
    cross_domain
):

    recommendations = []

    primary = (
        cross_domain[
            "priority_groups"
        ][
            "primary"
        ]
    )

    supporting = (
        cross_domain[
            "priority_groups"
        ][
            "supporting"
        ]
    )

    secondary = (
        cross_domain[
            "priority_groups"
        ][
            "secondary"
        ]
    )

    independent = (
        cross_domain[
            "priority_groups"
        ][
            "independent"
        ]
    )

    primary_findings = {
        item["finding"]
        for item in primary
    }

    supporting_findings = {
        item["finding"]
        for item in supporting
    }

    secondary_findings = {
        item["finding"]
        for item in secondary
    }

    independent_findings = {
        item["finding"]
        for item in independent
    }

    # --------------------------------------------------
    # PRIMARY: OVERALL LEVEL
    # --------------------------------------------------

    if (
        "overall_level_reduction"
        in primary_findings
    ):

        recommendations.append({

            "priority":
                "high",

            "area":
                "overall_level",

            "action":
                "Verify gain staging and overall mix level before making dynamics or tonal corrections.",

            "reason":
                "The mix is substantially below the reference loudness profile across multiple level measurements.",

            "do_not_assume":
                "Do not interpret the low level alone as evidence that more compression is required."
        })

    # --------------------------------------------------
    # PRIMARY: DYNAMICS
    # --------------------------------------------------

    if (
        "elevated_crest_with_reduced_rms_variation"
        in primary_findings
    ):

        recommendations.append({

            "priority":
                "high",

            "area":
                "dynamics",

            "action":
                "Investigate the relationship between transient energy and sustained energy before applying additional compression.",

            "reason":
                "Peak-to-RMS separation is unusually large while short-term RMS variation is restrained.",

            "do_not_assume":
                "Do not automatically increase compression. The measured pattern does not establish that compression is the cause."
        })

    # --------------------------------------------------
    # SUPPORTING: LOW-MID + DYNAMICS
    # --------------------------------------------------

    if (
        "low_mid_concentration_with_peak_sustained_imbalance"
        in supporting_findings
    ):

        recommendations.append({

            "priority":
                "high",

            "area":
                "low_mid_and_dynamics",

            "action":
                "Investigate whether sustained lower-mid energy is contributing to the observed peak-to-RMS imbalance.",

            "reason":
                "Lower-mid concentration and unusual peak-versus-sustained energy separation occur together.",

            "do_not_assume":
                "Do not remove lower-mid energy simply because it is above the reference. Confirm the responsible sources first."
        })

    # --------------------------------------------------
    # SECONDARY: HIGH FREQUENCY
    # --------------------------------------------------

    if (
        "reduced_high_frequency_energy"
        in secondary_findings
    ):

        recommendations.append({

            "priority":
                "medium",

            "area":
                "high_frequency",

            "action":
                "Investigate high-frequency source availability, processing, masking, and arrangement.",

            "reason":
                "Presence and brilliance energy are below the reference profile.",

            "do_not_assume":
                "Do not automatically boost high frequencies with EQ."
        })

    # --------------------------------------------------
    # SECONDARY: SPECTRAL + LOUDNESS
    # --------------------------------------------------

    if (
        "spectral_imbalance_with_level_reduction"
        in secondary_findings
    ):

        recommendations.append({

            "priority":
                "medium",

            "area":
                "spectral_balance",

            "action":
                "Evaluate spectral balance independently from overall gain.",

            "reason":
                "The mix remains strongly concentrated in the lower-mid region despite operating at a substantially lower overall level.",

            "do_not_assume":
                "Do not use a global gain change as a substitute for correcting spectral distribution."
        })

    # --------------------------------------------------
    # INDEPENDENT: STEREO BALANCE
    # --------------------------------------------------

    if (
        "left_right_balance_deviation"
        in independent_findings
    ):

        recommendations.append({

            "priority":
                "medium",

            "area":
                "stereo_balance",

            "action":
                "Investigate left/right channel balance and asymmetric source placement or processing.",

            "reason":
                "The stereo image shows measurable L/R imbalance.",

            "do_not_assume":
                "Do not widen or narrow the stereo image to solve a channel-balance problem."
        })

    # --------------------------------------------------
    # NEGATIVE EVIDENCE
    # --------------------------------------------------

    if (
        "stereo_integrity_within_reference"
        in independent_findings
    ):

        recommendations.append({

            "priority":
                "information",

            "area":
                "stereo_integrity",

            "action":
                "Preserve current phase, Mid/Side and mono-compatibility relationships unless other evidence appears.",

            "reason":
                "These stereo relationships remain within the reference profile.",

            "do_not_assume":
                "Do not make stereo-width or phase corrections without evidence."
        })

    return recommendations


def build_lead_decision(
    recommendations
):

    high_priority = [
        item
        for item in recommendations
        if item["priority"] == "high"
    ]

    medium_priority = [
        item
        for item in recommendations
        if item["priority"] == "medium"
    ]

    information = [
        item
        for item in recommendations
        if item["priority"] == "information"
    ]

    if high_priority:

        overall_priority = "high"

    elif medium_priority:

        overall_priority = "medium"

    else:

        overall_priority = "low"

    return {

        "overall_priority":
            overall_priority,

        "high_priority_count":
            len(high_priority),

        "medium_priority_count":
            len(medium_priority),

        "information_count":
            len(information),

        "lead_instruction":
            "Address the highest-priority engineering findings first. Treat secondary findings as supporting investigation areas and preserve domains that show no meaningful deviation."
    }


def save_output(
    cross_domain,
    recommendations,
    decision
):

    output = {

        "file":
            cross_domain["file"],

        "measurement_type":
            "file_handling_lead",

        "engineering_summary":
            build_engineering_summary(
                cross_domain
            ),

        "production_recommendations":
            recommendations,

        "lead_decision":
            decision
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
    cross_domain,
    recommendations,
    decision
):

    print()
    print(
        "========================================"
    )
    print(
        "FILE HANDLING LEAD"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"Target mix: "
        f"{cross_domain['file']}"
    )

    print()

    print(
        f"Overall priority: "
        f"{decision['overall_priority']}"
    )

    print()

    print(
        "PRODUCTION TEAM RECOMMENDATIONS"
    )

    print(
        "----------------------------------------"
    )

    for item in recommendations:

        print(
            f"[{item['priority'].upper()}] "
            f"{item['area']}"
        )

        print(
            f"Action: "
            f"{item['action']}"
        )

        print(
            f"Reason: "
            f"{item['reason']}"
        )

        print(
            f"Do not assume: "
            f"{item['do_not_assume']}"
        )

        print()

    print(
        "========================================"
    )

    print(
        "File Handling Lead output saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "========================================"
    )

    print()


def main():

    cross_domain = load_json(
        CROSS_DOMAIN_FILE
    )

    # These are loaded now so the Lead architecture
    # is ready to incorporate source-level evidence.
    #
    # They are intentionally not used to create
    # unsupported causal conclusions yet.

    if os.path.exists(
        RECOMMENDATION_FILE
    ):

        load_json(
            RECOMMENDATION_FILE
        )

    if os.path.exists(
        SOURCE_DIAGNOSIS_FILE
    ):

        load_json(
            SOURCE_DIAGNOSIS_FILE
        )

    if os.path.exists(
        SOURCE_RANKING_FILE
    ):

        load_json(
            SOURCE_RANKING_FILE
        )

    recommendations = (
        build_production_recommendations(
            cross_domain
        )
    )

    decision = (
        build_lead_decision(
            recommendations
        )
    )

    save_output(
        cross_domain,
        recommendations,
        decision
    )

    print_report(
        cross_domain,
        recommendations,
        decision
    )


if __name__ == "__main__":
    main()
