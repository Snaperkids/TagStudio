# Copyright (C) 2024 Travis Abendshien (CyanVoxel).
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio


import math
import typing
from dataclasses import dataclass, field

import structlog
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



def import_xmp(library: Library):
    logger.info("Beginning Import XMP")

    for entry in library.get_entries():
        logger.debug("Finding XMP File")
        
        # xmp_file = get_xmp_file(entry.path)

        # if not xmp_file.exist():
        #     logger.debug("Checking for Embedded XMP")
        
        logger.debug("Parse XMP Data to Tags")
        logger.debug("Adding XMP Tags")
        
        # if tag and not entry.has_tag(tag):
        #     library.add_field_tag(entry, tag, _FieldID.TAGS.name, create_field=True)

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
        self.setMinimumSize(640, 640)
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
            """This tool is intended to import XMP tags from embedded metadata and .xmp sidecar files.
            This tool is incomplete and still needs a preview created for it as the primary QoL"""
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
        import_xmp(self.library)
        self.close()
        self.driver.preview_panel.update_widgets()
