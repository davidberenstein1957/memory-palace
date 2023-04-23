from fastapi import FastAPI

app = FastAPI()

@app.get()
def health():
    return True


