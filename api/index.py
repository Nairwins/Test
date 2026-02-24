from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import segno
from io import BytesIO

app = FastAPI()

@app.get("/")
def home():
    return {"status": "QR Generator is running", "docs": "/docs"}

@app.get("/generate-qr")
async def generate_qr(
    data: str = Query(..., description="The text or URL to encode"),
    color: str = Query("black", description="Hex or name color for the dark modules"),
    bg_color: str = Query("white", description="Background color"),
    scale: int = Query(10, description="Scale of the QR code")
):
    """
    Generates a QR code using Segno and returns it as a PNG.
    """
    # Create the QR code
    qr = segno.make(data)
    
    # Create an in-memory buffer
    buffer = BytesIO()
    
    # Save to buffer as PNG
    # Note: Segno handles the 'scale' and colors natively
    qr.save(
        buffer, 
        kind="png", 
        dark=color, 
        light=bg_color, 
        scale=scale
    )
    
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="image/png")