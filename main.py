from io import BytesIO
from struct import pack
from zipfile import ZipFile
from PIL import Image, ImageDraw # pip install pillow

def text2html(text: bytes) -> bytes:
    return b"<html><head><style>body{visibility:hidden}div{visibility:visible}</style></head><body><div>" + text + b"</div>"
def text2pdf(text: bytes, fontsize: int = 100) -> bytes:
    return b"1 0 obj << /Type /Catalog /Pages << /Type /Pages /Kids [ << /Type /Page /Contents <<>> stream\n/F1 " + str(fontsize).encode() + b" Tf (" + text + b") Tj endstream >> ] /Count 1 >> >> endobj trailer << /Root 1 0 R >>"
def text2jpeg(text: bytes, width: int = 100, height: int = 100, x: int = 0, y: int = 0) -> bytes:
    out = BytesIO()
    img = Image.new("1", (width, height), 1)
    ImageDraw.Draw(img).text((x, y), text.decode(), fill=0)
    img.save(out, format="JPEG")
    return out.getvalue()
def dict2zip(zip: dict) -> bytes:
    out = BytesIO()
    with ZipFile(out, 'x') as Zip:
        for z in zip:
            Zip.writestr(z, zip[z])
    return out.getvalue()

def embed(html: bytes, pdf: bytes, jpeg: bytes, zip: bytes) -> bytes:
    offset = jpeg[jpeg.find(b"F"):].find(0xFF) + jpeg.find(b"F")
    return jpeg[:offset] + b"\xff\xfe" + pack(">h", len(html) + 29) + html + b"%PDF\n999 0 obj\n<<>>\nstream\n" + jpeg[offset:] + b"\xff\xd9\nendstream\nendobj\n" + pdf + b"\n%%EOF\n" + zip
def main(html: bytes, pdf: bytes, jpeg: bytes, zip: dict, outfile: str) -> bytes:
    open(outfile, "wb").write(embed(text2html(html), text2pdf(pdf), text2jpeg(jpeg), dict2zip(zip)))
text = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs" type="module"></script>
<script>
window.onload = () => {
    var { pdfjsLib } = globalThis;
    const canvas = document.getElementById('pdf');
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs';
    pdfjsLib.getDocument(window.location.href).promise.then(pdf =>
        pdf.getPage(1).then(page =>
            page.render({canvasContext: canvas.getContext('2d'), viewport: page.getViewport({scale: .1})})
        )
    );
};
</script>
This HTML page is also a valid PDF file, a valid ZIP archive and a valid JPEG image.<br>
If you download this HTML page and rename it to ".jpeg" you'll see this image:<br>
<img src=.><br>
And if you rename it to ".pdf" you'll see this PDF:<br>
<canvas id=pdf></canvas><br>
And finally, if you rename it to ".zip" you'll have an archive of the PDF and JPEG.
"""
main(text.replace("\n", "").encode(), b"PDF", b"JPEG", {
    "main.pdf": text2pdf(b"PDF"),
    "main.jpg": text2jpeg(b"JPEG"),
}, "index.html")
