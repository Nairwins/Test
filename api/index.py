import io
import os
import uuid
import traceback
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional

from script.engine import generate_custom_qr

app = FastAPI(
    title="Pro QR Generator API",
    description="API wrapper for the custom QR generator."
)


@app.get("/")
async def home():
    return {"status": "online", "message": "Access /docs for the API interface."}


@app.post("/generate")
async def generate_qr(
    data: str                          = Form(...),
    body_shape: str                    = Form("default"),
    body_color: str                    = Form("black"),
    body_gradient_color: Optional[str] = Form(""),
    body_gradient_type: str            = Form("radial"),
    innereye_shape: str                = Form("default"),
    innereye_color: Optional[str]      = Form(""),
    outereye_shape: str                = Form("default"),
    outereye_color: Optional[str]      = Form(""),
    icon_name: Optional[str]           = Form(""),
    icon_file: Optional[UploadFile]    = File(None),
    size: int                          = Form(10, ge=1, le=50),
    border: int                        = Form(4, ge=0, le=10),
    format: str                        = Form("png"),  # "png" or "svg"
):
    unique_id        = uuid.uuid4()
    temp_upload_path = None

    try:
        # ── Resolve icon ─────────────────────────────────────
        final_icon_path = icon_name or None
        if icon_file and icon_file.filename:
            temp_upload_path = f"/tmp/upload_{unique_id}_{icon_file.filename}"
            with open(temp_upload_path, "wb") as buf:
                buf.write(await icon_file.read())
            final_icon_path = temp_upload_path

        # ── Generate ─────────────────────────────────────────
        ext         = "svg" if format.lower() == "svg" else "png"
        output_path = f"/tmp/out_{unique_id}.{ext}"

        result = generate_custom_qr(
            data                = data,
            output_path         = output_path,
            body_shape          = body_shape,
            body_color          = body_color,
            body_gradient_color = body_gradient_color or None,
            body_gradient_type  = body_gradient_type,
            innereye_color      = innereye_color or None,
            outereye_color      = outereye_color or None,
            innereye_shape      = innereye_shape,
            outereye_shape      = outereye_shape,
            icon_path           = final_icon_path,
            size                = size,
            border              = border,
        )

        # ── Stream response ───────────────────────────────────
        if format.lower() == "svg":
            # result is an SVG string
            return StreamingResponse(
                io.BytesIO(result.encode("utf-8")),
                media_type="image/svg+xml",
            )
        else:
            # result is a PIL Image — convert to PNG bytes in memory
            buf = io.BytesIO()
            result.save(buf, "PNG")
            buf.seek(0)
            return StreamingResponse(buf, media_type="image/png")

    except Exception as e:
        print("--- ERROR ---")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Runtime Error: {str(e)}")

    finally:
        for p in [f"/tmp/out_{unique_id}.png", f"/tmp/out_{unique_id}.svg", temp_upload_path]:
            if p and os.path.exists(p):
                os.remove(p)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)