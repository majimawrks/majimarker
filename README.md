# MajiMarker

Simple and portable watermarking tool.

Stamps images with a purpose text and today's date — diagonal or horizontal, adjustable opacity and color. Outputs a separate file, never overwrites the original.

## Usage

```
python src/main.py
```

Or run the prebuilt `MajiMarker.exe` from `dist/`.

## Build

Requires [Nuitka](https://nuitka.net/) and Python 3.11+.

```
pip install -r requirements.txt
build.bat
```

Output: `dist/MajiMarker.exe` — single file, no installer needed.

## Supported formats

JPG, JPEG, PNG, BMP, TIFF

## License

MIT — see [LICENSE](LICENSE).

---

©majima.dev 2026 · made with Claude
