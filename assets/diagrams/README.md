# Reproducible diagrams

Every .mmd file has a matching .png, generated from the same ordered node definitions by scripts/build_pdfs.py. Mermaid files can be rendered by GitHub or any compatible Mermaid renderer; PNGs are used in PDFs.

- architecture: actual local system components.
- data_flow: review input through human-reviewed export.
- preprocessing: benchmark cleaning and splitting.
- training: fit, validation selection, freeze and evaluation.
- inference: model inference and explicit policy routing.
- interaction: user interaction flow.
- deployment: implemented localhost deployment.
- external: optional public dataset download, with no external runtime API.

These describe the assessment implementation. Future authenticated production connectors are not shown as implemented services.
