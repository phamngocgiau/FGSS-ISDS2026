# ISDS 2026 — Submission Format Check

Source: <https://isds.ctu.edu.vn/2026/> (fetched 30 July 2026)

## Conference requirements

| Item | Requirement |
|---|---|
| Conference | The 4th Int. Conf. on Intelligent Systems and Data Science (ISDS 2026) |
| Venue / dates | Yuan Ze University, Taiwan — 14–15 Nov 2026 |
| **Format** | **Springer LNCS/CCIS one-column page format** |
| Template | **LaTeX strongly preferred** over Word ("if two papers are of similar quality, preference will be given to the paper prepared in LaTeX") |
| Length | **Long paper 12–15 pages**; short paper 6–8 pages |
| Language | English |
| File type | PDF |
| Submission | EasyChair — <https://easychair.org/conferences/?conf=isds2026> |
| Deadline (submission) | **30 July 2026** |
| Acceptance notice | 07 Sept 2026 |
| Final paper | 14 Sept 2026 |
| Tracks | 1 Intelligent/Recommender Systems · 2 Data Science & ML · **3 Image Processing & Pattern Recognition** (this paper) · 4 NLP |
| Publication | Top 10% → JIT (ICT Research); 35% → Springer CCIS (Scopus Q3); 15% → CTUJoISD (Q4); selected papers → SN Computer Science (Q1) after ≥30% extension |

Springer guidelines: <https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines>

## What was changed (`bob_refine.tex` → `ISDS2026_FGSS.tex`)

| Area | Before (IEEE / ICT Đồng Tháp) | After (ISDS 2026 / LNCS) |
|---|---|---|
| Class | `\documentclass[conference]{IEEEtran}` (two-column) | `\documentclass[runningheads]{llncs}` (one-column) |
| Running head | fancyhdr banner "Hội thảo khoa học Quốc gia … Đồng Tháp, 22/5/2026" | removed; `\titlerunning` + `\authorrunning` |
| Language pkg | `\usepackage[utf8]{vietnam}` + `babel` | `fontenc` T1 + `inputenc` utf8 (English only) |
| Authors | `tabular` block with `\IEEEauthorblock*` / `\thanks` | LNCS `\author{... \inst{n}}` + `\institute{... \email{}}` |
| Abstract | `abstract` + `IEEEkeywords` | LNCS `abstract` + `\keywords{... \and ...}` |
| First paragraph | `\IEEEPARstart{H}{iding}` | plain text |
| Floats | 8 × `figure*` / `table*` (span-column) | all converted to single-column `figure` / `table` |
| Widths | `\columnwidth`, `\resizebox{\columnwidth}` | `\textwidth` fractions; `resizebox` replaced by `p{}` columns |
| Bibliography | IEEE style (`S.-P. Lu, R. Wang, "Title," in *Proc. …*, 2021, pp. …`) | Springer LNCS style (`Lu, S.-P., Wang, R.: Title. In: … pp. … (2021)`) — 28 entries |
| Removed | `tikz` + full `tikzset` (unused), `cite`, `subcaption` (unused; conflicts with `llncs`) | — |
| Kept | `booktabs`, `colortbl`/`rowcolor` shading, `tcolorbox` takeaway box, `algorithm`/`algpseudocode` | — |

Cross-reference audit: every `\ref` in the file resolves to a `\label` defined in the same file (verified by pattern match — no orphan references). All 11 `\includegraphics` targets exist under `paper_assets/`.

## Build

```powershell
cd D:\NCS_2023\Paper\2026\VCRIS\style_tranfer
pdflatex -interaction=nonstopmode ISDS2026_FGSS.tex
pdflatex -interaction=nonstopmode ISDS2026_FGSS.tex
```

`llncs.cls` ships with MiKTeX and TeX Live — no manual download needed. If MiKTeX prompts, allow on-the-fly package installation.

## ⚠ Open item: page count

**This was not verified by compilation** (no LaTeX/sandbox available in this session).
Moving from IEEE two-column to LNCS one-column typically **increases** page count by
roughly 1.6–1.8×. Rough estimate for the current file: **~24–27 pages** —
i.e. well above the 15-page long-paper ceiling.

Compile first, then check:

```powershell
pdfinfo ISDS2026_FGSS.pdf | Select-String "Pages|Page size"
rg -n "Overfull|Underfull|undefined|Warning|Error" ISDS2026_FGSS.log
```

### ✅ Compact variant produced: `ISDS2026_FGSS_compact.tex`

Items 1–7 of the plan below have been applied to a separate file; `ISDS2026_FGSS.tex`
is untouched as the full reference version. Changes in the compact variant:

- **Figures 12 → 5.** Kept: architecture, qualitative grid, frequency decomposition,
  robustness overview, training curve. Dropped: `intro_teaser` (redundant with the
  qualitative grid), `ceiling_penalty` (Eq. 8 is self-explanatory), `phase_timeline`
  (described in prose), `style_grid`, `attack_grid`, `cross_dataset_grid`,
  `multi_style_grid` (findings folded into the surrounding text).
- **Tables 11 → 7.** Dropped `tab:relwork`, `tab:losscheat`, `tab:sota_cross`
  (its content is now two sentences of prose) and `tab:inference` (timings moved
  into prose). `tab:serial2` + `tab:serial3` merged into one `tab:serial` with a
  `\multirow` block per serial step; the seven `blend_*` rows reduced to a
  one-sentence note.
- **Text.** Introduction 6 → 4 paragraphs; `sec:revdec`/`sec:rev`/`sec:serial`
  merged into one subsection; `sec:proto` + `sec:impl` merged; qualitative
  inspection collapsed from 5 paragraphs to 1; `sec:sota` + cost + prior-art
  merged into one subsection; conclusion 3 → 2 paragraphs.
- Every dropped float's `\ref` was removed — no dangling references (verified by
  pattern match). Environments balanced: 5 `figure`, 7 `table`, 1 `algorithm`.
- All 28 bibliography entries remain cited.

Estimated result: **~14–16 pages.** Compile and confirm; if still over, apply
item 8 (Introduction → 3 paragraphs) and drop `tab:ablation` in favour of
reporting the $+5.76$\,dB delta in prose.

### Trimming plan, in order of least damage to the contribution

1. **Merge the four qualitative grid figures into one** (`qualitative_grid`,
   `freq_decomp`, `attack_grid`, `cross_dataset_grid`, `multi_style_grid` →
   keep 2, move 3 to supplementary). ≈ −4 pages.
2. **Fold `tab:serial3` into `tab:serial2`** as extra rows, or move serial-3 to
   supplementary and report only the summary sentence. ≈ −1.5 pages.
3. **Drop `tab:losscheat`** (the 13-term cheat sheet) — the weights are already
   listed in Section "Implementation Details". ≈ −1 page.
4. **Drop `tab:sota_cross`** (explicitly labelled "not directly comparable"). ≈ −1 page.
5. **Drop `tab:relwork`** — the three families are described in prose immediately
   above it. ≈ −1 page.
6. **Compress Method subsections** `sec:revdec` and `sec:rev` (architecture
   channel-by-channel detail → one paragraph each). ≈ −1.5 pages.
7. **Shorten `sec:proto` and `sec:impl`**; move the full hyper-parameter list to a
   footnote or to the reproducibility package. ≈ −1 page.
8. Trim the Introduction from 6 paragraphs to 4. ≈ −0.8 page.

Applying items 1–5 alone should land the paper near 15–16 pages; 1–7 comfortably
inside 12–15.

## Second review pass (31 Jul 2026) — data-vs-manuscript audit

Every number in Tables 1–3 and the ablation prose was re-checked line by line against
`source_data/`. **All reverse and serial figures verify exactly** against
`paper_table_main.csv`; cover/token figures verify against `run_summary.json`,
`token_summary.csv` and `paper_numbers_overview.json`; cross-dataset and robustness
averages recompute correctly from `robustness_metrics.csv` (Identity avg 0.360206,
Crop-80% avg 0.361672 → Δ +0.0015; Serial-2 +0.0114; Serial-3 +0.0104; per-dataset
PSNR avg 39.9675 → 39.97). Ablation deltas recompute from `ablation.csv`
(41.37074 − 35.61185 = 5.75889 → +5.76 dB). No fabricated numbers found.

### Fixed in this pass

| Issue | Status |
|---|---|
| **Parameter-count overclaim.** `metrics.json` shows `trainable_params: 228435` with `image_size: 192`, `device: cpu` — i.e. 228 k is the **CPU/192 smoke config** (h=48, d_tok=24), *not* the 256×256 h=128 model that produces the headline 39.61 dB. Abstract and Intro attributed 228 k to the benchmark model. | Qualified in abstract + intro |
| **"Validation score decreases monotonically."** False — the log reverses at epochs 3, 8, 10, 12, 24, 25 etc., and Fig. 5(a) visibly zig-zags. Fig. 5 caption also said "without regression". | Reworded to "5.68 → 3.55 with epoch-to-epoch fluctuation" |
| **Baseline-guard description wrong twice.** `run_summary.json` has `baseline_guard_epoch: 1000000000` and `target_val_score: null` → guard never fired. Also `training_protocol.py` shows it `break`s (early stop), not "falls back to the best checkpoint". | Restated as available-but-disabled |
| **Future-pass phase wrong.** Paper said the sampler is enabled only in SOTA-refine at p_f=0.005. Log shows p_f=0.002/w_f=0.002 already active in robust-push (ep. 16–28), rising to 0.005/0.04 in sota-refine. | Both rates now stated; Alg. 1 uses p_f(e) |
| **Baseline-PSNR claim inconsistent 3 ways:** abstract "sub-38 dB", intro "seldom exceeding 35 dB", experiments "33–36 dB". | Harmonised to 33–36 dB |
| **`Cover L2 = 1.10×10⁻⁴ ± 0.00×10⁻⁴`** implies zero variance (artefact of the source being rounded to 4 dp; PSNR std 0.3532 dB proves it is nonzero). | ± dropped, mean only |
| **Table 6 showed 8 of 11 attacks** with no indication it was a subset, while abstract/text claim "11 attacks". | Caption now says "representative subset"; points to Fig. 4b |
| Crop-80% Δ printed as `+0.001` in Table 6 but `+0.0015` in the text. | Table now `+0.0015` |
| σ_eval = 1.36 sits **outside** the training range [1.02, 1.30] with no comment. | Extrapolation now acknowledged as the conservative direction |
| Serial table silently dropped the `token_rbn` rows (whose SSIM is worse than naive) while the note mentioned only `blend_*`. | Note now discloses both |

### Also fixed — LaTeX structural defects

Static integrity check passed on: all 33 `\ref` resolve, 27 `\cite` ↔ 27 `\bibitem`
match both directions, all environments balanced, all 5 `\includegraphics` paths exist,
no duplicate labels, every `\label` correctly placed after its `\caption`, all tabular
column counts correct, and no IEEEtran / fancyhdr / Vietnamese / TODO remnants.

Defects found and repaired:

- **Backwards equation range** in Alg. 1: `Eqs.~(\ref{eq:cap})--(\ref{eq:embed})`
  rendered as "Eqs. (8)--(7)". Reordered to `(\ref{eq:freq})--(\ref{eq:cap})`.
- **Hard-coded "Section 2"** in the SOTA paragraph. Added `\label{sec:relwork}` and a
  proper `\ref` so it cannot silently rot.
- **Apparent 50-vs-60 epoch contradiction** between the ablation and the CPU smoke run.
  These are genuinely different runs on the same configuration (`ablation.csv`
  logs ~13–14 s each vs 15.708 s for the 60-epoch smoke run) — reworded so it no
  longer reads as a contradiction.
- **Worst overfull box (46.4 pt ≈ 1.6 cm into the margin)** caused by the
  unhyphenatable `ConvBlock$+$ResidualBlock`. Rephrased.
- **20.2 pt overfull** from the underscored AdaIN style filenames. Added `\allowbreak`
  at each underscore.
- **Tables 2 and 3 were wider than `\textwidth`** (17.8 pt / 18.7 pt overfull): both
  set `\scriptsize` and then immediately overrode it with `\footnotesize`. Removed the
  stray `\footnotesize` and tightened `\tabcolsep`.
- **Mixed decimal precision** in Table 6's Δ column (`-0.000` signed zeros beside
  `+0.0015`). Now uniform 4 dp, recomputed from `robustness_metrics.csv`.

## Third pass (31 Jul 2026) — read `model_definition.py` + `training_protocol.py` + `followup_results/`

This pass found the two most serious problems in the manuscript. Both are now fixed.

### 🔴 The parameter count was wrong by ~47×

`metrics.json` reports `trainable_params: 228435`, and the paper repeated "228 k
parameters" in the abstract, introduction, cost paragraph and conclusion. Counting the
architecture in `model_definition.py` analytically (verified twice, independently):

| Module | Parameters |
|---|---|
| HybridTokenizer | 940,867 |
| StegoEncoder | 980,742 |
| StegoDecoder | 823,875 |
| ReverseDecoder (incl. nested TokenPriorDecoder 1,705,731) | 7,931,911 |
| **Total (VGG-19 excluded, it is frozen)** | **10,677,395** |

The three "jointly trained" modules alone are **2,745,484** — already 12× the claimed
figure. 228 k cannot describe the architecture the Method section describes. All four
claims are rewritten to the honest framing, which is still favourable: **the embedding
path (tokenizer + encoder) is only 1.9 M of 10.7 M**, so the sender side is cheap and
the heavy reverse decoder sits with the receiver.

### 🔴 `ModelConfig` capacity fields are dead code — the "small CPU variant" does not exist

`hidden_channels`, `token_channels` and `token_size` appear **only** in the dataclass
declaration (line 47). Every width and the 32×32 token grid are hard-coded literals:
`ConvBlock(3,64,stride=2)...ResidualBlock(128)` (l. 69), `adaptive_avg_pool2d(...,(32,32))`
(l. 73, 104), `fused = 3+64+3+2+3 # 75` (l. 84), `ConvBlock(67,128)` (l. 110),
`inc = 3+3+3+64+2+2+3 # 80` (l. 126), `ConvBlock(512,128)` / `ConvBlock(320,128)` (l. 131–132).

So instantiating with `hidden_channels=48, token_channels=24, token_size=24` silently
returns a **byte-identical 10.7 M model**. The paper's claims that the CPU run used
"h=48, d_tok=g_tok=24" and that the token is "g_tok=d_tok=24 at 192×192" are therefore
not achievable in this code. Corrected to: same architecture throughout, only the input
resolution differs (256 vs 192). ⚠ **If any table was produced by a sweep over those
three fields, that ablation measured seed noise, not capacity.** The reported ablation
sweeps ceiling/freq-loss on/off, which is unaffected.

### 🔴 Completed steganalysis showing the method IS detectable was omitted

`followup_results/` contains finished experiments on the same 600 pairs (1,200 images),
with a sound protocol (StratifiedGroupKFold keeping each pair's cover and stego in the
same fold, so no pair leakage):

| Detector | Pooled ROC-AUC | Balanced acc. |
|---|---|---|
| Full SRM (34,671 feats, logistic regression) | 0.848 | 0.768 |
| XuNet-lite | 0.905 | 0.783 |
| SRNet-tiny | 0.779 | 0.708 |

Chance is 0.5, so the stego images **are** detectable. The Discussion previously said
steganalysis was "future work ... beyond the scope of this paper" and argued the residual
is "highly localised ... and the cover PSNR is high" — which reads as an implicit
undetectability argument while contradicting data already in the repo. Your own
`README.md` says: *"already show above-chance detectability, so do not make security
claims."* I rewrote the paragraph to report all three numbers, state plainly that no
undetectability claim is made, note the neural probes are reduced local implementations
(lower bound, not exact), and name this as the paper's principal limitation. This is
both more honest and much safer under review.

### Also fixed from the source read

- **Payload semantics.** `payload_capacity_256.json` warns the payload is a lossy latent,
  "not guaranteed lossless capacity", and "the receiver needs the trained checkpoint".
  The paper never gave a bpp figure — a glaring omission for a steganography venue. Added
  33.5 bpp (FP32) / 8.375 bpp (uint8), plus explicit scoping to self-contained
  stylisation rather than keyless bitstream steganography.
- **GPU timings at the real benchmark resolution.** `gpu_runtime_256_summary.json` has
  256×256 numbers (0.0223 s end-to-end; reverse decoder 0.0124 s dominates) that were
  unused while the paper quoted only CPU/192 figures. Added — it also substantiates the
  "embedding is cheap, recovery is expensive" split.
- **Reproducibility items from the run's own `revision_notes.md`.** Item 5 (full COCO
  val2017 downloaded, shuffled with SEED=42, then subsampled to 420) and item 4 (training
  is **not** from scratch — `resume_training: true` from `colab_style_stego_benchmark_v4_serial_aware`)
  were both unstated. Added, including the caveat that exact reproduction needs that
  warm-start checkpoint.
- **Cross-dataset probe size.** No sample size was given; `cross_dataset_metrics.csv` has
  only 5 images per dataset. Reframed as a consistency check, not a generalisation guarantee.
- **Texture gate description.** Paper said "Sobel+DWT local-variance map"; the code
  (`texture_attention`) uses mean *absolute* Sobel plus 0.5× mean absolute high Haar
  sub-bands, max-normalised and clamped. Corrected.
- **DWT cost justification was self-contradictory.** The paper justified the pooling proxy
  as "markedly cheaper than a full DWT at every step", but `haar_dwt2` computes an exact
  DWT every step anyway for the texture gate. Rejustified on the correct grounds
  (the proxy returns the low band already at input resolution).

### Final consistency sweep

- `"228"` no longer appears anywhere in the file.
- `"cover-PSNR standard deviation stays below 0.35 dB"` was false against its own table
  (0.3532). Corrected.
- `"token MSE varies by less than 1e-4"` → the spread is *exactly* 1e-4 (0.0133/0.0133/0.0132).
  Changed to "at most".
- The intro attributed `0.069 s` to the whole embedding path, but that is the stego encoder
  alone and no CPU tokenizer timing exists. Now quotes the GPU embedding path (0.0096 s).
- GPU component timings now marked "approximately" (rounded components sum to 0.0224 vs a
  0.0223 total).
- Hyphenation was inconsistent between the abstract/conclusion (`frequency guided`,
  `self contained`, `cross dataset`) and the title/body (`frequency-guided`,
  `self-contained`, `cross-dataset`). Unified.
- Fixed a comma splice in the introduction.
- Verified clean: 35 `\ref` all resolve, 27 `\cite` ↔ 27 `\bibitem` exact, 36 `\begin` /
  36 `\end` balanced, all braces balanced in footnotes/captions, no raw underscore outside
  math, no odd `$` counts, no duplicated words.
- Conclusion now also carries the no-undetectability statement, so the limitation is
  visible to anyone who reads only the abstract and conclusion.

## Fourth pass (31 Jul 2026) — σ_eval resolved from the data

### ✅ σ_eval is 1.24, not 1.36 — corrected throughout

This was previously listed as needing your decision. `followup_results/checkpoint_ablation_600_summary.json`
settles it. Its `V8 full` row (`run: colab_style_stego_paper_repair_v8_coco_full`,
`best_epoch: 39` — i.e. exactly the reported checkpoint) records:

| Quantity | σ=1.24 run | Paper |
|---|---|---|
| `cover_psnr_mean` | 39.60695 ± 0.34941 | 39.6074 ± 0.3532 |
| `token_mse_mean` | 0.0133110 | 0.0133 |
| `reverse_l2_mean` | 0.0021855 | 0.0022 |
| `reverse_psnr_mean` | 27.4407 | 27.46 |

Every headline number matches the σ=1.24 measurement. Independently confirmed by
`gpu_runtime_256_summary.json` (also `eval_strength: 1.24`, cover PSNR 39.60695).

The arithmetic corroborates it. Since the residual scales as $\alpha\sigma MR$, cover MSE
scales as $\sigma^2$. The reported PSNR of 39.6074 dB implies MSE $=1.094\times10^{-4}$;
at σ=1.36 that would become $1.094\times10^{-4}\times(1.36/1.24)^2 = 1.317\times10^{-4}$,
i.e. **38.8 dB**. And indeed the training log's held-out cover error at
`val_strength: 1.36` is $1.348\times10^{-4}$ → 38.70 dB, about 0.9 dB below the reported
figure. So 1.36 is the *checkpoint-selection* strength and 1.24 is the *reporting*
strength — two different quantities the manuscript had conflated.

Fixed in five places (Eq. 3 line, attack-channel paragraph, Table 1 caption, Table 2
caption, §4.2 prose). **This also reverses an edit I made in the previous pass**: I had
added a sentence justifying σ_eval=1.36 as "conservative extrapolation" above the training
range. At 1.24 the value sits *inside* [1.02, 1.30], so that justification was wrong and
has been replaced with an accurate description of the two strengths.

### ⚠ New issue found: the checkpoint ablation is confounded

`checkpoint_ablation_600_summary.json` is a developmental comparison across seven
checkpoints, and on its face it is a strong result (reverse L2 0.0085–0.0099 → 0.0022, a
4× gain; cover PSNR 32.7 → 39.6). Your `README.md` cites it. **Do not put it in the paper
as it stands** — `eval_strength` differs per row:

| Checkpoint | eval σ | Cover PSNR | Reverse L2 |
|---|---|---|---|
| V3 baseline | 1.24 | 32.66 | 0.0099 |
| V4 serial-aware | 1.24 | 32.05 | 0.0085 |
| V7.1 capacity | **1.32** | 30.51 | 0.0091 |
| V7.2 capacity window | **1.36** | 31.02 | 0.0093 |
| V7.3 frequency | **1.56** | 29.83 | 0.0099 |
| V7.4 full pre-repair | **1.36** | 38.95 | 0.0099 |
| V8 full (ours) | 1.24 | 39.61 | 0.0022 |

Because cover MSE grows as σ², the rows evaluated at 1.32–1.56 are penalised relative to
ours at 1.24 — V7.3 at σ=1.56 is carrying a ~2 dB handicap from the strength setting
alone. Re-running every checkpoint at a single σ would turn this into a publishable
ablation; as logged it is not a controlled comparison.

### Steganalysis figures double-checked

The numbers I inserted are the *full* SRM (`feature_dim: 34671`, pooled ROC-AUC 0.8480,
balanced acc. 0.7675), per your README's instruction to prefer it over SRM-lite. For the
record, SRM-lite gives 0.7722 with the caveat "not a full canonical SRM implementation" —
correctly not used. XuNet-lite 0.9053/0.7825 and SRNet-tiny 0.7792/0.7083 both verified
against `neural_steganalysis_summary.json`. The conclusion's stated range 0.78–0.91 covers
all three.

## Fifth pass (31 Jul 2026) — coherence audit after the earlier edits

A full re-read caught contradictions *introduced or left behind* by the earlier passes.
The first one was mine.

- 🔴 **The ablation section still described the non-existent small model.** It read "the same
  lightweight CPU configuration ($h=48$, $d_{\text{tok}}=g_{\text{tok}}=24$)" — exactly the
  claim I had removed from three other sections, so the paper contradicted itself in three
  places at once (h=48 vs h=128 "at both resolutions"; d_tok=24 vs "64 throughout"; and
  "the same lightweight configuration" referred to nothing previously defined). Now states
  the reduced $192\times192$ resolution with the same architecture.
- **The reverse decoder was missing from the module inventory.** §3.1 said "four modules ...
  the first three are trained jointly", counting the non-learnable attack channel as a module
  while omitting $f_{\text{rev}}$ — which is learnable, is trained, and supplies 7.93 M of the
  10.7 M parameters I had just added. Now: four learnable modules plus the attack channel.
- **"Up to three subsequent re-stylisations" overstated the evidence** in the abstract and
  §4.5. Table 3 covers serial-2 (one extra pass) and serial-3 (two extra passes), and §3.8
  correctly said "one or two". Reworded to two further passes / three cumulative passes.
- **Unsupported per-style claim removed.** "$\sim40\pm0.6$ dB across all five styles" had no
  backing file and duplicated the per-*dataset* range. Replaced with an argument that is
  actually provable from Table 1: the 600 pairs already span all five styles, so the 0.35 dB
  PSNR standard deviation bounds across-style variation.
- **Cross-dataset PSNR range excluded its own table value** ("39.4–40.6 dB" while BOSSBase is
  39.37). Fixed.
- **Cross-dataset MSE columns now at 4 dp** so the column re-adds correctly (rounded to 3 dp
  the MSE(JP) column summed to 0.359 against a tabulated 0.360) and so Identity agrees with
  Table 6 at 0.3602.
- **Abstract claimed "under 0.08 s on a single CPU thread" for the embedding path** — but no
  CPU tokenizer timing exists, so only the 0.069 s encoder figure is measured. Now quotes the
  measured GPU embedding path (<0.01 s).
- **Conclusion quoted 0.8136 reverse SSIM unqualified** — that is the *oracle* row, which
  reads ground-truth tokens and is not achievable end-to-end. Now 0.8070 clean, with the
  oracle figure in parentheses.
- **Contribution (v) never mentioned the steganalysis study** that the Discussion calls the
  paper's principal limitation, and still said "a CPU inference budget" when the primary
  timing result is now GPU. Both corrected.
- Smaller fixes: "five auxiliary feature maps" miscounted the cover as auxiliary (four);
  "four-stage" CNN branch enumerated only three strided blocks; "sole source of the inference
  timings" was false once GPU timings were added; token dimensions written
  $32\times32\times64$ in the abstract/conclusion but $\mathbb{R}^{64\times32\times32}$ in the
  body (unified); Table 1's caption promised "mean ± std" while the L2 row had none (row
  relabelled Cover MSE, caption explains).

### Sixth pass — last three contradictions closed

- **50 vs 60 epochs.** §4.1 had claimed the 60-epoch CPU smoke run was also the source of the
  50-epoch loss ablation. They are different runs: `ablation.csv` logs 12.99–13.87 s per
  configuration, and `inference_timings.csv` gives 15.708 s for 60 epochs (≈0.262 s/epoch),
  so ≈13 s corresponds to 50 epochs. The smoke run is now credited only with the CPU timings.
- **Attack channel at test time.** §3.1 said the channel "samples a single stochastic mode at
  test time", but Tables 1 and 2 score every pair under all three modes. Corrected to
  enumerated in both regimes.
- **Algorithm 1 omitted $f_{\text{rev}}$** from its `\Require` and initialisation lines, which
  contradicted the corrected module inventory. Added.

Verification after these edits: 37 `\ref` all resolve, 27 `\cite` ↔ 27 `\bibitem` bijective,
36 `\begin`/`\end` balanced, braces balanced in all footnotes and captions, no raw underscore
outside math, even `$` parity on every line, no duplicated words or truncated sentences. The
prose-only ablation section is self-contained and its numbers are internally consistent
(10^−4.137 = 0.73×10⁻⁴, 10^−3.561 = 2.75×10⁻⁴).

### ⚠ Needs your decision — I could not resolve these

1. **The validation-score formula does not reproduce the logged values.** The paper
   stated $V = 0.45V_{\text{clean}} + 0.20V_{\text{rbn}} + 0.20V_{\text{jpeg}} +
   0.075V_{\text{ser2}} + 0.075V_{\text{ser3}} + 1.0$. Plugging in epoch 39
   (0.58293, 0.65911, 0.66216, 0.69831, 0.69847) gives **1.631**, but the log
   records `val_score: 3.549464` — and the paper quotes $V^\star = 3.549$. Epoch 1
   gives 2.07 vs logged 5.684. The weights are not recoverable from
   `training_protocol.py` or `model_definition.py`. **I replaced the explicit
   formula with a qualitative description** so the manuscript is not stating
   something checkably false — but if you want the equation back, recover the real
   weights from the training notebook first. A reviewer who tries to verify
   $V^\star$ from Fig. 5(a) would otherwise catch this.
2. **Confirm the parameter counts** by running
   `sum(p.numel() for p in BenchmarkSystemV7(ModelConfig()).parameters() if p.requires_grad)`
   — I expect exactly **10,677,395**, and per-module 940,867 / 980,742 / 823,875 / 7,931,911.
   Also worth finding out what `metrics.json`'s `228435` actually refers to, since it does
   not match this architecture; it may be inherited from an older, genuinely smaller model.
3. **PDF size 11.4 MB.** `ISDS2026_FGSS_compact.tex` points at `paper_assets/`, not
   the compressed set mentioned in `README.md`. EasyChair upload caps are often
   10 MB — check before you rely on the current build.
4. ~~σ_eval ambiguous~~ — **resolved above, corrected to 1.24.**
5. **Two conflicting cross-dataset sources.** `source_data/cross_dataset_metrics.csv`
   gives per-image PSNR of 38.3–39.3 dB (dataset means ≈38.5–38.8) and Token MSE ≈0.013,
   while `robustness_metrics.csv` — the file the paper actually cites — gives 39.37–40.57 dB
   and Token MSE ≈0.36. The manuscript uses the **more favourable** PSNR set. Your
   `README.md` already flags this as open ("Recheck cross-dataset token-MSE scale"). Decide
   which pipeline is authoritative before submitting; if a reviewer is given the repo, the
   discrepancy is visible. This also determines whether the Table 5/6 footnote is the right
   explanation.
7. **41 vs 60 epochs.** `training_protocol.py` sets `STEGO_EPOCHS = 60` with
   `MIN_EPOCHS = 30`, `EARLY_STOPPING_PATIENCE = 10`, yet the history stops at 41 with the
   best at 39. Early stopping does not obviously explain halting at 41 (best 39 + patience 10
   → 49). If the run was truncated (Colab session limit), say so, or the reader will assume
   the schedule completed as designed.
5. **Serial rows in Table 6 use a different baseline population from the other rows.**
   In `robustness_metrics.csv` the Serial-2/Serial-3 rows are COCO-only
   (`Dataset=COCO`, `CoverPSNR=0`), whereas Identity/JPEG/Gaussian/Resize/Median/Crop
   are averages over all four datasets. The reported Δ of +0.0114 / +0.0104 therefore
   compares a COCO-only value against a 4-dataset mean. Measured within COCO
   (Identity 0.3735) the serial drift is *negative*. This makes the published number
   conservative rather than inflated, so I added a dagger footnote disclosing it
   instead of restating the claim — but if you can rerun the serial attacks across all
   four datasets, that would remove the asymmetry cleanly. Note this also underpins
   Fig. 4(b)'s shaded band and the conclusion's "below 0.012 under serial
   re-stylisation".

## Pre-submission checklist

- [ ] **Deadline risk (31 Jul 2026 check):** the official page (isds.ctu.edu.vn/2026)
      still lists **30-July-2026** as the submission deadline, with no extension
      posted. Confirm current status directly on EasyChair
      (<https://easychair.org/conferences/?conf=isds2026>) before anything else —
      submit immediately if the system still accepts papers.
- [ ] Compiles clean, 12–15 pages, A4 — **not yet reverified**. 31-Jul build of
      `ISDS2026_FGSS_compact.tex` was 18 pages. Applied further cuts (Introduction
      4→3 paragraphs, `tab:ablation` dropped in favour of prose, loss
      hyper-parameter list moved to a footnote, SOTA/cost paragraphs tightened).
      **No LaTeX engine was available in this session to recompile** — run
      `pdflatex -interaction=nonstopmode ISDS2026_FGSS_compact.tex` (x2) locally and
      confirm the final page count; more cuts are ready to apply if still over 15.
- [ ] No `Overfull \hbox` warnings > 5 pt (minor overfull boxes present in the
      31-Jul build, mostly sub-20pt; none produced visible text-in-margin overflow
      on visual inspection of all 18 pages)
- [ ] Text-extraction/ligature fix: `\usepackage{cmap}` added to the preamble
      (before `fontenc`) so copy-pasting/searching text with "fi/fl/ffi" ligatures
      from the PDF does not produce garbled characters — a common LaTeX+CM
      "font error" for reviewers who copy text out of the PDF. Visual rendering of
      all 18 pages was inspected directly and showed no corrupted glyphs, boxes, or
      leftover Vietnamese/IEEE remnants.
- [ ] Anonymity: ISDS 2026 does **not** state double-blind review — author block kept visible. Re-check the EasyChair page before uploading.
- [ ] Track selected in EasyChair: **Track 3 — Image Processing & Pattern Recognition**
- [ ] Abstract + keywords pasted into EasyChair matching the PDF
- [ ] Numbers in tables still match `source_data/` (run `python audit_paper.py`)
- [ ] Claim hygiene: the phrase "highest reported in the style-transfer literature"
      was softened to "high relative to the style-transfer literature" (the local
      SRM / XuNet-lite / SRNet-tiny probes show above-chance detectability, so no
      undetectability or SOTA-security claim is made)
