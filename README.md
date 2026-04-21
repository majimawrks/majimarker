# MajiMarker

Simple and portable image watermarking tool for Windows.

Stamps images with a purpose text and today's date. Supports diagonal and horizontal placement, adjustable opacity and color, and batch processing. Output files never overwrite the original — a counter suffix is appended automatically.

---

## Requirements

- Python 3.11+
- [Nuitka](https://nuitka.net/) (for building the exe)
- Pillow 10.4.0 — `pip install -r requirements.txt`

## Run from source

```
pip install -r requirements.txt
python src/main.py
```

## Build

```
pip install nuitka
build.bat
```

Output: `dist/MajiMarker.exe` — single file, no installer, no runtime dependency.

The build script uses `--onefile --lto=yes` and strips test/dev imports for a lean binary.

## Supported formats

JPG, JPEG, PNG, BMP, TIFF

---

## Versioning

Version is defined in [`src/__init__.py`](src/__init__.py). Releases follow `vMAJOR.MINOR.PATCH`.

To cut a release:

```bash
# 1. Bump __version__ in src/__init__.py
# 2. Commit and tag
git commit -am "chore: bump version to X.Y.Z"
git tag vX.Y.Z
git push origin master --tags
```

Then attach the built exe to the GitHub release.

---

## Contributing

Open an issue before starting work on anything non-trivial. PRs without a linked issue may be closed.

Keep changes focused — one fix or feature per PR. Follow the existing code style (no docstrings that repeat the function name, no unnecessary abstractions).

Security issues: see [SECURITY.md](SECURITY.md).

---

## License

MIT — see [LICENSE](LICENSE).

©majima.dev 2026 · made with Claude
