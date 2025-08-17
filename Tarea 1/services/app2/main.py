from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging, math, time, uuid
from typing import Literal, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start = time.time()
        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = int((time.time() - start) * 1000)
            extra = {
                "event": "http_request",
                "method": request.method,
                "path": request.url.path,
                "status_code": getattr(response, "status_code", 500),
                "duration_ms": duration_ms,
                "request_id": request_id,
                "service": app.title,
            }
            root_logger.info("http_request", extra=extra)

app = FastAPI(title="app2", description="Servicio de cálculo: doble, factorial y fibonacci")
app.add_middleware(RequestLogMiddleware)
logger = logging.getLogger("app2")

class CalculoEntrada(BaseModel):
    operacion: Literal["doble", "factorial", "fibonacci"]
    valor: Optional[int] = Field(None, ge=0, description="Número entero >= 0")

def fibonacci(n: int) -> int:
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

def resolver(req: CalculoEntrada) -> int:
    if req.valor is None:
        raise HTTPException(400, "valor requerido")
    v = int(req.valor)
    if req.operacion == "doble":
        return v * 2
    if req.operacion == "factorial":
        if v > 10000:
            raise HTTPException(400, "valor demasiado grande para factorial")
        return math.factorial(v)
    if req.operacion == "fibonacci":
        if v > 100000:
            raise HTTPException(400, "valor demasiado grande para fibonacci")
        return fibonacci(v)
    raise HTTPException(400, "operacion no soportada")

@app.post("/calcular", summary="Calcula doble, factorial o fibonacci")
def calcular(req: CalculoEntrada):
    t0 = time.time()
    res = resolver(req)
    ms = int((time.time() - t0) * 1000)
    logger.info("calcular", extra={
        "event": "calcular",
        "operacion": req.operacion,
        "duracion_ms": ms,
        "service": "app2"
    })
    return {"resultado": res, "duracion_ms": ms}
