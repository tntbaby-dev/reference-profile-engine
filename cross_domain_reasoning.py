import json
import os


SPECTRAL_DIAGNOSIS_FILE = (
    "output/engineering_diagnosis.json"
)

LOUDNESS_DIAGNOSIS_FILE = (
    "output/loudness_engineering_diagnosis.json"
)

DYNAMICS_DIAGNOSIS_FILE = (
    "output/dynamics_engineering_diagnosis.json"
)

STEREO_DIAGNOSIS_FILE = (
    "output/stereo_engineering_diagnosis.json"
)

OUTPUT_FILE = (
    "output/cross_domain_reasoning.json"
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


def normalize_text(text):

    return text.lower().strip()


def get_diagnosis_texts(
    diagnosis_data
):

    return [
        normalize_text(
            diagnosis["diagnosis"]
        )
        for diagnosis
        in diagnosis_data["diagnoses"]
    ]


def contains_diagnosis(
    diagnosis_texts,
    *patterns
):

    for text in diagnosis_texts:

        if all(
            pattern in text
            for pattern in patterns
        ):

            return True

    return False


def build_cross_domain_evidence(
    spectral,
    loudness,
    dynamics,
    stereo
):

    spectral_texts = (
        get_diagnosis_texts(
            spectral
        )
    )

    loudness_texts = (
        get_diagnosis_texts(
            loudness
        )
    )

    dynamics_texts = (
        get_diagnosis_texts(
            dynamics
        )
    )

    stereo_texts = (
        get_diagnosis_texts(
            stereo
        )
    )

    evidence = []

    # --------------------------------------------------
    # SPECTRAL FINDINGS
    # --------------------------------------------------

    lower_mid_concentration = (
        contains_diagnosis(
            spectral_texts,
            "lower",
            "mid",
            "concentrated"
        )
        or
        contains_diagnosis(
            spectral_texts,
            "low-mid",
            "concentrated"
        )
    )

    reduced_high_frequency = (
        contains_diagnosis(
            spectral_texts,
            "presence",
            "brilliance",
            "reduced"
        )
        or
        contains_diagnosis(
            spectral_texts,
            "high-frequency",
            "reduced"
        )
    )

    # --------------------------------------------------
    # LOUDNESS FINDINGS
    # --------------------------------------------------

    overall_level_reduction = (
        contains_diagnosis(
            loudness_texts,
            "substantially",
            "lower",
            "overall",
            "level"
        )
        or
        contains_diagnosis(
            loudness_texts,
            "lower",
            "overall",
            "level"
        )
    )

    # --------------------------------------------------
    # DYNAMICS FINDINGS
    # --------------------------------------------------

    elevated_crest = (
        "elevated_peak_to_rms_ratio"
        in dynamics_texts
    )

    peak_sustained_imbalance = (
        "peak_sustained_energy_imbalance"
        in dynamics_texts
    )

    reduced_rms_variation = (
        "reduced_short_term_rms_variation"
        in dynamics_texts
    )

    # --------------------------------------------------
    # STEREO FINDINGS
    # --------------------------------------------------

    left_right_balance = (
        "left_right_balance_deviation"
        in stereo_texts
    )

    phase_normal = (
        "phase_relationship_within_reference"
        in stereo_texts
    )

    mid_side_normal = (
        "mid_side_relationship_within_reference"
        in stereo_texts
    )

    mono_normal = (
        "mono_compatibility_within_reference"
        in stereo_texts
    )

    # --------------------------------------------------
    # EVIDENCE GROUP 1
    # Overall level state
    # --------------------------------------------------

    if overall_level_reduction:

        evidence.append({

            "domain":
                "loudness",

            "finding":
                "overall_level_reduction",

            "role":
                "primary_level_state",

            "interpretation":
                "The mix is operating at a substantially lower overall level than the reference profile."
        })

    # --------------------------------------------------
    # EVIDENCE GROUP 2
    # Loudness + dynamics
    # --------------------------------------------------

    if (
        overall_level_reduction
        and
        elevated_crest
    ):

        evidence.append({

            "domain":
                "loudness_dynamics",

            "finding":
                "level_reduction_with_elevated_crest_factor",

            "role":
                "reinforcing_evidence",

            "interpretation":
                "The overall level is substantially reduced while peak-to-RMS separation remains unusually large. The level difference should therefore not automatically be interpreted as excessive compression."
        })

    # --------------------------------------------------
    # EVIDENCE GROUP 3
    # Dynamics internal relationship
    # --------------------------------------------------

    if (
        elevated_crest
        and
        reduced_rms_variation
    ):

        evidence.append({

            "domain":
                "dynamics",

            "finding":
                "elevated_crest_with_reduced_rms_variation",

            "role":
                "strong_pattern",

            "interpretation":
                "Peak-to-RMS separation is unusually large while short-term RMS variation is restrained. This warrants investigation of transient versus sustained energy."
        })

    # --------------------------------------------------
    # EVIDENCE GROUP 4
    # Spectral + dynamics
    # --------------------------------------------------

    if (
        lower_mid_concentration
        and
        peak_sustained_imbalance
    ):

        evidence.append({

            "domain":
                "spectral_dynamics",

            "finding":
                "low_mid_concentration_with_peak_sustained_imbalance",

            "role":
                "reinforcing_evidence",

            "interpretation":
                "The mix contains strong lower-mid concentration while also showing unusual separation between peak and sustained energy. Investigate whether low-mid-heavy sustained energy is contributing to the observed dynamics profile."
        })

    # --------------------------------------------------
    # EVIDENCE GROUP 5
    # Spectral + loudness
    # --------------------------------------------------

    if (
        lower_mid_concentration
        and
        overall_level_reduction
    ):

        evidence.append({

            "domain":
                "spectral_loudness",

            "finding":
                "spectral_imbalance_with_level_reduction",

            "role":
                "contextual_evidence",

            "interpretation":
                "The mix is substantially below the loudness reference while its spectral distribution remains strongly concentrated in the lower-mid region."
        })

    # --------------------------------------------------
    # EVIDENCE GROUP 6
    # High-frequency deficiency
    # --------------------------------------------------

    if reduced_high_frequency:

        evidence.append({

            "domain":
                "spectral",

            "finding":
                "reduced_high_frequency_energy",

            "role":
                "secondary_spectral_finding",

            "interpretation":
                "High-frequency energy is below the reference profile and should be investigated in relation to processing, arrangement, masking, and source availability."
        })

    # --------------------------------------------------
    # EVIDENCE GROUP 7
    # Stereo imbalance
    # --------------------------------------------------

    if left_right_balance:

        evidence.append({

            "domain":
                "stereo",

            "finding":
                "left_right_balance_deviation",

            "role":
                "independent_stereo_finding",

            "interpretation":
                "The stereo image shows measurable channel imbalance. Because phase, Mid/Side relationship, and mono compatibility remain within reference, this should be treated as a channel-balance investigation rather than a general stereo-width problem."
        })

    # --------------------------------------------------
    # EVIDENCE GROUP 8
    # Stereo integrity
    # --------------------------------------------------

    if (
        phase_normal
        and
        mid_side_normal
        and
        mono_normal
    ):

        evidence.append({

            "domain":
                "stereo",

            "finding":
                "stereo_integrity_within_reference",

            "role":
                "negative_evidence",

            "interpretation":
                "There is no strong evidence of a phase, excessive-width, or mono-compatibility problem."
        })

    return evidence


def build_priority_groups(
    evidence
):

    groups = {

        "primary":
            [],

        "supporting":
            [],

        "secondary":
            [],

        "independent":
            []
    }

    for item in evidence:

        role = item["role"]

        if role in {
            "primary_level_state",
            "strong_pattern"
        }:

            groups[
                "primary"
            ].append(
                item
            )

        elif role == (
            "reinforcing_evidence"
        ):

            groups[
                "supporting"
            ].append(
                item
            )

        elif role in {
            "secondary_spectral_finding",
            "contextual_evidence"
        }:

            groups[
                "secondary"
            ].append(
                item
            )

        elif role in {
            "independent_stereo_finding",
            "negative_evidence"
        }:

            groups[
                "independent"
            ].append(
                item
            )

    return groups


def save_output(
    spectral,
    evidence,
    groups
):

    output = {

        "file":
            spectral["file"],

        "measurement_type":
            "cross_domain_reasoning",

        "evidence":
            evidence,

        "priority_groups":
            groups
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
    spectral,
    groups
):

    print()
    print(
        "========================================"
    )
    print(
        "CROSS-DOMAIN REASONING"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"Target mix: "
        f"{spectral['file']}"
    )

    print()

    for category in [
        "primary",
        "supporting",
        "secondary",
        "independent"
    ]:

        print(
            category.upper()
        )

        print(
            "----------------------------------------"
        )

        items = groups[
            category
        ]

        if not items:

            print(
                "None"
            )

        for item in items:

            print(
                f"- {item['finding']}"
            )

            print(
                f"  {item['interpretation']}"
            )

        print()

    print(
        "========================================"
    )

    print(
        "Cross-domain reasoning saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "========================================"
    )

    print()


def main():

    spectral = load_json(
        SPECTRAL_DIAGNOSIS_FILE
    )

    loudness = load_json(
        LOUDNESS_DIAGNOSIS_FILE
    )

    dynamics = load_json(
        DYNAMICS_DIAGNOSIS_FILE
    )

    stereo = load_json(
        STEREO_DIAGNOSIS_FILE
    )

    evidence = build_cross_domain_evidence(
        spectral,
        loudness,
        dynamics,
        stereo
    )

    groups = build_priority_groups(
        evidence
    )

    save_output(
        spectral,
        evidence,
        groups
    )

    print_report(
        spectral,
        groups
    )


if __name__ == "__main__":
    main()
