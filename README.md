# EcclesiaSys

Sistema de gestión parroquial desarrollado con:

- Frontend: Angular
- Backend: FastAPI
- RAG: FastAPI + LangChain

---

# Requisitos

- Python 3.12+
- Node.js 20+
- Angular CLI
- Git

---

# Estructura

```
Proyecto/
│
├── Frontend/
├── Backend/
├── RAG/
└── README.md
```

---

# Frontend

## Activar

```bash
cd Frontend
npm install
ng serve
```

El frontend estará disponible en:

```
http://localhost:4200
```

---

# Backend

## Crear entorno virtual (solo la primera vez)

```bash
cd Backend

python -m venv .venv
```

## Activar entorno virtual

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn app.main:app --reload
```

Disponible en:

```
http://localhost:8000
```

---

# RAG

## Crear entorno virtual (solo la primera vez)

```bash
cd RAG

python -m venv .venv
```

## Activar entorno virtual

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn app.main:app --reload --port 8100
```

Disponible en:

```
http://localhost:8100
```

---

# Variables de entorno

Cada módulo utiliza su propio archivo `.env`.

```
Backend/.env
Frontend/.env
RAG/.env
```

Estos archivos no se incluyen en el repositorio por motivos de seguridad.

---

# Tecnologías

- Angular
- FastAPI
- Python
- SQLAlchemy
- LangChain
- ChromaDB
