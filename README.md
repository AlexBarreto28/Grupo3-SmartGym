# SmartGym API

API REST desarrollada con FastAPI para la gestión integral de gimnasios. El sistema permite administrar usuarios, roles, clientes, entrenadores, máquinas, clases, reservas, membresías, pagos, control de acceso, mantenimiento y ventas de productos.

La API implementa autenticación mediante JWT, control de acceso basado en roles (RBAC) y documentación automática con Swagger/OpenAPI.

---

## Tecnologías utilizadas

* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic
* JWT Authentication
* Swagger / OpenAPI
* Docker

---

## Estructura del proyecto

```text
.
├── alembic/
│
├── app/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── scripts/
│   └── seed.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Configuración

Crear un archivo `.env` tomando como referencia el archivo `.env.example`.

```env
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_password
POSTGRES_DB=nombre_db

DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=tu_llave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/laboratorio-1-2026-1/lab1-proyecto-2026-1-32023320-30754077-30716524.git
cd lab1-proyecto-2026-1-32023320-30754077-30716524
```

### 2. Crear entorno virtual

**Windows**

```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux / Mac**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

Crear una base de datos PostgreSQL y configurar correctamente las variables del archivo `.env`.

### 5. Ejecutar datos iniciales

**Windows**

```powershell
$env:PYTHONPATH="."
.\venv\Scripts\python.exe scripts\seed.py
```

El script de inicialización crea automáticamente:

* Roles del sistema.
* Usuarios de prueba.
* Categorías de máquinas.
* Máquinas de ejemplo.
* Disciplinas.
* Sesiones programadas.
* Reservas.
* Membresías.
* Pagos.
* Productos.
* Ventas.
* Evaluaciones biométricas.
* Registros de acceso.
* Tickets de mantenimiento.

---

## Usuarios de prueba

### Administrador

```text
Email: admin@gym.com
Password: Admin123*
```

### Entrenador

```text
Email: carlos@gym.com
Password: Entrenador123*
```

### Cliente

```text
Email: manuel@gym.com
Password: Cliente123*
```

### Finanzas

```text
Email: ana@gym.com
Password: Finanzas123*
```

---

## Ejecución

Iniciar el servidor:

```bash
uvicorn app.main:app --reload
```

La aplicación estará disponible en:

```text
http://127.0.0.1:8000
```

---

## Documentación de la API

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Desde Swagger es posible consultar y probar todos los endpoints disponibles de la API.

---

## Autenticación

La API utiliza autenticación basada en JSON Web Tokens (JWT).

### Obtener token

Endpoint:

```http
POST /api/v1/auth/login
```

Ejemplo de solicitud:

```json
{
  "email": "admin@gym.com",
  "password": "Admin123*"
}
```

Respuesta:

```json
{
  "access_token": "token_jwt",
  "token_type": "bearer"
}
```

### Usar el token

1. Iniciar sesión utilizando el endpoint de login.
2. Copiar el valor de `access_token`.
3. Abrir Swagger (`/docs`).
4. Presionar el botón **Authorize**.
5. Pegar el token recibido.
6. Ejecutar los endpoints protegidos.

---

## Migraciones

El proyecto utiliza Alembic para el control de migraciones de base de datos.

Crear una migración:

```bash
alembic revision --autogenerate -m "descripcion"
```

Aplicar migraciones:

```bash
alembic upgrade head
```

---

## Características principales

* Autenticación mediante JWT.
* Control de acceso basado en roles (RBAC).
* Gestión de usuarios, clientes y entrenadores.
* Gestión de máquinas y categorías.
* Programación y reserva de clases.
* Gestión de membresías y pagos.
* Registro de accesos al gimnasio.
* Seguimiento biométrico de clientes.
* Gestión de productos y ventas.
* Registro de mantenimiento de máquinas.
* Validaciones de negocio para reservas, membresías y control de acceso.
* Documentación automática mediante Swagger/OpenAPI.

---

## Integrantes

| Nombre | Cédula |
|----------|----------|
| Alex Barreto | 32.023.320 |
| Manuel Fuentes | 30.754.077 |
| José Alaña | 30.716.524 |

Universidad Centroccidental Lisandro Alvarado (UCLA)
Laboratorio I — 2026-1
