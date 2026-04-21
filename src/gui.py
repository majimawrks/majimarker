"""Minimal Tkinter GUI for MajiMarker."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from datetime import datetime

from watermark import add_watermark, WatermarkOrientation, WatermarkPosition, hex_to_rgb


SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')

# Orientation options with display labels
ORIENTATION_OPTIONS = [
    ("Diagonal ↗ (kiri bawah ke kanan atas)", WatermarkOrientation.DIAGONAL_BL_TR),
    ("Diagonal ↘ (kiri atas ke kanan bawah)", WatermarkOrientation.DIAGONAL_TL_BR),
    ("Horizontal", WatermarkOrientation.HORIZONTAL),
]

# Position options for horizontal watermarks
POSITION_OPTIONS = [
    ("Atas", WatermarkPosition.TOP),
    ("Tengah", WatermarkPosition.MIDDLE),
    ("Bawah", WatermarkPosition.BOTTOM),
]

# Color options
COLOR_OPTIONS = [
    ("Abu-abu", "#808080"),
    ("Hitam", "#000000"),
    ("Custom", None),
]


class WatermarkApp:
    """Minimal watermark application GUI."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MajiMarker - Watermark Dokumen")
        self.root.resizable(False, False)

        # Set app icon
        self._set_icon()

        # Register accent button style
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

        # File list
        self.files: list[Path] = []

        self._setup_ui()
        self._center_window()

    def _set_icon(self):
        """Set the application icon."""
        import sys

        # Try different icon locations
        icon_paths = [
            Path(__file__).parent.parent / "watermark.ico",  # ../watermark.ico from src/
            Path(__file__).parent / "watermark.ico",          # same dir as gui.py
            Path(sys.executable).parent / "watermark.ico",    # next to exe
        ]

        for icon_path in icon_paths:
            if icon_path.exists():
                try:
                    self.root.iconbitmap(str(icon_path))
                    break
                except tk.TclError:
                    continue

    def _center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def _setup_ui(self):
        """Setup the user interface."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        row = 0

        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File", padding="5")
        file_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        row += 1

        self.file_label = ttk.Label(file_frame, text="Belum ada file dipilih", width=45)
        self.file_label.grid(row=0, column=0, padx=(0, 10))

        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=0, column=1)

        ttk.Button(btn_frame, text="Pilih File", command=self._select_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Hapus", command=self._clear_files).pack(side=tk.LEFT, padx=2)

        # Purpose input
        ttk.Label(main_frame, text="Keperluan:").grid(row=row, column=0, sticky="w", pady=5)
        self.purpose_var = tk.StringVar(value="")
        self.purpose_entry = ttk.Entry(main_frame, textvariable=self.purpose_var, width=40)
        self.purpose_entry.grid(row=row, column=1, sticky="ew", pady=5)
        self.purpose_entry.focus()
        self.purpose_entry.bind("<Return>", lambda e: self._process())
        row += 1

        # Orientation dropdown
        ttk.Label(main_frame, text="Orientasi:").grid(row=row, column=0, sticky="w", pady=5)
        self.orientation_var = tk.StringVar(value=ORIENTATION_OPTIONS[0][0])
        self.orientation_combo = ttk.Combobox(
            main_frame,
            textvariable=self.orientation_var,
            values=[opt[0] for opt in ORIENTATION_OPTIONS],
            state="readonly",
            width=37
        )
        self.orientation_combo.grid(row=row, column=1, sticky="ew", pady=5)
        self.orientation_combo.bind("<<ComboboxSelected>>", self._on_orientation_change)
        row += 1

        # Position dropdown (only for horizontal)
        ttk.Label(main_frame, text="Posisi:").grid(row=row, column=0, sticky="w", pady=5)
        self.position_var = tk.StringVar(value=POSITION_OPTIONS[1][0])  # Default: Tengah
        self.position_combo = ttk.Combobox(
            main_frame,
            textvariable=self.position_var,
            values=[opt[0] for opt in POSITION_OPTIONS],
            state="readonly",
            width=37
        )
        self.position_combo.grid(row=row, column=1, sticky="ew", pady=5)
        # Initially disabled (diagonal is default)
        self.position_combo.config(state="disabled")
        row += 1

        # Stretch checkbox
        ttk.Label(main_frame, text="Ukuran:").grid(row=row, column=0, sticky="w", pady=5)
        self.stretch_var = tk.BooleanVar(value=True)
        self.stretch_check = ttk.Checkbutton(
            main_frame,
            text="Bentangkan teks (ujung ke ujung dengan padding)",
            variable=self.stretch_var
        )
        self.stretch_check.grid(row=row, column=1, sticky="w", pady=5)
        row += 1

        # Color selection
        ttk.Label(main_frame, text="Warna:").grid(row=row, column=0, sticky="w", pady=5)

        color_frame = ttk.Frame(main_frame)
        color_frame.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        self.color_var = tk.StringVar(value=COLOR_OPTIONS[0][0])
        self.color_combo = ttk.Combobox(
            color_frame,
            textvariable=self.color_var,
            values=[opt[0] for opt in COLOR_OPTIONS],
            state="readonly",
            width=15
        )
        self.color_combo.pack(side=tk.LEFT)
        self.color_combo.bind("<<ComboboxSelected>>", self._on_color_change)

        self.custom_color_var = tk.StringVar(value="#808080")
        self.custom_color_entry = ttk.Entry(
            color_frame,
            textvariable=self.custom_color_var,
            width=10
        )
        self.custom_color_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.custom_color_entry.config(state="disabled")
        self.custom_color_var.trace_add("write", self._on_preview_change)

        # Opacity slider
        ttk.Label(main_frame, text="Opacity:").grid(row=row, column=0, sticky="w", pady=5)

        opacity_frame = ttk.Frame(main_frame)
        opacity_frame.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        self.opacity_var = tk.IntVar(value=15)
        self.opacity_slider = ttk.Scale(
            opacity_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.opacity_var,
            command=self._update_opacity_label
        )
        self.opacity_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.opacity_label = ttk.Label(opacity_frame, text="15%", width=5)
        self.opacity_label.pack(side=tk.LEFT, padx=(10, 0))

        # Preview text
        ttk.Label(main_frame, text="Preview:").grid(row=row, column=0, sticky="w", pady=5)
        self.preview_label = tk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 10),
            fg="#808080"
        )
        self.preview_label.grid(row=row, column=1, sticky="w", pady=5)
        row += 1

        # Bind events for preview update
        self.purpose_var.trace_add("write", self._on_preview_change)
        self.opacity_var.trace_add("write", self._on_preview_change)
        self._update_preview()

        # Process button
        self.process_btn = ttk.Button(
            main_frame,
            text="Proses Watermark",
            command=self._process,
            style="Accent.TButton"
        )
        self.process_btn.grid(row=row, column=0, columnspan=2, pady=(15, 5), sticky="ew")
        row += 1

        # Status label
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="gray")
        self.status_label.grid(row=row, column=0, columnspan=2, pady=(5, 0))
        row += 1

        # Copyright footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=row, column=0, columnspan=2, pady=(15, 0))

        copyright_label = ttk.Label(
            footer_frame,
            text="©majima.dev 2026 - made with Claude",
            foreground="gray",
            font=("Segoe UI", 8)
        )
        copyright_label.pack()

        icon_link = ttk.Label(
            footer_frame,
            text="Watermark icons created by Freepik - Flaticon",
            foreground="blue",
            font=("Segoe UI", 8),
            cursor="hand2"
        )
        icon_link.pack()
        icon_link.bind("<Button-1>", lambda e: self._open_url("https://www.flaticon.com/free-icons/watermark"))

    def _open_url(self, url: str):
        """Open URL in default browser."""
        import webbrowser
        webbrowser.open(url)

    def _on_color_change(self, event=None):
        """Handle color dropdown change."""
        selected = self.color_var.get()
        if selected == "Custom":
            self.custom_color_entry.config(state="normal")
        else:
            self.custom_color_entry.config(state="disabled")
        self._update_preview()

    def _get_selected_color(self) -> tuple[int, int, int]:
        """Get the currently selected color as RGB tuple."""
        selected_label = self.color_var.get()
        for label, hex_val in COLOR_OPTIONS:
            if label == selected_label:
                if hex_val is None:  # Custom
                    try:
                        return hex_to_rgb(self.custom_color_var.get())
                    except (ValueError, IndexError):
                        return (128, 128, 128)  # Default gray on invalid
                return hex_to_rgb(hex_val)
        return (128, 128, 128)

    def _get_selected_color_hex(self) -> str:
        """Get the currently selected color as hex string."""
        selected_label = self.color_var.get()
        for label, hex_val in COLOR_OPTIONS:
            if label == selected_label:
                if hex_val is None:  # Custom
                    return self.custom_color_var.get()
                return hex_val
        return "#808080"

    def _on_preview_change(self, *args):
        """Handle preview update triggers."""
        self._update_preview()

    def _update_preview(self):
        """Update the preview text with current settings."""
        purpose = self.purpose_var.get().strip()
        if not purpose:
            purpose = "Keperluan"
        date_str = datetime.now().strftime("%d/%m/%Y")
        preview_text = f"{purpose} - {date_str}"

        # Get color
        color_hex = self._get_selected_color_hex()
        try:
            rgb = hex_to_rgb(color_hex)
        except (ValueError, IndexError):
            rgb = (128, 128, 128)

        # Get the actual background color of the window for accurate blending
        # Default tkinter bg is typically #f0f0f0 on Windows
        try:
            bg_color = self.preview_label.winfo_rgb(self.root.cget('bg'))
            bg_rgb = (bg_color[0] // 256, bg_color[1] // 256, bg_color[2] // 256)
        except Exception:
            bg_rgb = (240, 240, 240)  # Fallback to typical Windows bg

        # Blend color with background based on opacity to simulate transparency
        # Opacity slider is 10-100, which maps directly to alpha 10-100 out of 255
        # So we normalize: alpha = opacity / 100.0 for preview purposes (0.1 to 1.0)
        opacity = self.opacity_var.get()
        alpha = opacity / 100.0  # 10-100 -> 0.1-1.0
        blended = tuple(int(c * alpha + bg_rgb[i] * (1 - alpha)) for i, c in enumerate(rgb))
        blended_hex = f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"

        self.preview_label.config(text=preview_text, fg=blended_hex)

    def _on_orientation_change(self, event=None):
        """Handle orientation change - enable/disable position dropdown."""
        orientation = self._get_selected_orientation()
        if orientation == WatermarkOrientation.HORIZONTAL:
            self.position_combo.config(state="readonly")
            if not self.position_var.get():
                self.position_var.set(POSITION_OPTIONS[1][0])
        else:
            self.position_var.set("")
            self.position_combo.config(state="disabled")

    def _get_selected_orientation(self) -> WatermarkOrientation:
        """Get the currently selected orientation enum."""
        selected_label = self.orientation_var.get()
        for label, orientation in ORIENTATION_OPTIONS:
            if label == selected_label:
                return orientation
        return WatermarkOrientation.DIAGONAL_BL_TR

    def _get_selected_position(self) -> WatermarkPosition:
        """Get the currently selected position enum."""
        selected_label = self.position_var.get()
        for label, position in POSITION_OPTIONS:
            if label == selected_label:
                return position
        return WatermarkPosition.MIDDLE

    def _update_opacity_label(self, value=None):
        val = self.opacity_var.get()
        self.opacity_label.config(text=f"{val}%")
        self._update_preview()

    def _select_files(self):
        """Open file dialog to select images."""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("All files", "*.*")
        ]

        files = filedialog.askopenfilenames(
            title="Pilih gambar",
            filetypes=filetypes
        )

        if files:
            self.files = [Path(f) for f in files if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS]
            self._update_file_label()

    def _clear_files(self):
        """Clear selected files."""
        self.files = []
        self._update_file_label()

    def _update_file_label(self):
        """Update the file selection label."""
        count = len(self.files)
        if count == 0:
            self.file_label.config(text="Belum ada file dipilih")
        elif count == 1:
            self.file_label.config(text=self.files[0].name)
        else:
            self.file_label.config(text=f"{count} file dipilih")

    def _process(self):
        """Process the watermarking."""
        # Validation
        if not self.files:
            messagebox.showwarning("Peringatan", "Pilih file terlebih dahulu!")
            return

        purpose = self.purpose_var.get().strip()
        if not purpose:
            messagebox.showwarning("Peringatan", "Masukkan keperluan/tujuan!")
            self.purpose_entry.focus()
            return

        # percent → 8-bit alpha
        alpha = int(round(self.opacity_var.get() * 2.55))
        orientation = self._get_selected_orientation()
        position = self._get_selected_position()
        stretch = self.stretch_var.get()
        color = self._get_selected_color()

        # Disable UI during processing
        self.process_btn.config(state=tk.DISABLED)
        self.status_var.set("Memproses...")
        self.root.update()

        try:
            results = []
            total = len(self.files)

            for i, file_path in enumerate(self.files):
                self.status_var.set(f"Memproses {i + 1}/{total}: {file_path.name}")
                self.root.update()

                result = add_watermark(
                    file_path,
                    purpose,
                    alpha,
                    orientation=orientation,
                    position=position,
                    stretch=stretch,
                    color=color
                )
                results.append(result)

            # Success message
            output_folder = results[0].parent
            if len(results) == 1:
                msg = f"Berhasil!\n\nFile disimpan:\n{results[0]}"
            else:
                msg = f"Berhasil memproses {len(results)} file!\n\nFile disimpan di folder yang sama dengan suffix '_watermarked'"

            open_folder = messagebox.askyesno("Selesai", msg + "\n\nBuka folder output?")
            if open_folder:
                import os
                os.startfile(str(output_folder))
            self.status_var.set(f"Selesai: {len(results)} file diproses")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memproses:\n{str(e)}")
            self.status_var.set("Error!")

        finally:
            self.process_btn.config(state=tk.NORMAL)


def run_app():
    """Run the application."""
    root = tk.Tk()

    # Try to set DPI awareness on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = WatermarkApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_app()
