# FGSS: Frequency-Guided Semantic Steganography for High-Fidelity Self-Contained Style-Transfer Image Hiding

[![Conference](https://img.shields.io/badge/ISDS--2026-Accepted-success.svg)](https://isds.ctu.edu.vn/2026/)
[![Proceedings](https://img.shields.io/badge/Springer-CCIS-blue.svg)](https://www.springer.com/series/7899)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange.svg)](https://pytorch.org/)

Official PyTorch implementation of the paper:
> **"Frequency-Guided Semantic Steganography for High-Fidelity Self-Contained Style-Transfer Image Hiding"**  
> *Ngoc-Giau Pham, Minh-Tuan Bui, and Phuoc-Hung Vo*  
> The 4th International Conference on Intelligent Systems and Data Science (**ISDS 2026**), Yuan Ze University, Taiwan.  
> Published in **Communications in Computer and Information Science (CCIS)**, Springer.

---

## 📌 Abstract

Style-transfer steganography uses the naturally variable texture of stylised images to mask embedding residuals, but repeated stylisation can degrade recovery. We investigate two design choices that contribute to this trade-off: distortion regularisers without a target-fidelity threshold and spatially dense payloads. 

**FGSS** represents the original content using a compact $\mathbf{z} \in \mathbb{R}^{64\times32\times32}$ semantic token and an auxiliary thumbnail. It combines:
1. **Target-calibrated capacity-ceiling loss ($\mathcal{L}_{\text{cap}}$):** A soft quadratic barrier activating above a PSNR-derived MSE threshold ($\approx 1.2 \times 10^{-4}$ for $39$\,dB).
2. **Frequency-guided residual placement ($\mathcal{L}_{\text{freq}}$):** Penalises smooth carrier perturbations in the low-frequency band ($\boldsymbol{\Delta}_{\text{LL}}$) and shifts perturbation energy into high-frequency texture bands ($\boldsymbol{\Delta}_{\text{HH}}$) where human visual sensitivity is lowest.
3. **Oracle-guided reverse decoder ($\mathcal{L}_{\text{oracle}}$):** Cascaded token prior and U-Net refinement decoder supervised against ground-truth representations.
4. **Serial-source consistency ($\mathcal{L}_{\text{ser}}$):** Enforces recovery across sequential multi-pass stylisations.

---

## 🚀 Key Results (600 Evaluation Pairs on COCO val2017)

| Metric | Baseline | FGSS (Ours) | Delta / Note |
|:---|:---:|:---:|:---|
| **Cover PSNR (dB)** | $32.66 \pm 0.54$ | $\mathbf{39.61 \pm 0.35}$ | $+6.95$\,dB improvement |
| **Cover SSIM** | $0.942$ | $\mathbf{0.9914 \pm 0.0030}$ | Near-lossless structure |
| **Cover LPIPS** | $0.084$ | $\mathbf{0.0195 \pm 0.0081}$ | Visually imperceptible |
| **Reverse Recovery SSIM** | $0.5234$ | $\mathbf{0.8070 \pm 0.0858}$ | $+0.2836$ over naive direct inverse |
| **Reverse Recovery PSNR** | $22.25$\,dB | $\mathbf{27.46 \pm 2.67}$\,dB | $+5.21$\,dB clean recovery |
| **End-to-End GPU Latency** | --- | $\mathbf{0.0223}$\,s / image | RTX 5070 Ti ($256 \times 256$) |

### Per-Style Consistency Breakdown (120 pairs per style)

| Exemplar Style | Cover PSNR (dB) | Token MSE ($\times 10^{-2}$) | Reverse L2 ($\times 10^{-3}$) | Reverse PSNR (dB) |
|:---|:---:|:---:|:---:|:---:|
| *Antimonocromatismo* | $39.63 \pm 0.36$ | $1.34 \pm 0.44$ | $2.14 \pm 1.48$ | $27.70 \pm 2.68$ |
| *Impronte d'artista* | $39.55 \pm 0.35$ | $1.33 \pm 0.44$ | $2.31 \pm 1.62$ | $27.12 \pm 2.65$ |
| *Picasso Self-Portrait* | $39.75 \pm 0.34$ | $1.33 \pm 0.43$ | $2.14 \pm 1.49$ | $27.57 \pm 2.64$ |
| *Trial* | $39.58 \pm 0.36$ | $1.32 \pm 0.42$ | $2.26 \pm 1.57$ | $27.22 \pm 2.68$ |
| *Woman with Hat (Matisse)* | $39.53 \pm 0.35$ | $1.34 \pm 0.44$ | $2.08 \pm 1.48$ | $27.59 \pm 2.68$ |
| **Combined (All Styles)** | $\mathbf{39.61 \pm 0.35}$ | $\mathbf{1.33 \pm 0.43}$ | $\mathbf{2.19 \pm 1.53}$ | $\mathbf{27.44 \pm 2.67}$ |

---

## 📁 Repository Structure

```text
FGSS-ISDS2026/
├── source_data/                    # Audited experimental data and protocol scripts
│   ├── model_definition.py         # PyTorch architectures (Tokenizer, Encoder, Decoders)
│   ├── training_protocol.py        # Complete training recipe & schedule definition
│   ├── ablation.csv                # Single-pair controlled parameter study
│   ├── paper_table_main.csv        # Main evaluation metrics (clean, RBN, JPEG, serial)
│   ├── token_summary.csv           # Token-side MSE across channels
│   ├── cross_dataset_metrics.csv   # OOD checks (DIV2K, CelebA, BOSSBase)
│   ├── robustness_metrics.csv      # Real DCT JPEG Q50, filter, crop, noise tests
│   └── run_summary.json            # Run metadata & training loss trajectories
├── followup_results/               # Detailed pair-level benchmark outputs
│   ├── checkpoint_ablation_600_summary.json # 600-pair checkpoint ablation
│   ├── checkpoint_ablation_600_per_pair.csv # Exact metrics for all 600 pairs
│   ├── full_srm_steganalysis_summary.json   # 34,671-dim SRM steganalysis probe
│   └── neural_steganalysis_summary.json     # XuNet-lite & SRNet-tiny probes
├── paper_assets/                   # Architecture diagrams and figure assets
├── Review_and_Submission/          # Camera-ready rebuttal and submission assets
│   ├── Response_to_Reviewers.md    # Full point-by-point response to reviewers
│   ├── Response_to_Reviewers.pdf   # Compiled rebuttal letter (PDF)
│   └── Response_to_Reviewers.tex   # LaTeX source of rebuttal
├── Compiled_PDFs/                  # Camera-ready compiled paper & response PDFs
│   ├── ISDS2026_FGSS_compact.pdf   # 15-page Springer CCIS manuscript
│   └── Response_to_Reviewers.pdf   # Rebuttal document
├── ISDS2026_FGSS_compact.tex       # Camera-ready LaTeX paper (revisions in blue)
├── audit_paper.py                  # Self-contained numerical auditing script
├── LICENSE                         # MIT License
└── README.md                       # This document
```

---

## 🛠️ Reproduction & Verification

### 1. Verification of Paper Numbers
To mathematically verify all 171 reported numbers in the manuscript against bundled ground-truth CSV/JSON logs:
```bash
python audit_paper.py
```
*Expected output:* `ALL NUMBERS VERIFIED - 0 ERRORS (171 verification points)`.

### 2. Building the Manuscript
To compile the camera-ready Springer CCIS LaTeX manuscript:
```bash
pdflatex -interaction=nonstopmode ISDS2026_FGSS_compact.tex
pdflatex -interaction=nonstopmode ISDS2026_FGSS_compact.tex
```

---

## 📜 Citation

If you find our work useful in your research, please cite:

```bibtex
@inproceedings{pham2026fgss,
  author    = {Pham, Ngoc-Giau and Bui, Minh-Tuan and Vo, Phuoc-Hung},
  title     = {Frequency-Guided Semantic Steganography for High-Fidelity Self-Contained Style-Transfer Image Hiding},
  booktitle = {Proceedings of the 4th International Conference on Intelligent Systems and Data Science (ISDS 2026)},
  series    = {Communications in Computer and Information Science (CCIS)},
  publisher = {Springer},
  year      = {2026}
}
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
