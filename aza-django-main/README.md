# Monitoreo de capturas de trefilado · Aceros AZA

Aplicación Django que muestra las mediciones originales de `METRICAS_CONSOLIDADAS`.
El archivo `METRICAS_CONSOLIDADAS.zip` contiene 859 capturas JSON registradas entre el
14 y el 21 de julio de 2026. De ellas, 128 incluyen un ángulo de salida y 731 no
incluyen esa medición. La aplicación conserva esta diferencia y no asigna estados
«aprobado» o «rechazado» a estos datos: los JSON no contienen límites de tolerancia,
receta ni lote.

## Puesta en marcha

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Complete `DATABASE_URL` en `.env` con la cadena del Session pooler de Supabase.
El arranque normal requiere PostgreSQL y el esquema `aza`. Cuando la base ya está
inicializada, compruebe la conexión y ejecute el servidor de desarrollo.

```powershell
& .\.venv\Scripts\python.exe manage.py verificar_base_datos
& .\.venv\Scripts\python.exe manage.py runserver
```

Abra `http://127.0.0.1:8000/` en el navegador del mismo equipo.

## Cuentas de usuario

Credenciales de demostraci?n para la revisi?n del proyecto:

| Usuario | Rol | Contrase?a | Estado |
|---|---|---|---|
| `admin_prueba` | Administrador | `AzatC96oLAAsb1a9` | Activo |
| `operador_prueba` | Operador | `Aza0YIa4xOfDGZC9` | Activo |
| `richi` | Operador | `AzaGzLjOV4NOIRf9` | Inactivo |
| `supervisor_prueba` | Supervisor | `AzaF3EBQj0A76QK9` | Activo |

Estas cuentas son solo para demostraci?n. No reutilice esas contrase?as en otros
sistemas y c?mbielas o desactive las cuentas al terminar la revisi?n.
## Datos reales

- `/operador/panel/`: últimas capturas, con «Sin medición» donde el JSON no trae ángulo.
- `/supervisor/dashboard/`: total de capturas, cobertura y rango de ángulos
  disponibles, capturas por día y confianza reportada por el análisis.
- `/supervisor/historial/`: filtros por fecha y presencia de ángulo; exportación
  CSV con todos los campos originales.
- `/captura/<id>/`: detalle de una captura. La ruta de diagnóstico es una referencia al
  equipo de origen; las imágenes de diagnóstico no están incluidas en el ZIP.
- `/administracion/control/`: resumen de capturas reales y alertas de seguridad.

La importación es repetible: `python manage.py importar_metricas` actualiza cada captura
por nombre de archivo y evita duplicados. Acepta una carpeta o ZIP con
`--source <ruta>`. Por defecto lee la carpeta extraída si existe y, en caso contrario,
`METRICAS_CONSOLIDADAS.zip`. Ambos archivos de origen se mantienen fuera del repositorio.
La importación a PostgreSQL de Supabase se hace una sola vez desde el equipo local.

En [SQL Editor de Letterboxd](https://supabase.com/dashboard/project/hxgewarawsnhttcxpnhw/sql/new),
consulte las capturas con el nombre completo del esquema:

```sql
SELECT archivo_origen, fecha_hora, scene, exit_angle_deg
FROM aza.trefilado_metricacaptura
ORDER BY fecha_hora DESC
LIMIT 50;
```

Para contrastar los totales del panel y la base:

```sql
SELECT COUNT(*) AS total, COUNT(exit_angle_deg) AS con_angulo
FROM aza.trefilado_metricacaptura;
```

## Supabase y despliegue

El proyecto **Letterboxd** de Supabase tiene un esquema privado `aza` para esta
aplicación. Las tablas existentes de Letterboxd en `public` no se borran ni se usan.
El esquema `aza` no concede acceso a los roles `anon` y `authenticated` de la API.

Para conectar Django, abra [Connect de Letterboxd](https://supabase.com/dashboard/project/hxgewarawsnhttcxpnhw?showConnect=true&method=session), elija **Session pooler** y copie la
cadena PostgreSQL del puerto **5432**. En el archivo local `.env`, reemplace
`DATABASE_URL=` por esa cadena con la contraseña real en lugar de
`[YOUR-PASSWORD]`. Si la contraseña contiene caracteres reservados de URL,
codifíquelos. No comparta la contraseña en el chat ni suba `.env` al repositorio.
`DB_SCHEMA=aza` ya está preparado. `python manage.py verificar_base_datos` muestra
el motor, el esquema, la referencia del proyecto si reconoce el Session pooler y
los totales de capturas y usuarios. El comando devuelve un error si la conexión
activa no usa PostgreSQL con `aza`. Si muestra «Proyecto Supabase: no identificable»,
compare el proyecto configurado en cada equipo por un canal seguro.

La URL de ejemplo utiliza el rol `postgres`, que también tiene permisos sobre las
tablas de Letterboxd. Guarde esa URL maestra para tareas de administración y evite
distribuirla a otros equipos. Antes de desplegar AZA, configure un usuario de base de
datos limitado al esquema `aza` y actualice `DATABASE_URL` con ese usuario.

En un despliegue central, el servicio Django guarda las credenciales de conexión
y cada equipo abre la misma URL desde el navegador. Para publicar en Render, suba este proyecto a un repositorio Git conectado a su
cuenta y cree un Blueprint seleccionando ese repositorio. Render leera
`render.yaml`, instalara dependencias, recopilara los archivos estaticos y ejecutara
las migraciones antes de iniciar Gunicorn. El Blueprint genera `SECRET_KEY` y
configura `DEBUG=0` y `DB_SCHEMA=aza`.

Al crear el servicio, ingrese `DATABASE_URL` con la cadena Session pooler de
Supabase, el puerto 5432 y el usuario/clave de base de datos con permisos sobre
el esquema `aza`. El servicio inicia sin SMTP, pero la recuperacion por correo queda deshabilitada
hasta configurar `EMAIL_HOST`, `EMAIL_HOST_USER`,
`EMAIL_HOST_PASSWORD` y `DEFAULT_FROM_EMAIL`. Render Free bloquea los puertos SMTP
25, 465 y 587; use un proveedor con STARTTLS en un puerto permitido, por ejemplo
2525, y ajuste `EMAIL_PORT` si corresponde.
Si utiliza el endpoint de captura, ingrese un secreto aleatorio en
`API_TOKEN_CAPTURA`; si se deja vacio, ese endpoint permanece deshabilitado.

Despues del primer despliegue, Render entrega la URL publica `onrender.com` con
HTTPS. Django detecta esa URL automaticamente. Los servicios Free pueden dormirse
tras inactividad y no conservan archivos locales entre despliegues; las evidencias
subidas requieren almacenamiento persistente en un plan compatible para conservarse.
La base PostgreSQL de Supabase permanece separada y mantiene los datos.

Si ejecuta Django en varias máquinas, configure cada instancia para conectarse a
la misma base PostgreSQL y al esquema `aza`. Verifique cada instancia con
`verificar_base_datos`. Para servir una sola URL con varias réplicas, use la misma
`SECRET_KEY` y la misma configuración de URL pública en todas ellas. Reserve
`DEBUG=1` para acceso local. Toda instancia con la base compartida que quede
accesible a terceros debe usar `DEBUG=0`.

Los archivos adjuntos de evidencia se guardan en `MEDIA_ROOT`, en el sistema de
archivos de la instancia que los recibe. PostgreSQL comparte las referencias a esos
archivos. Para conservar los adjuntos después de un reinicio o compartirlos entre
instancias, se necesita almacenamiento persistente y accesible desde todas ellas.
Los respaldos de PostgreSQL se gestionan en Supabase. El respaldo de archivos de
la aplicación solo está disponible en modo SQLite.

La API `/api/inspecciones/` y la gestión de recetas/lotes pertenecen al flujo de
captura por lote. Cada petición de inspección debe incluir `operador` con el nombre
de usuario de una cuenta activa con rol Operador, además del ángulo y lote:

```json
{"angulo": 12.5, "lote": "LOTE-001", "receta": 1, "operador": "operador_prueba"}
```

El endpoint valida que el operador exista y esté activo. El nombre indicado sirve
como atribución del registro; el token de API no autentica individualmente a esa
persona. Las inspecciones anteriores a este cambio quedan sin operador asociado.
En Histórico, el Supervisor puede descargar **Informe de gestión Excel**, con
resúmenes comparativos por receta y por lote/receta aplicada. Incluye material,
operadores, período (año/mes/día), total, aprobadas, rechazadas, porcentaje de
aprobación y promedio circular del ángulo. El rango de fechas seleccionado aplica
al informe; se excluyen las capturas sin ángulo o sin asociaciones de gestión. El
Administrador no tiene acceso a este informe. El CSV de métricas originales sigue
disponible por separado.

Los JSON consolidados no traen lote, operador ni receta. Las asociaciones usadas en
el informe se guardan opcionalmente en `MetricaCaptura`; las capturas sin vínculo no
se asignan automáticamente a un lote o receta. Al importar JSON, una captura se
asocia al lote y receta cuando existe exactamente un lote para su fecha; si hay
cero o varios lotes ese día, queda sin vínculo para evitar una atribución ambigua.

Los Administradores ingresan con usuario y contraseña; cambie cualquier contraseña temporal antes de usar el servicio.
`API_TOKEN_CAPTURA`. El proyecto Supabase contiene tablas previas en `public` sin
RLS; deben revisarse por separado antes de utilizar su Data API.



la base se conecta asi se tiene que ver

"
DATABASE_URL=<cadena Session pooler configurada de forma privada>
DB_SCHEMA=aza
"
