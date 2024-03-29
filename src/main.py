import fastapi
import uvicorn

from contacts import routes


contacts = fastapi.FastAPI()

contacts.include_router(routes.router)

if __name__ == "__main__":
    uvicorn.run("main:contacts", host="127.0.0.1", port=8000, reload=True)
