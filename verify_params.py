"""Verify the FGSS trainable-parameter count.

Runs two independent checks:
  1. Analytic count from the layer shapes in model_definition.py (no torch needed).
  2. Ground-truth count via torch, if torch is installed.

Usage:  python verify_params.py
"""
import sys
from pathlib import Path

# model_definition.py lives in source_data/ - make it importable standalone.
sys.path.insert(0, str(Path(__file__).resolve().parent / "source_data"))

EXPECTED_TOTAL = 10_677_395
EXPECTED = {
    "HybridTokenizer": 940_867,
    "StegoEncoder": 980_742,
    "StegoDecoder": 823_875,
    "ReverseDecoder": 7_931_911,
}


# ---------- analytic count ----------------------------------------------------
def conv(i, o, k, bias=True):
    return i * o * k * k + (o if bias else 0)


def gn(c):
    return 2 * c


def conv_block(i, o):
    """ConvBlock = Conv2d(i,o,3) + GroupNorm(o) + GELU."""
    return conv(i, o, 3) + gn(o)


def res_block(c):
    """ResidualBlock = 2 x [Conv2d(c,c,3) + GroupNorm(c)]."""
    return 2 * conv(c, c, 3) + 2 * gn(c)


def tokenizer():
    cnn = (conv_block(3, 64) + conv_block(64, 128) + conv_block(128, 128)
           + 2 * res_block(128) + conv(128, 64, 1))
    vgg = conv(256, 128, 1) + conv(128, 64, 1)
    thumb = conv_block(3, 64) + res_block(64) + conv(64, 3, 1)
    return cnn + vgg + thumb


def stego_encoder():
    stem = conv_block(75, 128) + 3 * res_block(128)
    return stem + conv(128, 3, 3) + conv(128, 3, 3)


def stego_decoder():
    stem = (conv_block(3, 64) + conv_block(64, 128) + conv_block(128, 128)
            + 2 * res_block(128))
    return stem + conv(128, 64, 1) + conv(128, 3, 1)


def token_prior_decoder():
    seed = conv_block(67, 128) + 2 * res_block(128)
    up64 = conv_block(128, 128) + res_block(128)
    up128 = conv_block(128, 128) + res_block(128)
    up256 = conv_block(128, 64) + res_block(64)
    return seed + up64 + up128 + up256 + conv(64, 3, 3)


def reverse_decoder():
    enc0 = conv_block(80, 128) + res_block(128)
    down1 = conv_block(128, 128) + res_block(128)
    down2 = conv_block(128, 256) + res_block(256)
    bottleneck = 2 * res_block(256)
    up1 = conv_block(512, 128) + res_block(128)
    up2 = conv_block(320, 128) + res_block(128)
    heads = conv(128, 1, 3) + conv(128, 3, 3)
    return (token_prior_decoder() + enc0 + down1 + down2
            + bottleneck + up1 + up2 + heads)


def analytic():
    return {
        "HybridTokenizer": tokenizer(),
        "StegoEncoder": stego_encoder(),
        "StegoDecoder": stego_decoder(),
        "ReverseDecoder": reverse_decoder(),
    }


# ---------- torch ground truth ------------------------------------------------
def via_torch():
    try:
        import torch  # noqa: F401
    except Exception as exc:
        # A broken/partial torch install raises OSError on Windows, not ImportError.
        print(f"  [torch] unavailable: {exc}")
        return None
    try:
        from model_definition import BenchmarkSystemV7, ModelConfig
    except Exception as exc:                      # pragma: no cover
        print(f"  [torch] could not import model_definition: {exc}")
        return None

    def count(m):
        return sum(p.numel() for p in m.parameters() if p.requires_grad)

    sysm = BenchmarkSystemV7(ModelConfig())
    return {
        "HybridTokenizer": count(sysm.tokenizer),
        "StegoEncoder": count(sysm.encoder),
        "StegoDecoder": count(sysm.decoder),
        "ReverseDecoder": count(sysm.reverse_decoder),
    }, count(sysm)


# ---------- dead-config check ------------------------------------------------
def dead_config_check():
    """Confirm hidden_channels / token_channels / token_size are unused."""
    try:
        import torch  # noqa: F401
        from model_definition import BenchmarkSystemV7, ModelConfig
    except Exception:
        return None

    def count(m):
        return sum(p.numel() for p in m.parameters() if p.requires_grad)

    a = count(BenchmarkSystemV7(ModelConfig()))
    b = count(BenchmarkSystemV7(ModelConfig(
        hidden_channels=48, token_channels=24, token_size=24)))
    return a, b


def main():
    print("=" * 66)
    print("FGSS parameter-count verification")
    print("=" * 66)

    ana = analytic()
    ana_total = sum(ana.values())

    print("\nAnalytic count (from layer shapes, no torch required)")
    print("-" * 66)
    ok = True
    for name, val in ana.items():
        exp = EXPECTED[name]
        flag = "OK " if val == exp else "!! "
        if val != exp:
            ok = False
        print(f"  {flag}{name:<20} {val:>12,}   (paper: {exp:>12,})")
    flag = "OK " if ana_total == EXPECTED_TOTAL else "!! "
    if ana_total != EXPECTED_TOTAL:
        ok = False
    print(f"  {flag}{'TOTAL':<20} {ana_total:>12,}   (paper: {EXPECTED_TOTAL:>12,})")

    embed = ana["HybridTokenizer"] + ana["StegoEncoder"]
    print(f"\n  Embedding path (tokenizer + stego encoder): {embed:,}"
          f"  -> paper says 1.9 M")
    print(f"  Full system: {ana_total:,}  -> paper says 10.7 M")

    tr = via_torch()
    if tr is None:
        print("\n[torch not available - analytic count only]")
        print("To get the ground truth:  pip install torch  then re-run.")
    else:
        per, total = tr
        print("\nTorch ground truth")
        print("-" * 66)
        for name, val in per.items():
            flag = "OK " if val == ana[name] else "!! "
            if val != ana[name]:
                ok = False
            print(f"  {flag}{name:<20} {val:>12,}")
        flag = "OK " if total == EXPECTED_TOTAL else "!! "
        if total != EXPECTED_TOTAL:
            ok = False
        print(f"  {flag}{'TOTAL':<20} {total:>12,}")

        dc = dead_config_check()
        if dc:
            a, b = dc
            print("\nDead-config check (are hidden/token_channels/token_size used?)")
            print("-" * 66)
            print(f"  ModelConfig()                                -> {a:,}")
            print(f"  ModelConfig(hidden=48, token_ch=24, size=24) -> {b:,}")
            if a == b:
                print("  CONFIRMED: those three fields are dead code. The 'small CPU")
                print("  variant' (h=48, d_tok=g_tok=24) cannot be instantiated, so any")
                print("  ablation sweeping them would have measured only seed noise.")
            else:
                print("  NOTE: the fields DO affect the model - my analysis was wrong.")
                print("  Tell Claude: the capacity-field finding needs revisiting.")

    print("\n" + "=" * 66)
    print("RESULT: " + ("all counts match the manuscript."
                        if ok else "MISMATCH - see '!!' lines above."))
    print("=" * 66)
    if not ok:
        print("\nIf there is a mismatch, paste this output back to Claude - the")
        print("numbers 10.7 M / 1.9 M in the paper would need correcting.")


if __name__ == "__main__":
    main()
