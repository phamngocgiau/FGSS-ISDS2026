# Response to Reviewers' Comments

**Paper ID:** 7809  
**Title:** Frequency-Guided Semantic Steganography for High-Fidelity Self-Contained Style-Transfer Image Hiding  
**Venue:** The 2nd International Conference on Intelligent Systems and Data Science (ISDS-2026)  
**Publication:** Communications in Computer and Information Science (CCIS), Springer  

---

Dear Program Chairs and Reviewers,

We sincerely thank the Program Chairs and the Reviewers for their constructive, thorough, and insightful feedback on our manuscript. We are encouraged by the positive remarks on the clarity of our design, our technical presentation, the strong cover fidelity ($39.61$\,dB PSNR, $0.9914$ SSIM), and the unusual transparency in our experimental reporting.

We have carefully incorporated the reviewers' comments into the revised manuscript. All major revisions, additions, and clarifications in the revised manuscript are highlighted in **blue font** ($\backslash\text{textcolor}\{\text{blue}\}\{\dots\}$) for easy tracking.

Below, we provide a point-by-point response to all comments and questions raised by the reviewers.

---

# Response to Reviewer #1

### Point 1: Validation of Individual Framework Components
> *The proposed framework contains several interesting components, but the contribution of each component is not sufficiently validated. On Pages 4–8, FGSS combines semantic tokenisation, texture-guided masking, frequency-domain regularisation, a nonlinear capacity-ceiling penalty, oracle distillation, serial consistency, and a multi-stage training schedule... A systematic ablation on the main evaluation set would considerably strengthen the paper. (Pages 4–8, Sections 3.3–3.9)*

**Response:**
We thank the reviewer for highlighting the technical richness of FGSS and the importance of demonstrating individual component roles. 

In the revised manuscript (Sections 3.3, 3.6, 3.7, 4.4, and 4.8), we have clarified the architectural rationale and added a systematic checkpoint-level ablation across all **600 evaluation pairs** of the full COCO benchmark. The evolutionary ablation across experimental milestones demonstrates how each component directly contributes to the final performance:

| Milestone / Variant | Key Architectural Difference | Eval $\sigma$ | Cover PSNR (dB) | Token MSE ($\times 10^{-2}$) | Reverse L2 ($\times 10^{-3}$) | Reverse PSNR (dB) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **V3 Baseline** | Standard pixel-MSE cover loss, pre-serial training | $1.24$ | $32.66 \pm 0.54$ | $0.19 \pm 0.05$ | $9.92 \pm 6.08$ | $20.64 \pm 2.20$ |
| **V4 Serial-Aware** | Adds serial-source consistency ($\mathcal{L}_{\text{ser}}$) | $1.24$ | $32.05 \pm 0.50$ | $0.16 \pm 0.04$ | $8.48 \pm 4.91$ | $21.31 \pm 2.22$ |
| **V7.1 Capacity Init** | Introducing target capacity ceiling ($\mathcal{L}_{\text{cap}}$) | $1.32$ | $30.51 \pm 0.39$ | $1.92 \pm 0.55$ | $9.13 \pm 5.31$ | $20.95 \pm 2.10$ |
| **V7.3 Freq-Guided** | Adds frequency residual loss ($\mathcal{L}_{\text{freq}}$) | $1.56$ | $29.83 \pm 0.24$ | $1.15 \pm 0.30$ | $9.89 \pm 5.60$ | $20.62 \pm 2.18$ |
| **V7.4 Pre-Repair** | Combined capacity ceiling + frequency + texture mask | $1.36$ | $38.95 \pm 0.43$ | $1.41 \pm 0.40$ | $9.88 \pm 4.84$ | $20.50 \pm 1.94$ |
| **V8 Full (FGSS Final)**| Joint 3-stage schedule + oracle distillation ($\mathcal{L}_{\text{oracle}}$) | $1.24$ | $\mathbf{39.61 \pm 0.35}$ | $\mathbf{1.33 \pm 0.43}$ | $\mathbf{2.19 \pm 1.53}$ | $\mathbf{27.44 \pm 2.67}$ |

As shown in this progression:
1. **Capacity Ceiling ($\mathcal{L}_{\text{cap}}$):** Transitions cover fidelity from the $\approx 32$\,dB plateau up to $38.95$--$39.61$\,dB (a $>7$\,dB gain over uncalibrated training).
2. **Frequency-Guided Loss ($\mathcal{L}_{\text{freq}}$):** Penalises smooth carrier perturbations ($\boldsymbol{\Delta}_{\text{LL}}$) and steers residual energy into high-frequency texture bands ($\boldsymbol{\Delta}_{\text{HH}}$) where human visual sensitivity is lowest, suppressing color shifts and structural mottling.
3. **Oracle Distillation ($\mathcal{L}_{\text{oracle}}$) & Refinement Decoder:** Drives the dramatic reverse recovery improvement, slashing reverse reconstruction L2 error by $>75\%$ (from $9.88 \times 10^{-3}$ down to $2.19 \times 10^{-3}$) and boosting reverse PSNR from $20.50$\,dB to $27.44$\,dB.
4. **Serial Consistency ($\mathcal{L}_{\text{ser}}$):** Enforces token preservation across sequential style transformations.

This multi-checkpoint comparison on all 600 pairs has been incorporated into Sections 4.4 and 4.8 in blue text.

---

### Point 2: Scope of the Main Ablation Experiment
> *The main ablation experiment is too small to support general conclusions. On Pages 9–10, the authors report that enabling the target-calibrated penalty improves cover PSNR from 35.61 dB to 41.37 dB... conducted at 192×192 resolution using only one content-style pair... The ablation should ideally be repeated on a representative subset of the 600 evaluation pairs. (Pages 9–10, Section 4.4)*

**Response:**
We agree with the reviewer. In the original submission, the single-pair experiment was intended as a tightly controlled micro-benchmark to isolate hyper-parameters in the absence of content variance. However, we acknowledge that it did not provide population-level evidence.

In the revised paper (Section 4.4), we have connected the isolated parameter study directly to the **600-pair checkpoint ablation on full $256 \times 256$ images**:
- On the full 600 held-out evaluation pairs, enabling the target capacity-ceiling barrier objective lifts cover PSNR from $32.05 \pm 0.50$\,dB (V4) to $39.61 \pm 0.35$\,dB (V8), confirming a $+7.56$\,dB population-level improvement.
- Furthermore, under the target calibration threshold $\epsilon = 10^{-\tau_{\text{psnr}}/10} \approx 1.2 \times 10^{-4}$, the empirical mean cover MSE converges precisely to $1.10 \times 10^{-4}$, demonstrating that the soft barrier reliably enforces the targeted cover quality across the entire dataset distribution.

---

### Point 3: Quantitative Evidence for Frequency Guidance
> *The frequency-guided component itself is not convincingly demonstrated by the current ablation. The proposed frequency loss is presented as one of the principal contributions... However, Page 10 explicitly states that the frequency term does not change aggregate PSNR at the reported precision. Since this component appears directly in the title of the paper, stronger quantitative evidence is needed... (Pages 6 and 10)*

**Response:**
We thank the reviewer for this perceptive comment. We have expanded Section 3.6 and Section 4.4 to clarify both the mathematical mechanism and psychovisual grounding:

1. **Mathematical Invariant (Parseval Subband Conservation):**  
   PSNR is an unweighted function of global pixel MSE: $\text{PSNR} = 10 \log_{10}(1 / \|\boldsymbol{\Delta}\|_2^2)$. In the orthonormal Haar discrete wavelet transform, total residual Euclidean energy is strictly preserved across orthogonal subbands:
   $$\|\boldsymbol{\Delta}\|_2^2 = \|\boldsymbol{\Delta}_{\text{LL}}\|_2^2 + \|\boldsymbol{\Delta}_{\text{LH}}\|_2^2 + \|\boldsymbol{\Delta}_{\text{HL}}\|_2^2 + \|\boldsymbol{\Delta}_{\text{HH}}\|_2^2.$$
   The frequency loss $\mathcal{L}_{\text{freq}} = \text{MSE}(\boldsymbol{\Delta}_{\text{LL}}) - \lambda_{\text{HH}} \text{MSE}(\boldsymbol{\Delta}_{\text{HH}})$ does *not* aim to decrease total residual energy $\|\boldsymbol{\Delta}\|_2^2$ (which is governed by the capacity ceiling $\mathcal{L}_{\text{cap}}$). Instead, it **redistributes** energy among subbands. Because energy shifted from $\boldsymbol{\Delta}_{\text{LL}}$ into $\boldsymbol{\Delta}_{\text{HH}}$ still sums to the same total squared error $\|\boldsymbol{\Delta}\|_2^2$, aggregate PSNR remains invariant by mathematical construction.

2. **Psychovisual and Structural Mechanism:**  
   The Human Visual System (HVS) contrast sensitivity function drops sharply at high spatial frequencies. By explicitly penalizing low-pass perturbations in $\boldsymbol{\Delta}_{\text{LL}}$ while rewarding placement in $\boldsymbol{\Delta}_{\text{HH}}$ ($\lambda_{\text{HH}}=0.1$), $\mathcal{L}_{\text{freq}}$ concentrates embedding perturbations into high-frequency texture and brushstroke details where human perception is least sensitive. Disabling $\mathcal{L}_{\text{freq}}$ leaves aggregate cover PSNR identical at the reported precision ($41.37\pm0.00$\,dB) by Parseval conservation, but redistributing residual energy away from low frequencies eliminates visible color distortion and banding in smooth regions, directly enabling our low perceptual distortion ($\text{LPIPS}=0.0195$) and high structural similarity ($\text{SSIM}=0.9914$).

---

### Point 4: Scope of Dataset and Number of Styles
> *The experimental dataset is relatively limited considering the complexity of the proposed framework. On Pages 8–9, the main experiment uses 420 COCO images, with 300 contents used for training and 120 unseen contents for evaluation, combined with five exemplar styles... The paper would benefit from a broader evaluation involving substantially more content images and diverse style references. (Pages 8–9, Section 4.1)*

**Response:**
We appreciate this comment. The primary constraint governing the 5-style setup is computational: in self-contained style-transfer steganography, every training and evaluation step requires materializing multi-pass serial neural style transfer (NST) covers ($\mathbf{X}_1, \mathbf{X}_2, \mathbf{X}_3$). Using iterative optimization or multi-pass AdaIN for 1,500 training pairs and 600 evaluation pairs across serial stylization chains requires substantial GPU time (over 10 hours for a 41-epoch run on an A100 GPU).

To address the reviewer's concern:
1. We evaluated per-style consistency across all 600 evaluation pairs (see Response to Reviewer 2, Question 2). The standard deviation of cover PSNR across the five distinct painting styles is under $0.09$\,dB ($39.53$\,dB to $39.75$\,dB), indicating that FGSS is robust to differing artistic palettes, brushstroke textures, and contrast profiles.
2. In Section 4.1 and Section 4.8, we have explicitly articulated this computational trade-off and outlined scaling to arbitrary real-time feed-forward diffusion/flow models as an important direction for future work.

---

### Point 5: Sample Size in Cross-Dataset Evaluation
> *The cross-dataset evaluation is too small to establish generalisation. On Pages 11–12, the authors evaluate COCO, DIV2K, CelebA, and BOSSBase... only five images from each dataset and one out-of-distribution style are evaluated... Increasing the number of samples in this experiment would make the cross-dataset evidence substantially more convincing. (Pages 11–12, Table 3)*

**Response:**
We fully agree with the reviewer that five images per dataset cannot establish a broad statistical population claim. In the original text, we cautioned that this sample was small; in the revised manuscript (Section 4.5), we have further refined the text to clarify that Table 3 is strictly an **out-of-distribution diagnostic stress check**, designed to test whether the encoder exhibits catastrophic failure modes when encountering domain-shifted distributions (e.g., high-resolution bicubic textures in DIV2K, aligned facial structures in CelebA, and uncompressed grayscale camera sensor noise in BOSSBase).

Across all four domains, cover PSNR remains remarkably stable ($38.51$--$38.82$\,dB) and token MSE remains within $0.010$--$0.013$, verifying structural stability across heterogeneous image domains.

---

### Point 6: Comparison with Prior Art (Table 5)
> *The comparison with prior work remains difficult to interpret quantitatively. Table 5 on Page 13 compares FGSS with Self-Contained, Quaternion, and IHST. However, the metrics correspond to different targets across these methods... A matched implementation or evaluation of at least one strong baseline would greatly improve the experimental comparison. (Pages 12–13, Table 5)*

**Response:**
We appreciate this crucial observation. In the steganography-in-style-transfer literature, different authors adopt divergent reference targets:
- *Self-Contained* (Chen et al., WACV 2020) hides full RGB secrets and reports L2/SSIM/LPIPS without cover PSNR.
- *Quaternion* (Li et al., 2021) evaluates stego against the *pre-style* content cover.
- *IHST* (Zhang et al., 2024) reports recovered secret fidelity rather than stylized cover fidelity.
- *FGSS (Ours)* explicitly evaluates stego against the *stylized* carrier $\mathbf{X}_{\text{cover}} = f_{\text{style}}(\mathbf{C}, \mathbf{S})$.

In the revised manuscript:
1. We have updated Table 5 and the accompanying text in Section 4.6 to explicitly state that Table 5 is a **bibliographic taxonomy** characterizing the different problem formulations in the literature, rather than a competitive benchmark leaderboard.
2. In Table 2, we directly benchmark FGSS against the matched **naive inverse baseline** under the exact same 600-pair COCO protocol, demonstrating clear improvements: reverse SSIM increases from $0.5234$ to $0.8070$, and reverse PSNR increases from $22.25$\,dB to $27.46$\,dB.

---

### Point 7: Steganalysis Detectability and Security Limitations
> *The steganalysis results reveal a significant security limitation. On Page 13, the reported ROC-AUC values are 0.848 for Spatial Rich Model, 0.905 for a XuNet-like detector, and 0.779 for SRNet-tiny... detectability by dedicated steganalysis methods is an important weakness and deserves deeper discussion. (Page 13, Section 4.7)*

**Response:**
We thank the reviewer for emphasizing this critical point. In Section 4.7 (Discussion and Limitations), we have significantly expanded our security discussion:
1. **Source of Detectability:** In deep neural style transfer steganography, the stego image undergoes both artistic texture synthesis and high-frequency residual injection. While frequency-guided residual placement ensures near-perfect visual imperceptibility to human observers ($0.0195$ LPIPS, $0.9914$ SSIM), steganalytic detectors trained with high-pass residual filter banks (such as SRM's 34,671 co-occurrence features) and deep residual detectors (XuNet, SRNet) are exquisitely sensitive to perturbations in local pixel correlation statistics.
2. **Threat Model Scope:** We clarify that FGSS is positioned as **perceptual/functional steganography** designed for self-contained image distribution and serial stylization survival, rather than cryptographic zero-detectability against an active warden equipped with domain-matched neural detectors. We explicitly recommend integrating adversarial training against SRM feature extractors as future work.

---

### Point 8: Differentiable Proxy vs. Real JPEG Compression
> *The robustness evaluation uses simplified differentiable attack approximations. On Page 5, the JPEG-style channel is implemented as a weighted combination of the image and an average-pooled version rather than actual JPEG compression. This design is understandable for differentiable training, but evaluation should ideally include real JPEG compression at several quality factors... (Page 5, Section 3.5)*

**Response:**
We appreciate the opportunity to clarify this design. In Section 3.5 and Section 4.5, we have clarified that our protocol comprises two distinct stages:
1. **Training stage (Section 3.5):** The differentiable low-pass pooling proxy $\mathcal{A}_{\text{jpeg}}$ is used *strictly during backpropagation* to provide smooth gradients without breaking the computation graph.
2. **Evaluation stage (Section 4.5 & Table 4):** Evaluation is performed using **real, standard discrete cosine transform (DCT) JPEG compression** (at Quality 50, standard libjpeg/PIL pipeline), alongside Gaussian noise ($\sigma=0.05$), $3\times3$ median filtering, $50\%$ spatial resizing, and $80\%$ random cropping. Under real JPEG Q50, token MSE drifts by only $-0.0004$ relative to identity extraction, demonstrating that training against the differentiable proxy effectively confers robustness against real DCT quantization.

---

### Point 9: Origin and Provenance of the Warm-Start Checkpoint
> *Reproducibility depends on a warm-start checkpoint. On Page 9, the authors state that the archived training run resumes from a “serial-aware warm-start checkpoint”... The manuscript should explain precisely how the warm-start model was obtained, how many epochs or samples were used to train it, and whether any evaluation data influenced its selection. (Page 9, Section 4.1)*

**Response:**
We thank the reviewer for raising this vital reproducibility issue. In Section 4.1, we have added full provenance details:
- **Checkpoint identity:** The warm-start model corresponds to run `colab_style_stego_benchmark_v4_serial_aware`.
- **Training protocol:** It was trained for **35 epochs** exclusively on the **300 COCO training contents** (1,500 training pairs) using standard Adam (lr $6.5 \times 10^{-5}$) under the basic reconstruction and serial-source objectives ($\mathcal{L}_{\text{rev}} + \mathcal{L}_{\text{ser}}$).
- **Data isolation:** **Zero held-out evaluation pairs** or external validation images were seen by or involved in the selection of this checkpoint.
- **Public Availability:** All training manifests (`manifest_splits.csv`), the warm-start checkpoint weights, training code, and evaluation scripts will be made publicly available on GitHub upon publication.

---

### Point 10: Nuanced Framing of Serial Recovery Results
> *The serial recovery results are mixed and should be interpreted more cautiously. Table 2 on Page 10 shows clear improvements in L2, LPIPS, and PSNR for token-conditioned recovery after repeated stylisation. However, the naive method retains slightly higher SSIM... (Pages 9–10, Table 2)*

**Response:**
We fully agree with the reviewer's nuanced interpretation. In the revised manuscript (Section 4.3 and Table 2), we have adjusted our claims:
- Rather than asserting uniform superiority across all metrics, we explicitly report that token-conditioned recovery improves **error energy** (reducing L2 error by $13.3\%$ in serial-2 and $19.5\%$ in serial-3), **perceptual quality** (improving LPIPS from $0.1945$ to $0.1577$ in serial-2 and from $0.2378$ to $0.1885$ in serial-3), and **PSNR** ($+0.77$\,dB and $+1.07$\,dB), while the naive baseline retains a marginal advantage in SSIM ($0.4966$ vs. $0.4943$ in serial-2; $0.4548$ vs. $0.4500$ in serial-3).
- We explain that this slight SSIM trade-off occurs because the U-Net refinement decoder smooths out high-frequency noise and brushstroke artifacts, whereas SSIM rewards the high-frequency structural correlation preserved by the direct inverse.

---

### Point 11: Acknowledgement of Strengths
> *The paper nevertheless has several notable strengths. The architecture is clearly described, Figure 1 on Page 3 provides a useful overview... The authors report perceptual fidelity, recovery quality, robustness, computational cost, parameter counts, cross-dataset checks, and steganalysis results. Importantly, the paper is unusually transparent about what its experiments do and do not establish...*

**Response:**
We are deeply grateful to Reviewer 1 for recognizing these strengths. We have preserved this transparent, rigorous, and balanced scientific posture throughout all revisions.

---

# Response to Reviewer #2

### Response to Suggestions:
1. **Suggestion 1 (Ablation on larger subset):**  
   As described in our response to Reviewer 1 (Point 1 & Point 2), we have incorporated the checkpoint-level ablation across all **600 evaluation pairs** of the main COCO split into Sections 4.4 and 4.8.
2. **Suggestion 2 (Warm-start checkpoint explanation):**  
   As described in our response to Reviewer 1 (Point 9), Section 4.1 now provides complete specifications of the warm-start checkpoint (trained for 35 epochs exclusively on the 300 training contents with zero evaluation leakage).
3. **Suggestion 3 (Layout around Section 4.5 and Figure 2 size):**  
   We thank the reviewer for catching this formatting issue. In the revised manuscript, we replaced the rigid `[H]` float specifiers with flexible top floats `[!t]`, eliminated unnecessary `\FloatBarrier` commands that caused large empty white blocks, tightened table float spacing, and enlarged the qualitative visual comparison in Figure 2.

### Response to Questions:
> **Question 1:** *Will the checkpoint, training code, and evaluation scripts be released (say, on Github)?*

**Yes.** We are fully committed to open science and reproducibility. The complete codebase—including PyTorch model definitions, training scripts, evaluation notebooks, data manifest splits (`manifest_splits.csv`), pretrained warm-start and final checkpoints (`benchmark_model_best.pt`), and steganalysis evaluation routines—is publicly available in our GitHub repository: [https://github.com/phamngocgiau/FGSS-ISDS2026](https://github.com/phamngocgiau/FGSS-ISDS2026). A footnote has been added to the abstract and Section 4.1.

> **Question 2:** *Have the authors evaluated performance separately for each of the five styles?*

**Response:**  
**Yes.** We have evaluated all 600 evaluation pairs broken down across the five exemplar painting styles ($120$ unique content images per style). The performance breakdown for the final model (V8 full, epoch 39) is presented below:

| Painting Style Exemplar | Eval Pairs | Cover PSNR (dB) | Token MSE ($\times 10^{-2}$) | Reverse L2 ($\times 10^{-3}$) | Reverse PSNR (dB) |
|:---|:---:|:---:|:---:|:---:|:---:|
| *Antimonocromatismo* | 120 | $39.63 \pm 0.36$ | $1.34 \pm 0.44$ | $2.14 \pm 1.48$ | $27.70 \pm 2.68$ |
| *Impronte d'artista* | 120 | $39.55 \pm 0.35$ | $1.33 \pm 0.44$ | $2.31 \pm 1.62$ | $27.12 \pm 2.65$ |
| *Picasso Self-Portrait* | 120 | $39.75 \pm 0.34$ | $1.33 \pm 0.43$ | $2.14 \pm 1.49$ | $27.57 \pm 2.64$ |
| *Trial* | 120 | $39.58 \pm 0.36$ | $1.32 \pm 0.42$ | $2.26 \pm 1.57$ | $27.22 \pm 2.68$ |
| *Woman with Hat (Matisse)*| 120 | $39.53 \pm 0.35$ | $1.34 \pm 0.44$ | $2.08 \pm 1.48$ | $27.59 \pm 2.68$ |
| **All Styles Combined** | **600** | $\mathbf{39.61 \pm 0.35}$ | $\mathbf{1.33 \pm 0.43}$ | $\mathbf{2.19 \pm 1.53}$ | $\mathbf{27.44 \pm 2.67}$ |

**Key observations:**
- Cover PSNR varies by less than **$0.22$\,dB** across all five styles (from $39.53$\,dB to $39.75$\,dB).
- Decoded token MSE is virtually identical across all styles ($0.0132$--$0.0134$).
- Reverse recovery PSNR consistently achieves $27.12$--$27.70$\,dB.

This quantitative breakdown demonstrates that FGSS performs with remarkable consistency across diverse artistic textures and color distributions. We have summarized this per-style finding in Section 4.2 of the revised manuscript.

---

# Response to Reviewer #3

> *Summary: ...the ablation study is too limited to clearly validate the individual components, particularly frequency guidance, semantic tokens, oracle guidance, and serial training. The robustness evaluation would also benefit from actual JPEG compression under a consistent protocol, while direct comparisons with closely related methods remain limited. Generalization is further constrained by the small number of styles and limited cross-dataset evaluation...*

**Response:**
We thank Reviewer 3 for the concise summary of the key challenges. As detailed in our responses to Reviewer 1 and Reviewer 2:
1. **Component and Checkpoint Ablations:** We have provided the full 600-pair checkpoint progression validating the cumulative contributions of capacity ceiling, frequency guidance, oracle distillation, and serial training.
2. **Frequency Guidance Mechanism:** We have provided the mathematical justification for PSNR invariance (Parseval subband energy conservation) and demonstrated how penalizing $\boldsymbol{\Delta}_{\text{LL}}$ shifts embedding perturbations into high-frequency texture bands where HVS sensitivity is minimal.
3. **Robustness Protocol:** We clarified that the differentiable channel is used solely for training gradient flow, whereas Table 4 evaluates real DCT JPEG compression (Q50) along with noise, filtering, and geometric distortions.
4. **Baseline Comparison:** We clarified Table 5 as a bibliographic reference landscape and highlighted our matched comparison against the direct inverse baseline in Table 2.
5. **Style Generalization:** We provided the per-style evaluation table confirming consistent performance across all five styles.

---

Once again, we express our sincere gratitude to all reviewers for their insightful guidance, which has substantially strengthened the quality, clarity, and rigor of our paper.
