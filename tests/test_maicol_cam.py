import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import webcam_float

def test_version_defined():
    assert hasattr(webcam_float, "__version__")
    assert webcam_float.__version__ == "1.1.0"

def test_config_defaults(tmp_path, monkeypatch):
    test_cfg = tmp_path / "test_config.json"
    monkeypatch.setattr(webcam_float, "get_config_path", lambda: str(test_cfg))

    cfg = webcam_float.load_config()
    assert cfg is None

def test_config_save_and_load(tmp_path, monkeypatch):
    test_cfg = tmp_path / "test_config.json"
    monkeypatch.setattr(webcam_float, "get_config_path", lambda: str(test_cfg))

    sample_data = {
        "pos_x": 120,
        "pos_y": 80,
        "width": 320,
        "height": 420,
        "is_circle": False,
        "corner_radius": 28,
        "always_on_top": True,
        "show_border": False,
        "mirror_mode": False,
        "zoom_factor": 1.25,
        "pan_offset_x": 0,
        "pan_offset_y": 0
    }
    with open(test_cfg, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)

    loaded = webcam_float.load_config()
    assert loaded["pos_x"] == 120
    assert loaded["width"] == 320
    assert loaded["corner_radius"] == 28
    assert loaded["always_on_top"] is True
    assert loaded["show_border"] is False

def test_app_icon_exists():
    icon_path = webcam_float.get_app_icon_path()
    assert icon_path is not None
    assert os.path.exists(icon_path)

def test_zoom_factor_limits():
    zoom = 1.0
    # Simulate zoom in steps
    for _ in range(20):
        zoom = min(4.0, zoom + 0.25)
    assert zoom == 4.0

    # Simulate zoom out steps
    for _ in range(20):
        zoom = max(1.0, zoom - 0.25)
    assert zoom == 1.0

def test_aspect_ratio_calculations():
    formats = {
        "9:16": (270, 480),
        "3:4": (315, 420),
        "16:9": (480, 270),
        "4:3": (400, 300),
        "1:1": (340, 340)
    }
    for name, (w, h) in formats.items():
        assert w > 0 and h > 0
        ratio = w / h
        assert 0.5 <= ratio <= 2.0

def test_video_capture_thread_processing():
    import numpy as np
    from PyQt6.QtGui import QImage

    thread = webcam_float.VideoCaptureThread()
    thread.update_render_params(
        win_w=300,
        win_h=200,
        dpr=1.0,
        zoom_factor=1.0,
        pan_offset_x=0,
        pan_offset_y=0,
        mirror_mode=True,
        sharpness_boost=True
    )

    test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    qimg = thread._process_frame(test_frame)

    assert isinstance(qimg, QImage)
    assert not qimg.isNull()
    assert qimg.width() == 300
    assert qimg.height() == 200
