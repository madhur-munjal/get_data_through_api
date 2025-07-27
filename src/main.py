from fastapi import FastAPI

from src.routers import api_router

app = FastAPI(title="api_to_get_data",
              description="",
              version="0.0.1",
              contact={
                  "name": "Madhur Munjal",
                  # "url": "",
                  # "email": ""
              },
              root_path="/src",)

app.include_router(api_router.router)


@app.get("/")
async def status():
    """

    :return:
    """
    return {"status": "online"}
