import os
import tempfile
from typing import List

import pdfplumber
from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.get("/")
def healthcheck():
    return {"status": "ok", "service": "pdf-parser-api"}


@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)):
    suffix = ".pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        content = await file.read()
        tmp.write(content)

    pages = []
    bad_pages = []

    try:
        with pdfplumber.open(tmp_path) as pdf:
            total_pages = len(pdf.pages)

            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""

                pages.append({
                    "page": i,
                    "chars": len(text),
                    "text_preview": text[:500],
                })

                if len(text.strip()) < 50:
                    bad_pages.append(i)

        return {
            "filename": file.filename,
            "total_pages": total_pages,
            "bad_pages_count": len(bad_pages),
            "bad_pages_preview": bad_pages[:50],
            "pages_preview": pages[:10],
        }

    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
