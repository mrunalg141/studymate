import io
import os
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pypdf import PdfWriter

# Pre-set GROQ_API_KEY so app.llm client initializes without requiring real API keys
os.environ.setdefault("GROQ_API_KEY", "test-dummy-groq-key")

# Stub heavy ML / vector DB dependencies if not present to avoid unnecessary overhead
for mod in ["chromadb", "fastembed"]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import app.main as app_main
from fastapi.testclient import TestClient


HEX_UUID_PDF_REGEX = re.compile(r"^[0-9a-f]{32}\.pdf$")


@pytest.fixture
def sample_pdf_bytes():
    """Generates valid minimal 1-page PDF bytes for upload tests."""
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.fixture
def test_env(monkeypatch, tmp_path):
    """
    Sets up an isolated upload directory and mocks the RAG indexing pipeline boundary
    so tests verify upload path safety without running heavy model inference.
    """
    isolated_upload_dir = tmp_path / "uploads"
    isolated_upload_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(app_main, "UPLOAD_DIR", isolated_upload_dir)

    mock_index = MagicMock(return_value=1)
    monkeypatch.setattr(app_main, "index_pdf", mock_index)

    with TestClient(app_main.app) as client:
        yield client, isolated_upload_dir, mock_index


def test_upload_normal_filename(test_env, sample_pdf_bytes):
    """Test standard valid PDF upload."""
    client, upload_dir, mock_index = test_env
    filename = "lecture_notes.pdf"

    response = client.post(
        "/upload",
        files={"file": (filename, sample_pdf_bytes, "application/pdf")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"'{filename}' uploaded successfully."
    assert data["chunks"] == 1

    # Verify RAG index was called with safe path and original doc_id
    assert mock_index.called
    saved_path_str, = mock_index.call_args[0]
    called_doc_id = mock_index.call_args[1].get("doc_id")
    assert called_doc_id == filename

    # Verify the physical file is stored strictly in the uploads directory
    saved_path = Path(saved_path_str)
    assert saved_path.exists()
    assert saved_path.parent == upload_dir
    assert HEX_UUID_PDF_REGEX.match(saved_path.name)
    assert saved_path.name != filename

    # Verify SQLite preserves original filename for metadata/display
    latest_doc = app_main.get_latest_document()
    assert latest_doc is not None
    assert latest_doc["filename"] == filename


@pytest.mark.parametrize("traversal_filename", [
    "../../evil.pdf",
    "....//....//escape.pdf",
    r"..\..\win_escape.pdf",
    r"subdir\..\..\..\boot.ini.pdf",
])
def test_upload_path_traversal_filenames(test_env, sample_pdf_bytes, tmp_path, traversal_filename):
    """
    Test that filenames containing path traversal sequences (../, ..\\) cannot escape
    the uploads directory and do not write to arbitrary locations.
    """
    client, upload_dir, mock_index = test_env

    # Marker file outside upload_dir to ensure no external writes occur
    canary_file = tmp_path / "evil.pdf"
    assert not canary_file.exists()

    response = client.post(
        "/upload",
        files={"file": (traversal_filename, sample_pdf_bytes, "application/pdf")}
    )

    assert response.status_code == 200
    assert not canary_file.exists()

    # Verify physical file is safely stored inside upload_dir with a UUID name
    saved_path_str, = mock_index.call_args[0]
    saved_path = Path(saved_path_str)
    assert saved_path.exists()
    assert saved_path.is_relative_to(upload_dir)
    assert saved_path.parent == upload_dir
    assert HEX_UUID_PDF_REGEX.match(saved_path.name)
    assert ".." not in saved_path.name

    # Verify original filename is kept for metadata/display
    assert response.json()["message"] == f"'{traversal_filename}' uploaded successfully."
    assert mock_index.call_args[1].get("doc_id") == traversal_filename
    assert app_main.get_latest_document()["filename"] == traversal_filename


@pytest.mark.parametrize("absolute_filename", [
    "/etc/passwd.pdf",
    "/var/log/secret.pdf",
    r"C:\Windows\System32\cmd.pdf",
    r"D:\Desktop\studymate\pwned.pdf",
])
def test_upload_absolute_path_filenames(test_env, sample_pdf_bytes, absolute_filename):
    """
    Test that absolute or root-relative paths in client filenames cannot overwrite
    system or workspace files and are kept contained within the uploads directory.
    """
    client, upload_dir, mock_index = test_env

    response = client.post(
        "/upload",
        files={"file": (absolute_filename, sample_pdf_bytes, "application/pdf")}
    )

    assert response.status_code == 200

    saved_path_str, = mock_index.call_args[0]
    saved_path = Path(saved_path_str)
    assert saved_path.exists()
    assert saved_path.is_relative_to(upload_dir)
    assert saved_path.parent == upload_dir
    assert HEX_UUID_PDF_REGEX.match(saved_path.name)

    # Verify original filename (or sanitized basename as parsed by multipart) is kept for metadata
    expected_display_name = app_main.get_latest_document()["filename"]
    assert response.json()["message"] == f"'{expected_display_name}' uploaded successfully."
    assert mock_index.call_args[1].get("doc_id") == expected_display_name


@pytest.mark.parametrize("special_filename", [
    "My Study Guide (2026) - Final Version.pdf",
    "résumé_académique_élève.pdf",
    "日本語_研究ノート.pdf",
    "ملف_الفيزياء.pdf",
    "math & physics [ch. 1-3] @2026.pdf",
])
def test_upload_spaces_and_unicode_filenames(test_env, sample_pdf_bytes, special_filename):
    """
    Test that filenames containing spaces, punctuation, or Unicode characters
    are preserved for display and metadata without breaking filesystem operations.
    """
    client, upload_dir, mock_index = test_env

    response = client.post(
        "/upload",
        files={"file": (special_filename, sample_pdf_bytes, "application/pdf")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"'{special_filename}' uploaded successfully."

    # Physical file is safely saved using an ASCII hex UUID on disk
    saved_path_str, = mock_index.call_args[0]
    saved_path = Path(saved_path_str)
    assert saved_path.exists()
    assert saved_path.is_relative_to(upload_dir)
    assert HEX_UUID_PDF_REGEX.match(saved_path.name)

    # Original Unicode filename is intact in SQLite metadata
    latest_doc = app_main.get_latest_document()
    assert latest_doc["filename"] == special_filename
    assert mock_index.call_args[1].get("doc_id") == special_filename

