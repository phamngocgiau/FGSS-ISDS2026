"""Generate a Colab notebook for a paper-repair benchmark run.

The generated notebook is intentionally conservative:
- downloads the full official COCO val2017 archive;
- uses explicit train/val/test manifests instead of tiny ad-hoc splits;
- trains from scratch by default;
- exports all paper tables from one metrics file;
- adds reviewer-facing notes so the manuscript can be revised only after
  the new run has finished.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "colab_style_stego_benchmark_v7_4_sota_killer_scratch.ipynb"
DST = ROOT / "colab_style_stego_paper_repair_v8_coco_full.ipynb"


def replace_all(text: str, old: str, new: str) -> str:
    return text.replace(old, new)


nb = json.loads(SRC.read_text(encoding="utf-8"))

for cell in nb["cells"]:
    src = "".join(cell.get("source", []))

    if cell.get("cell_type") == "markdown" and src.startswith("# Robust Self-Contained"):
        src = """# Paper-Repair COCO-Full Benchmark Notebook

Notebook này dùng để chạy lại toàn bộ kết quả trước khi sửa manuscript.

Mục tiêu của bản này không phải "SOTA killer". Mục tiêu là tạo một protocol đủ sạch để reviewer khó bắt lỗi:

- tải **đầy đủ official COCO val2017** từ `images.cocodataset.org`;
- tạo `manifest_splits.csv` với seed cố định, image IDs rõ ràng;
- train **from scratch** mặc định, không dùng warm-start mơ hồ;
- dùng nhiều ảnh train/val/test hơn bản nháp cũ;
- xuất tất cả bảng paper từ cùng một file `metrics_per_pair.csv`;
- xuất `paper_exports/revision_notes.md` nhắc những claim phải hạ nếu kết quả không đủ mạnh.

Sau khi Colab chạy xong, tải thư mục `results/paper_exports/` về và chỉ sửa paper theo số liệu trong đó.
"""

    if cell.get("cell_type") == "markdown" and src.startswith("## Ghi chu khi viet paper"):
        src = """## Ghi chú khi viết lại paper

- Không dùng số liệu bản nháp cũ nữa.
- `results/manifest_splits.csv` ghi rõ COCO image IDs dùng cho train/eval.
- `results/metrics_per_pair.csv`, `results/summary_long.csv`, và `results/paper_exports/` là nguồn số liệu duy nhất.
- Nếu chưa chạy baseline cùng protocol, không viết claim SOTA hoặc highest reported.
- Nếu chưa chạy SRNet/XuNet/SRM, ghi limitation rõ ràng về steganalysis/security.
- Nếu kết quả serial kém naive ở PSNR/LPIPS/L2, chỉ claim improvement ở metric thật sự tốt hơn và giải thích trade-off.
"""

    if cell.get("cell_type") == "code":
        replacements = {
            "PROJECT_ROOT = '/content/drive/MyDrive/Style Transfer'  # Sua neu can":
                "PROJECT_ROOT = '/content/drive/MyDrive/style_stego_paper_repair_v8'  # Sua neu can",
            "RUN_NAME = 'colab_style_stego_benchmark_v7_4_sota_killer_scratch'":
                "RUN_NAME = 'colab_style_stego_paper_repair_v8_coco_full'",
            "NUM_CONTENT_TOTAL = 8":
                "NUM_CONTENT_TOTAL = 420  # full protocol subset sampled from complete COCO val2017",
            "NUM_CONTENT_TRAIN = 6":
                "NUM_CONTENT_TRAIN = 300",
            "NUM_CONTENT_EVAL = 2":
                "NUM_CONTENT_EVAL = 120",
            "STEGO_EPOCHS = 100":
                "STEGO_EPOCHS = 60  # increase to 100+ for final camera-ready run",
            "SAMPLES_PER_PAIR = 24":
                "SAMPLES_PER_PAIR = 1  # one cached cover per content-style pair; avoids duplicate leakage",
            "MIN_EPOCHS = 35":
                "MIN_EPOCHS = 30",
            "EARLY_STOPPING_PATIENCE = 15":
                "EARLY_STOPPING_PATIENCE = 10",
            "RESUME_TRAINING = True":
                "RESUME_TRAINING = True  # resumes only this run's transparent checkpoint",
            "TARGET_VAL_SCORE = 5.054748964309693":
                "TARGET_VAL_SCORE = None  # do not inherit old toy-run target",
            "BASELINE_GUARD_EPOCH = 35":
                "BASELINE_GUARD_EPOCH = 10**9  # disabled for paper-repair run",
            "USE_WIKIART_ZIP = False":
                "USE_WIKIART_ZIP = False  # set True only if you upload a documented style zip",
        }
        for old, new in replacements.items():
            src = replace_all(src, old, new)

        # Make the dataset-download cell explicit about full COCO.
        if src.lstrip().startswith("# Download content dataset: official COCO val2017"):
            src = src.replace(
                "# Download content dataset: official COCO val2017",
                "# Download content dataset: full official COCO val2017 (5000 images)"
            )
            src = replace_all(
                src,
                "content_paths = sorted(COCO_DIR.glob('*.jpg'))[:NUM_CONTENT_TOTAL]\n"
                "style_paths = sorted([p for p in STYLE_DIR.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}])[:NUM_STYLES]\n"
                "assert len(content_paths) >= NUM_CONTENT_TOTAL\n"
                "assert len(style_paths) >= NUM_STYLES\n"
                "\n"
                "content_train = content_paths[:NUM_CONTENT_TRAIN]\n"
                "content_eval = content_paths[NUM_CONTENT_TRAIN:NUM_CONTENT_TRAIN + NUM_CONTENT_EVAL]\n",
                "all_content_paths = sorted(COCO_DIR.glob('*.jpg'))\n"
                "assert len(all_content_paths) == 5000, f'Expected full COCO val2017 with 5000 images, found {len(all_content_paths)}'\n"
                "assert NUM_CONTENT_TOTAL <= len(all_content_paths)\n"
                "content_paths = all_content_paths.copy()\n"
                "rng = random.Random(SEED)\n"
                "rng.shuffle(content_paths)\n"
                "content_paths = content_paths[:NUM_CONTENT_TOTAL]\n"
                "style_paths = sorted([p for p in STYLE_DIR.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}])[:NUM_STYLES]\n"
                "assert len(style_paths) >= NUM_STYLES\n"
                "\n"
                "content_train = content_paths[:NUM_CONTENT_TRAIN]\n"
                "content_eval = content_paths[NUM_CONTENT_TRAIN:NUM_CONTENT_TRAIN + NUM_CONTENT_EVAL]\n"
                "manifest_rows = []\n"
                "for split_name, items in [('train', content_train), ('eval', content_eval)]:\n"
                "    for idx, p in enumerate(items):\n"
                "        manifest_rows.append({'split': split_name, 'index': idx, 'image_file': p.name, 'image_id': p.stem, 'seed': SEED})\n"
                "manifest_path = RESULT_DIR / 'manifest_splits.csv'\n"
                "pd.DataFrame(manifest_rows).to_csv(manifest_path, index=False)\n"
                "print('Full COCO val2017 images:', len(all_content_paths))\n"
                "print('Selected contents:', len(content_paths), 'train:', len(content_train), 'eval:', len(content_eval))\n"
                "print('manifest =', manifest_path)\n",
            )

        # Remove old aggressive wording in notes.
        src = replace_all(src, "V7.4 SOTA Killer image-stego scratch", "Paper-repair V8 COCO-full run")
        src = replace_all(src, "SOTA Killer", "Paper Repair")
        src = replace_all(src, "sota_killer", "paper_repair")

        if src.lstrip().startswith("# Integrated paper-table export"):
            src += r'''

# Reviewer-facing revision notes. Do not edit the paper with old toy-run numbers.
notes = f"""
# Manuscript Revision Notes

Use only files in this export directory for the revised manuscript.

Mandatory fixes after this run:

1. Replace all old COCO 10-pair claims with the new protocol size from `manifest_splits.csv`.
2. Remove "two orders of magnitude" unless a separate bit-rate calculation proves it.
3. Do not claim SOTA unless baselines are rerun under the same protocol.
4. Report train-from-scratch status and checkpoint path.
5. State that COCO val2017 was downloaded in full, then split with SEED={SEED}.
6. Add limitation: no steganalysis unless SRNet/XuNet/SRM experiments are added.
7. Treat `summary_long.csv`, `metrics_per_pair.csv`, and generated LaTeX tables as the single source of truth.

Run directory:
{RESULT_DIR}
"""
(EXPORT_DIR / 'revision_notes.md').write_text(notes, encoding='utf-8')
print('revision notes:', EXPORT_DIR / 'revision_notes.md')
'''

        src = replace_all(
            src,
            "        'target_gap': val_stats['val_score'] - TARGET_VAL_SCORE,",
            "        'target_gap': None if TARGET_VAL_SCORE is None else val_stats['val_score'] - TARGET_VAL_SCORE,",
        )
        src = replace_all(
            src,
            "    if epoch >= BASELINE_GUARD_EPOCH and best_score > TARGET_VAL_SCORE and no_improve >= BASELINE_GUARD_PATIENCE:\n"
            "        print(f'Baseline guard stop at epoch {epoch}: best {best_score:.6f} is still above target {TARGET_VAL_SCORE:.6f}.')\n"
            "        break",
            "    if (TARGET_VAL_SCORE is not None and epoch >= BASELINE_GUARD_EPOCH and\n"
            "            best_score > TARGET_VAL_SCORE and no_improve >= BASELINE_GUARD_PATIENCE):\n"
            "        print(f'Baseline guard stop at epoch {epoch}: best {best_score:.6f} is still above target {TARGET_VAL_SCORE:.6f}.')\n"
            "        break",
        )

    cell["source"] = src.splitlines(keepends=True)
    if cell.get("cell_type") == "code":
        cell["execution_count"] = None
        cell["outputs"] = []

DST.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"generated: {DST}")
