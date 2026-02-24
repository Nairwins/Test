import io
import os
import uuid
import traceback
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional

# Importing your custom logic from the local directory
try:
    from script.code import generate_custom_qr
except ImportError:
    from api.script.code import generate_custom_qr

app = FastAPI(
    title="Pro QR Generator API",
    description="Custom QR generator with shapes and gradients."
)

@app.get("/")
async def home():
    return {"status": "online", "message": "Access /docs for the API interface."}

@app.post("/generate")
async def generate_qr(
    data: str = Form(..., description="The URL or text for the QR code"),
    body_shape: str = Form("default"),
    body_color: str = Form("black"),
    body_gradient_color: Optional[str] = Form(""),
    body_gradient_type: str = Form("radial"),
    innereye_shape: str = Form("default"),
    innereye_color: Optional[str] = Form(""),
    outereye_shape: str = Form("default"),
    outereye_color: Optional[str] = Form(""),
    icon_name: Optional[str] = Form(""),
    icon_file: Optional[UploadFile] = File(None),
    size: int = Form(10, ge=1, le=50),
    border: int = Form(4, ge=0, le=10)
):
    unique_id = uuid.uuid4()
    # Vercel ONLY allows writing to the /tmp directory
    output_filename = f"/tmp/out_{unique_id}.png"
    temp_upload_path = None

    try:
        # Handle Icon Upload if provided
        final_icon_path = icon_name
        if icon_file and icon_file.filename:
            temp_upload_path = f"/tmp/upload_{unique_id}_{icon_file.filename}"
            with open(temp_upload_path, "wb") as f:
                content = await icon_file.read()
                f.write(content)
            final_icon_path = temp_upload_path

        # Generate the QR code using your custom script
        generate_custom_qr(
            data                = data,
            output_path         = output_filename,
            body_shape          = body_shape,
            body_color          = body_color,
            body_gradient_color = body_gradient_color,
            body_gradient_type  = body_gradient_type,
            innereye_color      = innereye_color if innereye_color else body_color,
            outereye_color      = outereye_color if outereye_color else body_color,
            innereye_shape      = innereye_shape,
            outereye_shape      = outereye_shape,
            icon_path           = final_icon_path,
            size                = size,
            border              = border
        )

        # Check if the file was actually created
        if not os.path.exists(output_filename):
            raise HTTPException(status_code=500, detail="QR generation failed to create file.")

        # Read the file into a BytesIO buffer (mimicking your working code)
        buffer = io.BytesIO()
        with open(output_filename, "rb") as f:
            buffer.write(f.read())
        
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="image/png")

    except Exception as e:
        print("--- VERCEL ERROR LOG ---")
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=f"Runtime Error: {str(e)}")

    finally:
        # Cleanup: Delete the temp files immediately after streaming
        if output_filename and os.path.exists(output_filename):
            os.remove(output_filename)
        if temp_upload_path and os.path.exists(temp_upload_path):
            os.remove(temp_upload_path)

# Ensure Vercel can find the app
app = app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)