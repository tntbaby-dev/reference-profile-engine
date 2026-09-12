# Reference Profile Engine

A statistical audio-analysis and engineering-diagnosis system for comparing a target mix against a dataset of professional reference mixes.

The system turns audio measurements into engineering intelligence:

Audio → Measurement → Reference → Deviation → Diagnosis → Source Evidence → Recommendation

## What it does

Reference Profile Engine analyzes professional reference mixes to build statistical profiles for:

- Spectral balance
- Loudness
- Dynamics
- Stereo characteristics

It then analyzes a target mix, measures its deviation from those reference profiles, performs engineering diagnosis, analyzes available stem contributions, and produces production-facing recommendations.

## Architecture

```text
Professional Reference WAVs
        ↓
Reference Analyzers
        ↓
Statistical Profile Builders
        ↓
Reference Profiles
Target Mix + Stems
        ↓
Target Analysis
        ↓
Deviation Detection
        ↓
Engineering Diagnosis
        ↓
Source-Level Evidence
        ↓
Cross-Domain Reasoning
        ↓
File Handling Lead
        ↓
Production Recommendations Analysis domains
Spectral
The spectral system measures relative energy across eight frequency bands:
Sub: 20–60 Hz
Bass: 60–120 Hz
Low Mid: 120–250 Hz
Mid: 250–500 Hz
Upper Mid: 500 Hz–2 kHz
Presence: 2–4 kHz
Brilliance: 4–8 kHz
Air: 8–16 kHz
The target is compared against statistical distributions derived from professional references.
Loudness
The loudness system analyzes:
Integrated LUFS
Estimated true peak
RMS level
Loudness Range (LRA)
Estimated true peak is currently calculated using 4× oversampling and should be treated as an estimate rather than a standards-grade true-peak implementation.
Dynamics
The dynamics system analyzes:
Sample peak
Crest factor
RMS dynamic variation
RMS P90–P10 spread
Sample peak is retained as a measurement but is not treated as a primary dynamics indicator because many reference masters are normalized close to 0 dBFS.
Stereo
The stereo system analyzes:
Left/right balance
Phase correlation
Mid/Side relationship
Mono compatibility
Engineering intelligence
The system does not treat statistical deviation as an automatic engineering problem.
Instead:
Measurement
    ↓
Reference Comparison
    ↓
Deviation
    ↓
Engineering Diagnosis
    ↓
Contextual Evidence
    ↓
Recommendation
A deviation indicates that something is statistically different from the reference population. The diagnostic layer determines whether that difference is potentially meaningful.
Recommendations are deliberately conservative. The system does not blindly prescribe EQ boosts, cuts, compression, widening, or other processing based on a single measurement.
Stem analysis
When stems are available, the system evaluates their contribution to diagnosed spectral regions.
Example target structure:
target/
├── ditb.wav
├── ditb_drums.wav
├── ditb_music.wav
└── ditb_wet_back_vox.wav
The target mix is analyzed separately from its stems.
Stem contribution is treated as supporting evidence rather than exact causal decomposition because summed stem power does not necessarily reconstruct mix power due to phase relationships, routing, automation, effects, and other interactions.
Master commands
Build reference profiles
Place professional reference WAV files inside references/, then run:
python build_reference_profiles.py
This runs the reference-analysis pipeline and builds the spectral, loudness, dynamics, and stereo reference profiles.
Analyze a target mix
Place the target mix and optional stems inside target/, then run:
python analyze_target.py
The controller automatically identifies the target mix and associated stems.
The target pipeline performs:
Spectral deviation analysis
Spectral engineering diagnosis
Loudness deviation analysis
Loudness engineering diagnosis
Dynamics deviation analysis
Dynamics engineering diagnosis
Stereo deviation analysis
Stereo engineering diagnosis
Stem contribution analysis
Source-level diagnosis
Recommendation generation
Cross-domain reasoning
File Handling Lead analysis
Project structure
reference-profile-engine/
├── analyze_target.py
├── build_reference_profiles.py
├── reference_analyzer.py
├── profile_builder.py
├── deviation_detector.py
├── engineering_diagnosis.py
├── diagnosis_prioritizer.py
├── loudness_reference_analyzer.py
├── loudness_profile_builder.py
├── loudness_deviation_detector.py
├── loudness_engineering_diagnosis.py
├── dynamics_reference_analyzer.py
├── dynamics_profile_builder.py
├── dynamics_deviation_detector.py
├── dynamics_engineering_diagnosis.py
├── stereo_reference_analyzer.py
├── stereo_profile_builder.py
├── stereo_deviation_detector.py
├── stereo_engineering_diagnosis.py
├── stem_contribution_analyzer.py
├── stem_contribution_ranker.py
├── source_level_diagnosis.py
├── recommendation_engine.py
├── cross_domain_reasoning.py
├── file_handling_lead.py
├── validate_profile.py
├── validate_loudness_profile.py
├── validate_dynamics_engineering_diagnosis.py
├── validate_loudness_engineering_diagnosis.py
├── validate_recommendation_engine.py
├── validate_stereo_engineering_diagnosis.py
├── requirements.txt
└── .gitignore
Installation
Create a Python 3.11 virtual environment:
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
Current limitations
The reference dataset is currently small and should be expanded for stronger statistical confidence.
Reference profiles are currently not genre-specific.
Spectral band measurements represent relative total power contribution within 20 Hz–16 kHz; they are not power-density measurements.
Stem contribution analysis provides evidence, not definitive causal attribution.
Estimated true peak is currently an oversampled estimate.
More granular stems will improve source-level diagnosis.
Artifact analysis is not yet integrated into the cross-domain reasoning layer.
Design principle
The system is designed around a simple principle:
Statistical difference is evidence, not a diagnosis.
The goal is to progressively combine measurements, reference distributions, engineering knowledge, source-level evidence, and cross-domain relationships before recommending production action.
Status
Reference Profile Engine V1
Completed:
Reference profile generation
Spectral deviation detection
Engineering diagnosis
Source-level diagnosis
Recommendation engine
Loudness integration
Dynamics integration
Stereo integration
Cross-domain reasoning
File Handling Lead
Automated reference pipeline
Automated target-analysis pipeline
