
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.measurements import router as measurements_router
from api.v1.devices import router as devices_router
from infrastructure.database.init import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("APP: starting database initialization", flush=True)

    init_database()

    print("APP: database initialization completed", flush=True)
    yield


app = FastAPI(
    title="data-platform-service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(measurements_router)
app.include_router(devices_router)

# uvicorn app:app --reload --port 8000

@app.get("/cors-test")
async def cors_test():
    return {"status": "ok"}
