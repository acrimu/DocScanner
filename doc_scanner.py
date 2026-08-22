from __future__ import annotations

import math
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy as np
from PIL import Image, ImageTk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None


class DocumentScannerApp:
    MARKER_RADIUS = 7
    MARKER_HIT_RADIUS = 14
    MAGNIFIER_SIZE = 180
    MAGNIFIER_SOURCE_SIZE = 60
    MAGNIFIER_MARGIN = 14

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Document Perspective Scanner")
        self.root.geometry("1100x760")
        self.root.minsize(760, 520)

        self.source_path: Path | None = None
        self.source_image: Image.Image | None = None
        self.result_image: Image.Image | None = None
        self.display_photo: ImageTk.PhotoImage | None = None
        self.magnifier_photo: ImageTk.PhotoImage | None = None
        self.points: list[tuple[float, float]] = []
        self.drag_index: int | None = None
        self.pointer_position: tuple[float, float] | None = None
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        self._build_ui()

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="Open image", command=self.open_image).pack(side=tk.LEFT)
        self.rotate_left_button = ttk.Button(
            toolbar, text="Rotate left", command=lambda: self.rotate_image(clockwise=False), state=tk.DISABLED
        )
        self.rotate_left_button.pack(side=tk.LEFT, padx=(6, 0))
        self.rotate_right_button = ttk.Button(
            toolbar, text="Rotate right", command=lambda: self.rotate_image(clockwise=True), state=tk.DISABLED
        )
        self.rotate_right_button.pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Clear corners", command=self.clear_points).pack(side=tk.LEFT, padx=6)
        self.process_button = ttk.Button(toolbar, text="Extract page", command=self.extract_page, state=tk.DISABLED)
        self.process_button.pack(side=tk.LEFT)
        self.save_button = ttk.Button(toolbar, text="Save result", command=self.save_result, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=6)

        self.status = tk.StringVar(value="Open an image, then click the four page corners.")
        ttk.Label(toolbar, textvariable=self.status).pack(side=tk.LEFT, padx=14)

        self.canvas = tk.Canvas(self.root, background="#252525", cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _event: self.redraw())
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        if DND_FILES is not None:
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind("<<Drop>>", self.on_file_drop)

    def open_image(self) -> None:
        filename = filedialog.askopenfilename(
            title="Open scanned page",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp"), ("All files", "*.*")],
        )
        if not filename:
            return
        self.load_image(filename)

    def load_image(self, filename: str) -> None:
        try:
            with Image.open(filename) as image:
                self.source_image = image.convert("RGB")
        except Exception as exc:
            messagebox.showerror("Cannot open image", str(exc))
            return

        self.source_path = Path(filename)
        self.points.clear()
        self.result_image = None
        self.save_button.config(state=tk.DISABLED)
        self.process_button.config(state=tk.DISABLED)
        self.rotate_left_button.config(state=tk.NORMAL)
        self.rotate_right_button.config(state=tk.NORMAL)
        self.status.set("Click the four corners in any order. Drag a marker to adjust it.")
        self.redraw()

    def on_file_drop(self, event: tk.Event) -> None:
        """Load the first file from a desktop drag-and-drop event."""
        filenames = self.root.tk.splitlist(event.data)
        if filenames:
            self.load_image(filenames[0])

    def clear_points(self) -> None:
        self.points.clear()
        self.process_button.config(state=tk.DISABLED)
        self.status.set("Click the four page corners in any order.")
        self.redraw()

    def rotate_image(self, clockwise: bool) -> None:
        if self.source_image is None:
            return
        operation = Image.Transpose.ROTATE_270 if clockwise else Image.Transpose.ROTATE_90
        self.source_image = self.source_image.transpose(operation)
        self.points.clear()
        self.result_image = None
        self.process_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        direction = "right" if clockwise else "left"
        self.status.set(f"Image rotated {direction}. Click the four page corners.")
        self.redraw()

    def redraw(self) -> None:
        self.canvas.delete("all")
        if self.source_image is None:
            self.canvas.create_text(
                max(1, self.canvas.winfo_width()) / 2,
                max(1, self.canvas.winfo_height()) / 2,
                text="Drop an image here\nor click Open image",
                fill="#dddddd",
                font=("TkDefaultFont", 18),
            )
            return

        canvas_w = max(1, self.canvas.winfo_width())
        canvas_h = max(1, self.canvas.winfo_height())
        image_w, image_h = self.source_image.size
        self.scale = min(canvas_w / image_w, canvas_h / image_h)
        draw_w = max(1, round(image_w * self.scale))
        draw_h = max(1, round(image_h * self.scale))
        self.offset_x = (canvas_w - draw_w) / 2
        self.offset_y = (canvas_h - draw_h) / 2

        displayed = self.source_image.resize((draw_w, draw_h), Image.Resampling.LANCZOS)
        self.display_photo = ImageTk.PhotoImage(displayed)
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.display_photo)

        canvas_points = [self.image_to_canvas(point) for point in self.points]
        if len(canvas_points) == 4:
            ordered = self.order_points(np.asarray(canvas_points, dtype=np.float32))
            coords = [coordinate for point in ordered for coordinate in point]
            self.canvas.create_polygon(*coords, outline="#00e5ff", fill="", width=3)

        for index, (x, y) in enumerate(canvas_points):
            r = self.MARKER_RADIUS
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#ffcc00", outline="#111111", width=2)
            self.canvas.create_text(x + 14, y - 14, text=str(index + 1), fill="white", font=("TkDefaultFont", 10, "bold"))

        self.draw_magnifier()

    def draw_magnifier(self) -> None:
        """Draw a zoomed view of the image beneath the pointer."""
        self.canvas.delete("magnifier")
        if self.source_image is None or self.pointer_position is None:
            return

        image_point = self.canvas_to_image(*self.pointer_position)
        if image_point is None:
            return

        image_x, image_y = image_point
        source_size = self.MAGNIFIER_SOURCE_SIZE
        half_source = source_size / 2
        crop = self.source_image.crop(
            (
                round(image_x - half_source),
                round(image_y - half_source),
                round(image_x + half_source),
                round(image_y + half_source),
            )
        )
        zoomed = crop.resize((self.MAGNIFIER_SIZE, self.MAGNIFIER_SIZE), Image.Resampling.NEAREST)
        self.magnifier_photo = ImageTk.PhotoImage(zoomed)

        canvas_width = max(1, self.canvas.winfo_width())
        left = max(self.MAGNIFIER_MARGIN, canvas_width - self.MAGNIFIER_SIZE - self.MAGNIFIER_MARGIN)
        top = self.MAGNIFIER_MARGIN
        right = left + self.MAGNIFIER_SIZE
        bottom = top + self.MAGNIFIER_SIZE
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2

        self.canvas.create_rectangle(
            left - 3,
            top - 3,
            right + 3,
            bottom + 3,
            fill="#111111",
            outline="#ffffff",
            width=2,
            tags="magnifier",
        )
        self.canvas.create_image(left, top, anchor=tk.NW, image=self.magnifier_photo, tags="magnifier")
        self.canvas.create_line(center_x, top, center_x, bottom, fill="#00e5ff", width=1, tags="magnifier")
        self.canvas.create_line(left, center_y, right, center_y, fill="#00e5ff", width=1, tags="magnifier")
        self.canvas.create_oval(
            center_x - 5,
            center_y - 5,
            center_x + 5,
            center_y + 5,
            outline="#ffcc00",
            width=2,
            tags="magnifier",
        )

    def image_to_canvas(self, point: tuple[float, float]) -> tuple[float, float]:
        return point[0] * self.scale + self.offset_x, point[1] * self.scale + self.offset_y

    def canvas_to_image(self, x: float, y: float) -> tuple[float, float] | None:
        if self.source_image is None:
            return None
        image_x = (x - self.offset_x) / self.scale
        image_y = (y - self.offset_y) / self.scale
        width, height = self.source_image.size
        if 0 <= image_x < width and 0 <= image_y < height:
            return image_x, image_y
        return None

    def on_mouse_down(self, event: tk.Event) -> None:
        if self.source_image is None:
            return
        self.pointer_position = (event.x, event.y)
        for index, point in enumerate(self.points):
            x, y = self.image_to_canvas(point)
            if math.hypot(event.x - x, event.y - y) <= self.MARKER_HIT_RADIUS:
                self.drag_index = index
                return
        point = self.canvas_to_image(event.x, event.y)
        if point is not None and len(self.points) < 4:
            self.points.append(point)
            self.process_button.config(state=tk.NORMAL if len(self.points) == 4 else tk.DISABLED)
            self.status.set(f"{len(self.points)}/4 corners selected." if len(self.points) < 4 else "Ready. Drag corners to adjust, then extract the page.")
            self.redraw()

    def on_mouse_drag(self, event: tk.Event) -> None:
        self.pointer_position = (event.x, event.y)
        if self.drag_index is None or self.source_image is None:
            return
        width, height = self.source_image.size
        x = min(max((event.x - self.offset_x) / self.scale, 0), width - 1)
        y = min(max((event.y - self.offset_y) / self.scale, 0), height - 1)
        self.points[self.drag_index] = (x, y)
        self.redraw()

    def on_mouse_up(self, _event: tk.Event) -> None:
        self.drag_index = None

    def on_mouse_move(self, event: tk.Event) -> None:
        self.pointer_position = (event.x, event.y)
        self.draw_magnifier()

    def on_mouse_leave(self, _event: tk.Event) -> None:
        self.pointer_position = None
        self.canvas.delete("magnifier")

    @staticmethod
    def order_points(points: np.ndarray) -> np.ndarray:
        """Return points in top-left, top-right, bottom-right, bottom-left order."""
        center = points.mean(axis=0)
        angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
        circular = points[np.argsort(angles)]
        start = int(np.argmin(circular.sum(axis=1)))
        ordered = np.roll(circular, -start, axis=0)
        if ordered[1, 0] < ordered[-1, 0]:
            ordered = ordered[[0, 3, 2, 1]]
        return ordered.astype(np.float32)

    def extract_page(self) -> None:
        if self.source_image is None or len(self.points) != 4:
            return
        source = self.order_points(np.asarray(self.points, dtype=np.float32))
        top_left, top_right, bottom_right, bottom_left = source
        width = round(max(np.linalg.norm(bottom_right - bottom_left), np.linalg.norm(top_right - top_left)))
        height = round(max(np.linalg.norm(top_right - bottom_right), np.linalg.norm(top_left - bottom_left)))
        if width < 2 or height < 2:
            messagebox.showerror("Invalid selection", "The selected corners do not form a usable page.")
            return

        destination = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
        matrix = cv2.getPerspectiveTransform(source, destination)
        source_array = np.asarray(self.source_image)
        rectified = cv2.warpPerspective(source_array, matrix, (width, height), flags=cv2.INTER_CUBIC)
        self.result_image = Image.fromarray(rectified)
        self.save_button.config(state=tk.NORMAL)
        self.show_result_window()

    def show_result_window(self) -> None:
        if self.result_image is None:
            return
        window = tk.Toplevel(self.root)
        window.title("Extracted page")
        window_width = min(900, self.root.winfo_screenwidth() - 100)
        window_height = min(700, self.root.winfo_screenheight() - 100)
        window.geometry(f"{window_width}x{window_height}")
        window.minsize(320, 240)

        controls = ttk.Frame(window, padding=8)
        controls.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(controls, text="Save result", command=self.save_result).pack()

        preview_area = tk.Frame(window, background="#252525")
        preview_area.pack(fill=tk.BOTH, expand=True)
        label = tk.Label(preview_area, background="#252525", borderwidth=0)
        label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        def resize_preview(event: tk.Event | None = None) -> None:
            if self.result_image is None:
                return
            available_width = event.width - 16 if event is not None else label.winfo_width() - 16
            available_height = event.height - 16 if event is not None else label.winfo_height() - 16
            if available_width < 2 or available_height < 2:
                return

            image_width, image_height = self.result_image.size
            scale = min(available_width / image_width, available_height / image_height)
            preview_size = (
                max(1, round(image_width * scale)),
                max(1, round(image_height * scale)),
            )
            preview = self.result_image.resize(preview_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview)
            label.config(image=photo)
            label.image = photo

        preview_area.bind("<Configure>", resize_preview)
        window.after_idle(resize_preview)

    def save_result(self) -> None:
        if self.result_image is None:
            return
        initial = f"{self.source_path.stem}_scanned.png" if self.source_path else "scanned_page.png"
        filename = filedialog.asksaveasfilename(
            title="Save extracted page",
            initialfile=initial,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("TIFF", "*.tif *.tiff")],
        )
        if not filename:
            return
        try:
            self.result_image.save(filename, quality=95)
            self.status.set(f"Saved: {filename}")
        except Exception as exc:
            messagebox.showerror("Cannot save image", str(exc))


def main() -> None:
    root = TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    DocumentScannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
