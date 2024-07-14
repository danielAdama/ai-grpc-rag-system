import pytest

def pytest_configure(config):
    config.option.assert_rewrite_exclude.append("anyio")

import pathlib
import sys

current_dir = pathlib.Path(__file__).parent
previous_dir = current_dir.parent
sys.path.append(str(previous_dir))

from pdf.services.pdf_service import PDFService
from pathlib import Path

@pytest.fixture
def pdf_service():
    return PDFService()

def test_extract_source_title(pdf_service):
    text = "See discussions, stats, and author profiles for this publication at: https://www.researchgate.net/publication/377396514\nActive Inference for AI\nConference Paper "
    "· January 2024\nCITATIONS\n0\nREADS\n137\n1 author:\nMaria Raffa\nIULM Libera Università di Lingue "
    "e Comunicazione di Milano\n4 PUBLICATIONS\xa0\xa0\xa00 CITATIONS\xa0\xa0\xa0\nSEE PROFILE\nAll content following this page was uploaded "
    "by Maria Raffa on 14 January 2024.\nThe user has requested enhancement of the downloaded file.\n1 authors: John Doe, Jane Smith"

    source, title = pdf_service.extract_source_title(text)
    assert source == "https://www.researchgate.net/publication/377396514"
    assert title == "Active Inference for AI"

def test_extract_author(pdf_service):
    text = "1 authors: John Doe, Jane Smith"
    author = pdf_service.extract_author(text)
    assert author == "John Doe, Jane Smith"

def test_extract_keywords(pdf_service):
    text = "Keywords: Machine Learning, AI, Data Science"
    keywords = pdf_service.extract_keywords(text)
    assert keywords == "Machine Learning, AI, Data Science"

def test_clean_metadata(pdf_service):
    metadata = {
        'modDate': '2023-01-01',
        'producer': 'Producer',
        'creator': 'Creator',
        'creationDate': '2023-01-01'
    }
    text = "See discussions, stats, and author profiles for this publication at: https://www.researchgate.net/publication/377396514\nActive Inference for AI\nConference Paper "
    "· January 2024\nCITATIONS\n0\nREADS\n137\n1 author:\nMaria Raffa\nIULM Libera Università di Lingue "
    "e Comunicazione di Milano\n4 PUBLICATIONS\xa0\xa0\xa00 CITATIONS\xa0\xa0\xa0\nSEE PROFILE\nAll content following this page was uploaded "
    "by Maria Raffa on 14 January 2024.\nThe user has requested enhancement of the downloaded file.\n1 authors: John Doe, Jane Smith"

    cleaned_metadata = pdf_service.clean_metadata(metadata, text, text)
    assert 'modDate' not in cleaned_metadata
    assert 'producer' not in cleaned_metadata
    assert 'creator' not in cleaned_metadata
    assert 'creationDate' not in cleaned_metadata
    assert cleaned_metadata['source'] == "https://www.researchgate.net/publication/377396514"
    assert cleaned_metadata['title'] == "Active Inference for AI"
    assert 'uploaded_at' in cleaned_metadata

def test_generate_id(pdf_service):
    content = "Retrieval-Augmented Generation RAG"
    _id = pdf_service.generate_id(content)
    assert isinstance(_id, str)
    assert len(_id) == 36  # UUID length
