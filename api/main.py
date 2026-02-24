from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
import segno
import io
import uuid

app = FastAPI(
    title="Simple QR API",
    description="Generate QR codes (SVG) using FastAPI."
)

@app.get("/")
async def home():
    return {"status": "online", "message": "Use POST /generate to create QR codes."}

@app.post("/generate")
async def generate_qr(data: str = Form(...)):
    qr = segno.make(data, error="h")
    svg_io = io.BytesIO()
    qr.save(svg_io, kind="svg")
    svg_io.seek(0)
    filename = f"qr_{uuid.uuid4().hex}.svg"
    return StreamingResponse(svg_io, media_type="image/svg+xml", headers={"Content-Disposition": f"inline; filename={filename}"})