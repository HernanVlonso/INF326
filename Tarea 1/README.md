# Tarea 1 INF326 Arquitectura de Software

Este proyecto despliega dos nano-servicios en **FastAPI** con logging estructurado en JSON.  
Los logs se envían mediante **Promtail** a **Loki**, y se visualizan en **Grafana**.  
Todo está desplegado mediante **Docker Compose**.

Uno de los nano servicios permite revisar su estado y mostrar un saludo de prueba, el otro permite realizar operaciones matemáticas tales como el doble de un número, el factorial de un número y el enésimo número de la succesión de Fibonacci.

---

## Contenido del proyecto
- **docker-compose.yml**: Contendores `app1`, `app2`, `loki`, `promtail`, `grafana`.
- **services/app1/**: Servicio FastAPI `app1`
  - Endpoints:
    - `GET /`: estado
    - `GET /saludo`: saludo de prueba
- **services/app2/**: Servicio FastAPI `app2`
  - Endpoint:
    - `POST /calcular`: operaciones `doble`, `factorial` y `fibonacci`
- **promtail/config.yml**: Configuración de Promtail.
- **grafana/provisioning/**: Datasource Loki y dashboard.

**Puertos expuestos:**
- **app1**: http://localhost:8001
- **app2**: http://localhost:8002
- **Loki**: http://localhost:3100
- **Grafana**: http://localhost:3000 (usuario: `admin`, password: `admin`)

---

## Inicio
```powershell
cd Tarea 1
docker compose build
docker compose up -d
docker compose ps
```

Luego de esto `app1`, `app2`, `loki`, `promtail`, `grafana` estarán en estado `running`.

---

## Probar los servicios

### app1

#### PowerShell
```powershell
Invoke-RestMethod -Uri "http://localhost:8001/" -Method Get
Invoke-RestMethod -Uri "http://localhost:8001/saludo" -Method Get
```

#### Linux
```bash
curl -s http://localhost:8001/
curl -s http://localhost:8001/saludo
```

---

### app2

#### PowerShell
```powershell
# Doble
Invoke-RestMethod -Uri "http://localhost:8002/calcular" -Method Post -ContentType "application/json" -Body '{"operacion":"doble","valor":21}'

# Factorial
Invoke-RestMethod -Uri "http://localhost:8002/calcular" -Method Post -ContentType "application/json" -Body '{"operacion":"factorial","valor":6}'

# Fibonacci
Invoke-RestMethod -Uri "http://localhost:8002/calcular" -Method Post -ContentType "application/json" -Body '{"operacion":"fibonacci","valor":12}'
```

#### Linux
```bash
curl -s -X POST http://localhost:8002/calcular -H "Content-Type: application/json" -d '{"operacion":"doble","valor":21}'
curl -s -X POST http://localhost:8002/calcular -H "Content-Type: application/json" -d '{"operacion":"factorial","valor":6}'
curl -s -X POST http://localhost:8002/calcular -H "Content-Type: application/json" -d '{"operacion":"fibonacci","valor":12}'
```

---

## Ver logs en Grafana
1. Se debe abrir [http://localhost:3000](http://localhost:3000) (usuario: `admin`, password: `admin`).
2. Ir a **Explore** y seleccionar fuente **Loki**.
3. Ejecutar consultas:
   - Logs de `app1`:  
     ```
     {compose_service="app1"} | json | event=~"estado|ping|saludo|http_request"
     ```
   - Logs de `app2`:  
     ```
     {compose_service="app2"} | json | event="calcular"
     ```
4. También se puede abrir el dashboard:  
   - **Ir a Dashboards y luego a Logs de dos nano servicios**.

---

## Notas
- `valor` debe ser entero `>= 0`.
- Factorial tiene como límite máximo `10000`.
- Fibonacci tiene como límite máximo `100000`.

---

## Cierre
```powershell
docker compose down -v
```

---
