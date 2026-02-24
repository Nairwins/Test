from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import qrcode
from io import BytesIO

app = FastAPI(title="QR Code Generator API")

@app.get("/generate-qr")
async def generate_qr(
    data: str = Query(..., description="The text or URL to encode in the QR code"),
    fill_color: str = Query("black", description="Color of the QR code"),
    back_color: str = Query("white", description="Background color")
):
    """
    Generates a QR code image based on the provided data string.
    """
    # Configure the QR code parameters
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data to the instance
    qr.add_data(data)
    qr.make(fit=True)

    # Create the image (PIL object)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    # Save the image to a buffer (in-memory) instead of a file
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Return the buffer as a streaming response
    return StreamingResponse(buffer, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)