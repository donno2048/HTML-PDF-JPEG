from io import BytesIO
from struct import pack
from PIL import Image, ImageDraw
def text2html(text: bytes) -> bytes:
    return b"<html><head><style>body{visibility:hidden}div{visibility:visible}</style></head><body><div>" + text + b"</div></body></html>"
def text2pdf(text: bytes, fontsize: int = 100) -> bytes:
    return b"1 0 obj << /Type /Catalog /Pages << /Type /Pages /Kids [ << /Type /Page /Contents <<>> stream\n/F1 " + str(fontsize).encode() + b" Tf (" + text + b") Tj endstream >> ] /Count 1 >> >> endobj trailer << /Root 1 0 R >>"
def text2jpeg(text: bytes, width: int = 100, height: int = 100, x: int = 0, y: int = 0) -> bytes:
    out = BytesIO()
    img = Image.new("1", (width, height), 1)
    ImageDraw.Draw(img).text((x, y), text.decode(), fill=0)
    img.save(out, format="JPEG")
    return out.getvalue()
def embed(html: bytes, pdf: bytes, jpeg: bytes) -> bytes:
    offset = jpeg[jpeg.find(b"F"):].find(0xFF) + jpeg.find(b"F")
    return jpeg[:offset] + b"\xff\xfe" + pack(">h", len(pdf) + len(html) + 11) + html + b"<!--%PDF\n" + pdf + jpeg[offset:]
def main(html: bytes, pdf: bytes, jpeg: bytes, outfile: str) -> bytes:
    open(outfile, "wb").write(embed(text2html(html), text2pdf(pdf), text2jpeg(jpeg)))
main(b"HTML", b"PDF", b"JPEG", "main.html")
main(b"HTML", b"PDF", b"JPEG", "main.pdf")
main(b"HTML", b"PDF", b"JPEG", "main.jpeg")
