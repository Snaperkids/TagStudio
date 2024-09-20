# Copyright (C) 2024 Travis Abendshien (CyanVoxel).
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio


import binascii
import io
import math
from struct import unpack
import typing
from dataclasses import dataclass, field

import structlog
import os
import pathlib
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from src.core.constants import TAG_ARCHIVED, TAG_FAVORITE
from src.core.library import Library, Tag
from src.core.library.alchemy.fields import _FieldID
from src.core.palette import ColorType, get_tag_color
from src.qt.flowlayout import FlowLayout

if typing.TYPE_CHECKING:
    from src.qt.ts_qt import QtDriver

logger = structlog.get_logger(__name__)

jpeg_segment_markers = {
    0xFFD8: "SOI",
    0xFFE1: "APP",
    0xFFE1: "APP1",
    0xFFC0: "SOF0",
    0xFFC2: "SOF2",
    0xFFC4: "DHT",
    0xFFDB: "DQT",
    0xFFDD: "DRI",
    0xFFDA: "SOS",
    0xFFFE: "COM",
    0xFFD9: "EOI"
}

def decode_jpeg(file_data: bytes):
    
    while True:
        marker, = unpack(">H", file_data[0:2])
        if marker == 0xFFD8:
            logger.info("SOI : " + str(2))
            file_data = file_data[2:]
        else:
            segment_length, = unpack(">H", file_data[2:4])
            logger.info(str(marker) + " : " + str(segment_length))
            file_data = file_data[2 + segment_length:]
        if len(file_data) == 0:
            break

# RETURNS: Input Stream Positioned at the Beginning of the XMP Data
def get_embedded_xmp_data(entry_file_stream: io.BufferedReader, suffix: str):
    
    file_data = entry_file_stream.read()

    if suffix == ".jpg":
        return io.BytesIO(decode_jpeg(file_data))


def import_metadata(library: Library):
    logger.info("Beginning Metadata Import")

    for entry in library.get_entries():
        
        # Finding Path to XMP File and Getting File Stream for Readin
        xmp_file_path = library.library_dir / pathlib.Path(entry.path.stem + ".xmp")
        xmp_file_stream = None

        if xmp_file_path.exists():
            import_xmp(xmp_file_path)
        else:


        logger.debug("Parse XMP Data to Tags")
        logger.debug("Adding XMP Tags")
        
        # if tag and not entry.has_tag(tag):
        #     library.add_field_tag(entry, tag, _FieldID.TAGS.name, create_field=True)

        xmp_file_stream.close()

    logger.info("Done")

# =========== UI ===========

class XMPToTagsModal(QWidget):
    def __init__(self, library: "Library", driver: "QtDriver"):
        super().__init__()
        self.library = library
        self.driver = driver
        self.count = -1
        self.filename = ""

        self.setWindowTitle("Import XMP")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setMinimumSize(640, 320)
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(6, 6, 6, 6)

        self.title_widget = QLabel()
        self.title_widget.setObjectName("title")
        self.title_widget.setWordWrap(True)
        self.title_widget.setStyleSheet("font-weight:bold;" "font-size:14px;" "padding-top: 6px")
        self.title_widget.setText("Import XMP Tags")
        self.title_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.desc_widget = QLabel()
        self.desc_widget.setObjectName("descriptionLabel")
        self.desc_widget.setWordWrap(True)
        self.desc_widget.setText(
            """This tool is intended to import tags from embedded metadata and .xmp sidecar files.
            This tool is incomplete and still needs a preview created for it as the primary QoL.
            Currently this tool only supports EXIF and XMP metadata from JPEGs"""
        )

        #TODO: Add Preview for XMP Import

        self.apply_button = QPushButton()
        self.apply_button.setText("&Apply")
        self.apply_button.setMinimumWidth(100)
        self.apply_button.clicked.connect(self.on_apply)

        # self.showEvent = self.on_open  # type: ignore

        self.root_layout.addWidget(self.title_widget)
        self.root_layout.addWidget(self.desc_widget)
        self.root_layout.addWidget(self.apply_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_apply(self, event):
        import_file_metadata(self.library)
        self.close()
        self.driver.preview_panel.update_widgets()
