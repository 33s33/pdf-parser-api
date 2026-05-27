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
async def parse_pdf(
    file: UploadFile = File(...),
    start_page: int = 0,
    max_pages: int = 25
):

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        content = await file.read()
        tmp.write(content)

    pages = []
    bad_pages = []

    try:
        with pdfplumber.open(tmp_path) as pdf:
             total_pages = len(pdf.pages)
             end_page = min(start_page + max_pages, total_pages)

        for i in range(start_page, end_page):
            page_num = i + 1
            page = pdf.pages[i]

                pages.append({
                    "page": page_num,
                    "chars": len(text),
                    "text_preview": text[:500],
                })

                if len(text.strip()) < 50:
                    bad_pages.append(page_num)

        return {
            "filename": file.filename,
            "total_pages": total_pages,
            "processed_pages": limit,
            "bad_pages_count": len(bad_pages),
            "bad_pages_preview": bad_pages[:50],
            "pages_preview": pages,
            "start_page": start_page,
            "end_page": end_page,
            "processed_pages": end_page - start_page,
        }

    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
