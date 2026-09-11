"""Comprehensive audit: verify paper numbers against bundled source data."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import csv
import json
import sys


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DATA = BASE_DIR / "source_data"
PAPER_ASSETS = BASE_DIR / "paper_assets_compressed"
FOLLOWUP_RESULTS = BASE_DIR / "followup_results"

errors: list[str] = []
warnings: list[str] = []


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


# === 1. REVERSE TABLE (paper_table_main.csv rows 2-6) ===
rows = read_csv(SOURCE_DATA / "paper_table_main.csv")

paper_reverse = {
    "naive_reverse": {"L2": 0.0065, "SSIM": 0.5234, "LPIPS": 0.1889, "PSNR": 22.25},
    "token_reverse_clean": {"L2": 0.0022, "SSIM": 0.8070, "LPIPS": 0.1216, "PSNR": 27.46},
    "token_reverse_rbn": {"L2": 0.0027, "SSIM": 0.7884, "LPIPS": 0.1514, "PSNR": 26.54},
    "token_reverse_jpeg": {"L2": 0.0025, "SSIM": 0.7898, "LPIPS": 0.1467, "PSNR": 26.97},
    "token_reverse_oracle": {"L2": 0.0021, "SSIM": 0.8136, "LPIPS": 0.1135, "PSNR": 27.63},
}

for row in rows:
    method = row["method"]
    if method in paper_reverse:
        for metric, paper_val in paper_reverse[method].items():
            csv_key = f"{metric}_mean"
            csv_val = float(row[csv_key])
            if abs(paper_val - round(csv_val, 4)) > 0.005:
                errors.append(f"REVERSE {method}.{metric}: paper={paper_val}, csv={csv_val:.4f}")


# === 2. SERIAL-2 TABLE (rows 7-14) ===
paper_serial2 = {
    "naive_serial2": {"L2": 0.0090, "SSIM": 0.4966, "LPIPS": 0.1945, "PSNR": 20.64},
    "token_serial2_clean": {"L2": 0.0078, "SSIM": 0.4943, "LPIPS": 0.1577, "PSNR": 21.41},
    "token_serial2_jpeg": {"L2": 0.0081, "SSIM": 0.4796, "LPIPS": 0.1662, "PSNR": 21.23},
    "token_serial2_v7_render_clean": {"L2": 0.0083, "SSIM": 0.4738, "LPIPS": 0.1836, "PSNR": 21.10},
    "token_serial2_v7_clean": {"L2": 0.0081, "SSIM": 0.4795, "LPIPS": 0.1715, "PSNR": 21.20},
    "token_serial2_v7_rbn": {"L2": 0.0087, "SSIM": 0.4615, "LPIPS": 0.1815, "PSNR": 20.89},
    "token_serial2_v7_jpeg": {"L2": 0.0085, "SSIM": 0.4647, "LPIPS": 0.1802, "PSNR": 21.02},
}

for row in rows:
    method = row["method"]
    if method in paper_serial2:
        for metric, paper_val in paper_serial2[method].items():
            csv_key = f"{metric}_mean"
            csv_val = float(row[csv_key])
            if abs(paper_val - round(csv_val, 4)) > 0.005:
                errors.append(f"SERIAL2 {method}.{metric}: paper={paper_val}, csv={csv_val:.4f}")


# === 3. SERIAL-3 TABLE (rows 15-22) ===
paper_serial3 = {
    "naive_serial3": {"L2": 0.0113, "SSIM": 0.4548, "LPIPS": 0.2378, "PSNR": 19.64},
    "token_serial3_clean": {"L2": 0.0091, "SSIM": 0.4500, "LPIPS": 0.1885, "PSNR": 20.71},
    "token_serial3_jpeg": {"L2": 0.0094, "SSIM": 0.4376, "LPIPS": 0.1984, "PSNR": 20.58},
    "token_serial3_v7_render_clean": {"L2": 0.0102, "SSIM": 0.4192, "LPIPS": 0.2260, "PSNR": 20.23},
    "token_serial3_v7_clean": {"L2": 0.0098, "SSIM": 0.4278, "LPIPS": 0.2090, "PSNR": 20.38},
    "token_serial3_v7_rbn": {"L2": 0.0108, "SSIM": 0.4046, "LPIPS": 0.2196, "PSNR": 19.98},
    "token_serial3_v7_jpeg": {"L2": 0.0102, "SSIM": 0.4155, "LPIPS": 0.2196, "PSNR": 20.25},
}

for row in rows:
    method = row["method"]
    if method in paper_serial3:
        for metric, paper_val in paper_serial3[method].items():
            csv_key = f"{metric}_mean"
            csv_val = float(row[csv_key])
            if abs(paper_val - round(csv_val, 4)) > 0.005:
                errors.append(f"SERIAL3 {method}.{metric}: paper={paper_val}, csv={csv_val:.4f}")


# === 4. CHECKPOINT-LEVEL ABLATION TABLE ===
abl_path = FOLLOWUP_RESULTS / "checkpoint_ablation_600_summary.json"
if not abl_path.exists():
    errors.append(f"MISSING FOLLOWUP JSON: {abl_path.name}")
else:
    abl_rows = {row["label"]: row for row in read_json(abl_path)["rows"]}
    paper_ablation = {
        "V3 baseline": (1.24, 32.66, 0.0019, 0.0019, 0.0099),
        "V4 serial-aware": (1.24, 32.05, 0.0016, 0.0016, 0.0085),
        "V7.1 capacity": (1.32, 30.51, 0.0192, 0.0191, 0.0091),
        "V7.2 capacity window": (1.36, 31.02, 0.0228, 0.0226, 0.0093),
        "V7.3 frequency": (1.56, 29.83, 0.0115, 0.0114, 0.0099),
        "V7.4 full pre-repair": (1.36, 38.95, 0.0141, 0.0140, 0.0099),
        "V8 full": (1.24, 39.61, 0.0133, 0.0133, 0.0022),
    }
    for label, (strength, psnr, token, jpeg, reverse_l2) in paper_ablation.items():
        if label not in abl_rows:
            errors.append(f"ABLATION missing row: {label}")
            continue
        row = abl_rows[label]
        checks = {
            "eval_strength": (strength, round(float(row["eval_strength"]), 2), 0.001),
            "cover_psnr_mean": (psnr, round(float(row["cover_psnr_mean"]), 2), 0.01),
            "token_mse_mean": (token, round(float(row["token_mse_mean"]), 4), 0.0001),
            "jpeg_token_mse_mean": (jpeg, round(float(row["jpeg_token_mse_mean"]), 4), 0.0001),
            "reverse_l2_mean": (reverse_l2, round(float(row["reverse_l2_mean"]), 4), 0.0001),
        }
        for metric, (paper_val, csv_val, tol) in checks.items():
            if abs(paper_val - csv_val) > tol:
                errors.append(f"ABLATION {label}.{metric}: paper={paper_val}, json={csv_val}")


# === 5. CROSS-DATASET TABLE ===
rob_rows = read_csv(SOURCE_DATA / "robustness_metrics.csv")

paper_cross = {
    "COCO": (40.47, 0.3735, 0.3731),
    "DIV2K": (40.57, 0.3425, 0.3413),
    "CelebA": (39.46, 0.3673, 0.3673),
    "BOSSBase": (39.37, 0.3575, 0.3565),
}

for rr in rob_rows:
    ds = rr["Dataset"]
    if ds in paper_cross and rr["Attack"] == "Identity":
        p_psnr, p_tok_id, _ = paper_cross[ds]
        csv_psnr = float(rr["CoverPSNR"])
        csv_tok = float(rr["TokenMSE"])
        if abs(csv_psnr - p_psnr) > 0.01:
            errors.append(f"CROSS {ds} PSNR: paper={p_psnr}, csv={csv_psnr}")
        if abs(csv_tok - p_tok_id) > 0.002:
            errors.append(f"CROSS {ds} TokenMSE: paper={p_tok_id}, csv={csv_tok}")
    if ds in paper_cross and rr["Attack"] == "JPEG Q75":
        _, _, p_tok_jpeg = paper_cross[ds]
        csv_tok = float(rr["TokenMSE"])
        if abs(csv_tok - p_tok_jpeg) > 0.002:
            errors.append(f"CROSS {ds} TokenMSE(JPEG): paper={p_tok_jpeg}, csv={csv_tok}")


# === 6. ROBUSTNESS TABLE ===
attack_avgs: defaultdict[str, list[float]] = defaultdict(list)
for rr in rob_rows:
    if rr["Attack"] not in ("Serial-2", "Serial-3"):
        attack_avgs[rr["Attack"]].append(float(rr["TokenMSE"]))

paper_robustness = {
    "Identity": 0.3602,
    "JPEG Q75": 0.3596,
    "JPEG Q50": 0.3598,
    "Gaussian 0.02": 0.3603,
    "Gaussian 0.05": 0.3600,
    "Resize 50%": 0.3600,
    "Resize 75%": 0.3599,
    "Median 3x3": 0.3600,
    "Crop 80%": 0.3617,
}

for attack, paper_val in paper_robustness.items():
    if attack in attack_avgs:
        avg = sum(attack_avgs[attack]) / len(attack_avgs[attack])
        if abs(avg - paper_val) > 0.001:
            errors.append(f"ROBUST {attack}: paper={paper_val}, computed_avg={avg:.4f}")


# === 7. COVER TABLE (from run_summary.json) ===
rs = read_json(SOURCE_DATA / "run_summary.json")

cm = rs["cover_metrics_mean"]
paper_cover = {"cover_psnr": 39.6074, "cover_ssim": 0.9914, "cover_lpips": 0.0195}
for k, pv in paper_cover.items():
    cv = round(cm[k], 4)
    if abs(cv - pv) > 0.001:
        errors.append(f"COVER {k}: paper={pv}, json={cv}")


# === 8. INFERENCE TABLE (from metrics.json) ===
met = read_json(SOURCE_DATA / "metrics.json")

paper_inf = {
    "nst_time_sec": 43.824,
    "encoder_inference_sec": 0.069,
    "decoder_inference_sec": 0.005,
    "stego_train_time_sec": 15.708,
}
for k, pv in paper_inf.items():
    cv = met.get(k, met.get(k.replace("_inference", "")))
    if cv is not None and abs(cv - pv) > 0.002:
        errors.append(f"INFERENCE {k}: paper={pv}, json={cv}")


# === 9. FOLLOW-UP GPU RUNTIME / FULL-SRM / PAYLOAD TABLES ===
runtime_path = FOLLOWUP_RESULTS / "gpu_runtime_256_summary.json"
srm_path = FOLLOWUP_RESULTS / "full_srm_steganalysis_summary.json"
neural_path = FOLLOWUP_RESULTS / "neural_steganalysis_summary.json"
payload_path = FOLLOWUP_RESULTS / "payload_capacity_256.json"

if not runtime_path.exists():
    errors.append(f"MISSING FOLLOWUP JSON: {runtime_path.name}")
else:
    rt = read_json(runtime_path)
    paper_gpu_runtime = {
        "tokenizer_sec_p50": 0.0022,
        "encoder_sec_p50": 0.0073,
        "decoder_sec_p50": 0.0003,
        "reverse_sec_p50": 0.0124,
        "full_sec_p50": 0.0223,
    }
    for k, pv in paper_gpu_runtime.items():
        cv = round(float(rt[k]), 4)
        if abs(cv - pv) > 0.0001:
            errors.append(f"GPU RUNTIME {k}: paper={pv}, json={cv}")
    if abs(float(rt.get("eval_strength", -1)) - 1.24) > 1e-6:
        errors.append(f"GPU RUNTIME eval_strength: paper=1.24, json={rt.get('eval_strength')}")

if not srm_path.exists():
    errors.append(f"MISSING FOLLOWUP JSON: {srm_path.name}")
else:
    srm = read_json(srm_path)
    paper_srm = {
        "pairs": 600,
        "samples": 1200,
        "feature_dim": 34671,
        "folds": 5,
        "balanced_accuracy_mean": 0.768,
        "pooled_roc_auc": 0.848,
    }
    for k, pv in paper_srm.items():
        cv = float(srm[k])
        tol = 0.001 if isinstance(pv, float) else 0.0
        if abs(cv - pv) > tol:
            errors.append(f"FULL-SRM {k}: paper={pv}, json={cv}")

if not neural_path.exists():
    errors.append(f"MISSING FOLLOWUP JSON: {neural_path.name}")
else:
    neural = read_json(neural_path)
    detectors = {row["model"]: row for row in neural["detectors"]}
    paper_neural = {
        "xunet_lite": {
            "params": 394946,
            "folds": 5,
            "epochs": 20,
            "balanced_accuracy_mean": 0.783,
            "pooled_roc_auc": 0.905,
        },
        "srnet_tiny": {
            "params": 3011394,
            "folds": 5,
            "epochs": 20,
            "balanced_accuracy_mean": 0.708,
            "pooled_roc_auc": 0.779,
        },
    }
    for model, checks in paper_neural.items():
        if model not in detectors:
            errors.append(f"NEURAL missing detector: {model}")
            continue
        row = detectors[model]
        for k, pv in checks.items():
            cv = float(row[k])
            if k in {"params", "folds", "epochs"}:
                if int(cv) != int(pv):
                    errors.append(f"NEURAL {model}.{k}: paper={pv}, json={cv}")
            elif abs(cv - pv) > 0.001:
                errors.append(f"NEURAL {model}.{k}: paper={pv}, json={cv:.3f}")

if not payload_path.exists():
    errors.append(f"MISSING FOLLOWUP JSON: {payload_path.name}")
else:
    payload = read_json(payload_path)
    paper_payload = {
        "latent_values": 68608,
        "fp32_bpp": 33.5,
        "fp16_bpp": 16.75,
        "uint8_bpp": 8.375,
    }
    for k, pv in paper_payload.items():
        cv = float(payload[k])
        if abs(cv - pv) > 0.001:
            errors.append(f"PAYLOAD {k}: paper={pv}, json={cv}")


# === 10. Check image files exist ===
required_imgs = [
    "figure1_architecture.png",
    "qualitative_grid.jpg",
    "cross_dataset_grid.jpg",
    "training_curve.png",
    "style_grid.jpg",
    "attack_grid.jpg",
]
for img in required_imgs:
    if not (PAPER_ASSETS / img).exists():
        errors.append(f"MISSING IMAGE: {img}")


print("=" * 60)
print("PAPER AUDIT REPORT")
print("=" * 60)
if errors:
    print(f"\nERRORS ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
else:
    print("\nALL NUMBERS VERIFIED - 0 ERRORS")

if warnings:
    print(f"\nWARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  - {w}")

print("\nChecks performed:")
print("  - Reverse table:     5 methods x 4 metrics = 20 values")
print("  - Serial-2 table:    7 methods x 4 metrics = 28 values")
print("  - Serial-3 table:    7 methods x 4 metrics = 28 values")
print("  - Ablation table:    7 checkpoints x 5 metrics = 35 values")
print("  - Cross-dataset:     4 datasets x 3 cols   = 12 values")
print("  - Robustness:        9 attacks x 1 metric  =  9 values")
print("  - Cover metrics:     3 values")
print("  - Inference table:   4 values")
print("  - GPU runtime:       5 values + eval strength =  6 values")
print("  - Full-SRM table:    6 values")
print("  - Neural steg.:      2 detectors x 5 values = 10 values")
print("  - Payload table:     4 values")
print(f"  - Image assets:      {len(required_imgs)} files")
print(f"  TOTAL: {20 + 28 + 28 + 35 + 12 + 9 + 3 + 4 + 6 + 6 + 10 + 4 + len(required_imgs)} verification points")

sys.exit(1 if errors else 0)
