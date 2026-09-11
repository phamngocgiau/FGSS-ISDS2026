"""Shrink the oversized figure assets so the submission PDF fits a 10 MB cap.

The two grid images dominate the PDF. From the build log they are ~2382x2455 px
but are typeset at only ~160 pt wide (~2.2 in), so even 900 px is over 300 dpi
at the printed size. figure1_architecture.png and training_curve.png are also
larger than needed.

Originals are copied to paper_assets_fullres/ first - nothing is destroyed.

Usage:  python shrink_assets.py            # shrink
        python shrink_assets.py --restore  # put the originals back
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "paper_assets"
BACKUP = ROOT / "paper_assets_fullres"

# filename -> max width in pixels
TARGETS = {
    "qualitative_grid.jpg": 1000,
    "freq_decomp.jpg": 1000,
    "figure1_architecture.png": 1600,
    "training_curve.png": 1400,
    "robustness_overview.png": 1400,
}


def human(n):
    return f"{n / 1024 / 1024:.2f} MB" if n >= 1024 * 1024 else f"{n / 1024:.0f} KB"


def restore():
    if not BACKUP.is_dir():
        print(f"No backup at {BACKUP} - nothing to restore.")
        return
    if not SRC.is_dir():
        print(f"Not found: {SRC} - cannot restore into a missing folder.")
        return
    n = 0
    for f in BACKUP.iterdir():
        if f.is_file():
            shutil.copy2(f, SRC / f.name)
            n += 1
    print(f"Restored {n} original file(s) into {SRC}.")


def main():
    if "--restore" in sys.argv:
        restore()
        return

    try:
        from PIL import Image
    except ImportError:
        print("Pillow is required:  pip install Pillow")
        print("(or: pip install Pillow --break-system-packages)")
        sys.exit(1)

    if not SRC.is_dir():
        print(f"Not found: {SRC}")
        sys.exit(1)

    BACKUP.mkdir(exist_ok=True)
    before_total = after_total = 0
    print(f"{'file':<32}{'before':>11}{'after':>11}   new size")
    print("-" * 70)

    for name, max_w in TARGETS.items():
        p = SRC / name
        if not p.is_file():
            print(f"{name:<32}{'MISSING':>11}")
            continue

        bak = BACKUP / name
        if not bak.exists():
            shutil.copy2(p, bak)

        # Size of the pristine original, so re-runs report stable numbers.
        before = bak.stat().st_size
        before_total += before

        # always work from the pristine original so re-running is idempotent
        img = Image.open(bak)
        w, h = img.size
        if w > max_w:
            new_h = round(h * max_w / w)
            img = img.resize((max_w, new_h), Image.LANCZOS)
        dims = f"{img.size[0]}x{img.size[1]}"

        if p.suffix.lower() in (".jpg", ".jpeg"):
            img.convert("RGB").save(p, "JPEG", quality=88,
                                    optimize=True, progressive=True)
        else:
            img.save(p, "PNG", optimize=True)

        after = p.stat().st_size
        after_total += after
        print(f"{name:<32}{human(before):>11}{human(after):>11}   {dims}")

    print("-" * 70)
    saved = before_total - after_total
    print(f"{'TOTAL':<32}{human(before_total):>11}{human(after_total):>11}")
    print(f"\nSaved {human(saved)}. Originals kept in {BACKUP.name}/")
    print("Now rebuild:  .\\check_submission.ps1")
    print("To undo:      python shrink_assets.py --restore")


if __name__ == "__main__":
    main()
