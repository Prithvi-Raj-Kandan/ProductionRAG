from fastapi import FastAPI , UploadFile
from typing import List

app = FastAPI()

@app.post("/upload_pdf")
async def upload_pdf(files: List[UploadFile]):
    return {"message": "Files uploaded successfully", "files": [file.filename for file in files]}

