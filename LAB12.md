# Laboratorio 12 Ajax y Servicios Web

**Estudiante:** Diego Magallanes Linares. **Equipo:** individual, un integrante.
**Rama:** `lab09-react`. Revisión de entrega: 15 de noviembre de 2026.

La [guía del campus](https://campus.tecnologia/) y el API del curso se unen en el laboratorio
12: el backend de Django habilita CORS para el origen del frontend y el frontend consume la API real
con **Axios** (listado, creación y borrado de exámenes), con los tres estados de una petición.

## Procedencia y trabajo realizado

- Se instaló `django-cors-headers==4.7.0` en el backend y se registró la app `corsheaders` y su
  middleware (después de `SecurityMiddleware`) en `config/settings.py`.
- Se declararon los orígenes permitidos `http://localhost:5173` y `http://127.0.0.1:5173` en
  `CORS_ALLOWED_ORIGINS`.
- Se añadió la dependencia a `requirements.txt`.
- El backend responde `200 OK` con `Access-Control-Allow-Origin` para el origen del frontend y
  responde preflight `OPTIONS` a `POST /api/exams/`.
- El frontend del laboratorio 11 (`lab11-hooks/`) cambió de la red simulada a la **API real**:
  cliente Axios único (`API_BASE_URL` + token en `Authorization: Token ...`).
- Se implementó el CRUD de exámenes contra `http://127.0.0.1:8008/api/exams/`: listado, creación y
  borrado.
- Se implementó el hook `useExams` con los tres estados (`loading`, `ready`, `error`) y `reload`.
- Se implementó la lista (`ExamsList`) con las filas reales, el borrado y el estado vacío.
- Se implementó el formulario (`ExamForm`) con entrada controlada, `preventDefault`, cuerpo `POST`,
  validación (cliente y error de la API) y vuelta a la lista.

## Verificación

- Backend: `python manage.py check` sin errores; `python manage.py test` → **100 tests OK**.
- Frontend: `npm test` → **72 tests OK** (57 de la entrega anterior + 15 nuevos del lab 12);
  `npm run build` compila correctamente.
- CORS verificado en caliente: el backend responde `Access-Control-Allow-Origin` para
  `http://localhost:5173` y acepta el preflight de `POST /api/exams/`.

## Uso local

```powershell
cd C:\Users\Magal\OneDrive\Documentos\ChatGPT\Django
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8008

cd lab11-hooks
npm run dev        # http://localhost:5173
```

El token de la persona se guarda en `localStorage` (`dae-s11-token`); el backend expone los tokens
del seed (`profe` y `agente`) en `/api/docs/`.

## Entregables

- `deliverables/lab12/Lab12_Diego_Magallanes_Linares.docx`
- `deliverables/lab12/Lab12_codigo.zip`
- `deliverables/lab12/evidence/`
- `LAB12.md`
