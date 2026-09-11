
# Manuscript Revision Notes

Use only files in this export directory for the revised manuscript.

Mandatory fixes after this run:

1. Replace all old COCO 10-pair claims with the new protocol size from `manifest_splits.csv`.
2. Remove "two orders of magnitude" unless a separate bit-rate calculation proves it.
3. Do not claim SOTA unless baselines are rerun under the same protocol.
4. Report train-from-scratch status and checkpoint path.
5. State that COCO val2017 was downloaded in full, then split with SEED=42.
6. Add limitation: no steganalysis unless SRNet/XuNet/SRM experiments are added.
7. Treat `summary_long.csv`, `metrics_per_pair.csv`, and generated LaTeX tables as the single source of truth.

Run directory:
/content/drive/MyDrive/Style transfrer/style_stego_paper_repair_v8/runs/colab_style_stego_paper_repair_v8_coco_full/results
