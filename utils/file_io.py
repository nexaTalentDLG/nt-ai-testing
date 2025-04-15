# utils/file_io.py

import io
from io import StringIO
import docx
import PyPDF2
import streamlit as st


def extract_text_from_file(uploaded_file):
    """
    Handles uploaded file and extracts raw text content based on file type.
    """
    if uploaded_file is None:
        return ""

    try:
        if uploaded_file.type == "text/plain":
            return StringIO(uploaded_file.getvalue().decode("utf-8")).read()

        elif uploaded_file.name.endswith(".docx"):
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            return "\n".join([para.text for para in doc.paragraphs])

        elif uploaded_file.name.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            return "\n".join([page.extract_text() for page in pdf_reader.pages])

        else:
            return "Unsupported file format. Please use .txt, .docx, or .pdf."

    except Exception as e:
        return f"Error processing file: {str(e)}"
