# This is a FastAPI application
import fastapi
app = fastapi.App()
@app.get("/factorial")
def factorial(n: int):
    # TO DO: implement factorial calculation
    pass