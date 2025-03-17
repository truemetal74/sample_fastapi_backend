from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field
from typing import Optional

from fastapi import FastAPI, APIRouter, Depends, Response, Request, Header, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import conint
from starlette.responses import StreamingResponse
from starlette.status import HTTP_204_NO_CONTENT
from app_config import AppConfig
from report_error import WebTritErrorException
from report_error import raise_webtrit_error
from request_trace import RouteWithLogging

class Health(BaseModel):
    status: Optional[str] = Field(
        None, description="A response from the server.", example="OK"
    )


VERSION = "0.1.0"
API_VERSION_PREFIX = "/api/v1"

my_project_path = os.path.dirname(__file__)
sys.path.append(my_project_path)

config = AppConfig()

app = FastAPI(
    description="""Econet.""",
    title="Sample adapter for connecting WebTrit to a Econet",
    version=VERSION,
    #    servers=[{'url': '/api/v1', 'variables': {}}],
)
security = HTTPBearer()

router = APIRouter(route_class=RouteWithLogging)

class SessionCreateRequest(BaseModel):
    username: str
    password: str
    device_id: Optional[str] = None
    device_name: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    expires_at: datetime
    user: dict  # You might want to create a separate UserModel for more specific typing
  

@app.get(
    "/api/health-check",
    response_model=Health,
)
def health_check() -> Health:
    """
    Confirm the service is running
    """
    return Health(status='OK')


@router.post(
    '/session',
    response_model=SessionResponse,
    responses={
    },
#    tags=['session'],
)
def create_session(
        body: SessionCreateRequest,
        # to retrieve user agent from the request
        request: Request,
        
) :
    """
    test
    """
    d = {}
    print(d["test"])
    raise Exception("test")
    return SessionResponse(session_id="123", expires_at=datetime.now(), user={"username": body.username})

app.include_router(router, prefix=API_VERSION_PREFIX)
