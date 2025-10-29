import fitz

# Extract text from file
async def parse_file(file):
    if file.filename.endswith(".pdf"):
        text = ""
        with fitz.open(stream=await file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif file.filename.endswith(".txt"):
        return (await file.read()).decode("utf-8")
    else:
        return None

# Split text into chunks
def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
