routes_store.py
import yaml
from typing import Dict
from pydantic import BaseModel
from pathlib import Path

CONFIG_PATH = Path("config.yaml")

class Route(BaseModel):
    name: str
    url: str

class RouteStore:
    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.routes: Dict[str, str] = {}
        self.load_from_yaml()

    def load_from_yaml(self):
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f) or {}
                self.routes = {k: v["url"] for k, v in data.get("routes", {}).items()}

    def save_to_yaml(self):
        data = {"routes": {k: {"url": v} for k, v in self.routes.items()}}
        with open(self.config_path, "w") as f:
            yaml.safe_dump(data, f)

    def get(self, service: str) -> str | None:
        return self.routes.get(service)

    def set(self, name: str, url: str):
        self.routes[name] = url
        self.save_to_yaml()

    def delete(self, name: str):
      if name in self.routes:
          del self.routes[name]
          self.save_to_yaml()

    def all(self):
        return self.routes

store = RouteStore()


admin_routes.py
from fastapi import APIRouter
from routes_store import store, Route

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

@admin_router.get("/routes")
def get_routes():
    return store.all()

@admin_router.post("/routes")
def add_route(route: Route):
    store.set(route.name, route.url)
    return {"status": "ok", "routes": store.all()}

@admin_router.delete("/routes/{name}")
def delete_route(name: str):
    store.delete(name)
    return {"status": "deleted", "routes": store.all()}


main.py
from fastapi import FastAPI
from router import router
from admin_routes import admin_router

app = FastAPI(title="Dynamic API Gateway")

app.include_router(router, prefix="/api")
app.include_router(admin_router)


router.py

from fastapi import APIRouter, Request, Response
import httpx
from routes_store import store

router = APIRouter()

@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    target = store.get(service)
    if not target:
        return Response(content=f"Unknown service: {service}", status_code=404)
    
    target_url = f"{target}/{path}"
    async with httpx.AsyncClient() as client:
        req = client.build_request(
            method=request.method,
            url=target_url,
            headers=request.headers.raw,
            content=await request.body()
        )
        resp = await client.send(req, stream=True)
        return Response(
            content=await resp.aread(),
            status_code=resp.status_code,
            headers=resp.headers
        )
