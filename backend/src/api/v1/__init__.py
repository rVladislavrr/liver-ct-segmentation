from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import routers

http_bearer = HTTPBearer(auto_error=False)

async def for_documentation(api_key: HTTPAuthorizationCredentials = Depends(http_bearer)):
    pass
router = APIRouter(prefix="/v1", dependencies=[Depends(for_documentation)])

router.include_router(routers.files)
router.include_router(routers.auth)
router.include_router(routers.photos)
router.include_router(routers.contours)