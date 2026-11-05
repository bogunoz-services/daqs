from fastapi import FastAPI

from api.v1.measurements import router as measurements_router
from api.v1.devices import router as devices_router

app = FastAPI(title="data-platform-service")

app.include_router(measurements_router)
app.include_router(devices_router)