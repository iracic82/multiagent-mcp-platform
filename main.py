from fastapi import FastAPI
from routers import subnet

app = FastAPI(title="FastMCP Subnet Calculator")
app.include_router(subnet.router)