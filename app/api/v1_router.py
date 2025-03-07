from fastapi.routing import APIRouter

from app.api.v1 import user, auth, call, assistant

routes = APIRouter(prefix="/v1")

routes.include_router(auth.routes)
routes.include_router(user.routes)
routes.include_router(call.routes)
routes.include_router(assistant.routes)
