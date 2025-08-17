from fastapi import FastAPI
import logging, time, uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from pythonjsonlogger import jsonlogger

# --- Configuración de logging JSON ---
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

# --- Middleware para request logs ---
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

# --- FastAPI app ---
app = FastAPI(title="app1", description="Servicio app1 básico con logs JSON")
app.add_middleware(RequestLogMiddleware)
logger = logging.getLogger("app1")

@app.get("/", summary="Estado del servicio")
def estado():
    logger.info("estado", extra={"event": "estado", "service": "app1"})
    return {"servicio": "app1", "mensaje": "ok"}


@app.get("/saludo", summary="Saludo de prueba")
def saludo():
    logger.info("saludo", extra={"event": "saludo", "service": "app1"})
    return {"mensaje": "¡Hola desde app1!"}
