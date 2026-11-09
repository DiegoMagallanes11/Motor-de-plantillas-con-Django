# Laboratorio 09 Introducción a ReactJS

**Estudiante:** Diego Magallanes Linares. **Equipo:** individual, un integrante.
**Rama:** `lab09-react`. Documento revisado el 8 de noviembre de 2026.

La cartelera Cine Tecsup incluye ocho películas, afiches SVG locales,
clasificaciones, valoraciones, horarios y sinopsis desplegables. La guía del
campus y el [repositorio extra del docente](https://github.com/Hellscythe25/dae-s09-react-ia)
se resuelven juntos. No se usan estado ni hooks, conforme al README extra.

- [Guía resuelta en Word con conclusiones](deliverables/lab09/Lab09_Diego_Magallanes_Linares.docx).
- [Texto de referencia suministrado](deliverables/lab09/guia-referencia.txt).
- [Pruebas, mensajes y capturas reales](deliverables/lab09/evidence/).

## Instalar y ejecutar

El proyecto se creó con `npm create vite@latest frontend -- --template react --no-interactive`
(create-vite 9.3.4). Para repetir desde este repositorio, **no volver a generar**
la carpeta; instalar las versiones bloqueadas:

```powershell
git clone --branch lab09-react https://github.com/DiegoMagallanes11/Motor-de-plantillas-con-Django.git
cd Motor-de-plantillas-con-Django/frontend
node --version
npm ci
npm run dev
```

Abrir **http://localhost:5173/**. La configuración usa ese puerto de forma
estricta: si está ocupado, detener únicamente el servidor correspondiente antes
de volver a iniciar. El backend de Django se conserva en la raíz del repositorio;
no necesita estar encendido para este laboratorio de datos locales.

Se verificó con Node **24.15.0**, npm **11.12.1**, React y React DOM **19.3.1**,
Vite **8.3.6**, plugin-react **6.2.1**, Vitest **4.1.12**, jsdom **26.1.0** y
Testing Library React **16.3.3**. `package.json` declara las dependencias y
`package-lock.json` fija sus versiones. La intersección compatible de Vite y
Vitest es Node20.19+ dentro de 20, Node22.12+ dentro de 22 o Node24 y posteriores.

## Estructura y CSS

```text
frontend/
  index.html
  src/
    main.jsx
    App.jsx
    index.css
    components/
      Header/          Header.jsx y Header.css
      Footer/          Footer.jsx y Footer.css
      Hero/            Hero.jsx y Hero.css
      MovieCard/       MovieCard.jsx y MovieCard.css
      MovieList/       MovieList.jsx y MovieList.css
      Showtimes/       Showtimes.jsx y Showtimes.css
      Synopsis/        Synopsis.jsx y Synopsis.css
      AgentMessage/    AgentMessage.jsx y AgentMessage.css
    data/movies.js
    data/movieDetails.js
    styles/tokens.css
    styles/base.css
    styles/layout.css
    duel/team/         Reexportaciones de los componentes finales
    duel/ai/           Respuestas originales, sin cambios
    duel/fixed/        Copia corregida
    duel/tests/        Verificador original, sin cambios
  public/posters/      Ocho SVG locales
  public/art/          Banner SVG local
  lab-errors/          Casos deliberados aislados del producto
  scripts/
  package.json
  package-lock.json
```

`tokens.css` reúne los colores y la tipografía, `base.css` las reglas globales,
el foco de teclado y movimiento reducido; `layout.css` compone las secciones y
media queries. Cada componente importa su CSS con clases propias. El texto pegado
no detallaba otra arquitectura; se separó el CSS global del ejemplo docente para
cumplir la organización por responsabilidad y por componente de la guía.

## Componentes y props

| Componente | Props | Responsabilidad |
| --- | --- | --- |
| Header | name, links | h1 y navegación Principal |
| Footer | contact | Dirección, teléfono tel: y correo mailto: |
| Hero | movie | Destacada y enlace dinámico #horarios-id |
| MovieCard | movie | Imagen con alt, título, clasificación, valoración, sinopsis y horas |
| MovieList | movies | map y li con key={movie.id} |
| Showtimes | times | Lista de horas o Sin funciones hoy |
| Synopsis | text | Texto literal, sin interpretar HTML |
| AgentMessage | author, text | Autor y texto literal de un agente |

App importa y une los datos, elige la destacada y pasa las props. Los componentes
de presentación no importan el archivo de películas ni hacen peticiones. MovieList
pasa cada película a MovieCard; MovieCard reutiliza Synopsis. Las tarjetas muestran
las horas en una línea y Showtimes las presenta como una lista semántica en la
sección de funciones. Esto mantiene el verificador docente sin cambios y evita
anidar listas dentro del ul de películas. Las sinopsis se abren con `details` y
`summary`, sin estado de React.

`movies.js` es idéntico al original: sus pruebas exigen seis campos exactos. Las
clasificaciones y géneros ficticios están en `movieDetails.js`; App los agrega a
los objetos de presentación mediante `map` y propagación de propiedades. No se
duplican las películas dentro de los hijos. Una tiene `showtimes: []`, y otra trae
una sinopsis hostil deliberada.

Los ocho afiches y el banner son ilustraciones SVG originales generadas con
`frontend/scripts/create-art.mjs`. No requieren imágenes ni fuentes remotas.
Películas, valoraciones, clasificaciones y contacto son datos de demostración.

## Correspondencia con los doce pasos

| Paso de la guía | Implementación y evidencia |
| --- | --- |
| 1 | Generador Vite, instalación y servidor localhost5173; versiones y captura desktop |
| 2 | main.jsx e index.html mínimos; se retiraron las imágenes y controles de la plantilla |
| 3 | components, data y styles; un directorio y CSS por componente |
| 4 | Ocho películas; metadatos complementarios de clasificación y género |
| 5 | Header por props; navegación con destinos presentes |
| 6 | Footer con contact, tel: y mailto: |
| 7 | Hero con movie y enlace a los horarios de su id |
| 8 | MovieCard con imagen, título, valoración y horarios de props |
| 9 | MovieList usa map y key estable por id |
| 10 | App compone las ocho responsabilidades; ocho tarjetas verificadas en navegador |
| 11 | Tres fallos reales en lab-errors; mensajes en browser-results.json |
| 12 | Rama del curso, este documento, Word, capturas y observaciones |

## Pruebas y duelo con la IA

Desde `frontend/`:

```powershell
npm test
npm run duel
npm run duel:ai
npm run duel:fixed
npm run build
npm run lint
```

| Ejecución registrada | Resultado |
| --- | --- |
| Team inicial | 43 fallidas, ocho componentes pendientes |
| AI original | 29 correctas y 14 fallidas, en seis tareas |
| Fixed recién copiado con fixed:init | 29 correctas y 14 fallidas |
| Team final | 43 de 43 correctas |
| Fixed corregido | 43 de 43 correctas |
| Suite completa | 47 de 47 correctas |
| Suite tras restaurar el experimento inseguro | 47 de 47 correctas |
| Build y lint finales | Código de salida 0 |
| Navegador Edge mediante Playwright | 22 comprobaciones correctas |

Los registros están en `deliverables/lab09/evidence/01-team-red.txt` hasta
`11-final-lint.txt`, y `browser-results.json`. Las ejecuciones y capturas del
navegador se realizaron el 6 de noviembre; el documento se terminó el día 8.

**duel:ai falla de forma intencional:** no hay que usarlo como señal de que el
producto final está roto. El código original de IA se conserva como material del
ejercicio y está excluido de lint, igual que `lab-errors/`. El análisis sí incluye
los componentes finales, la copia fixed y el verificador. `duel:solutions` está
reservado al docente y no se utilizó.

No ejecutar `fixed:init -- --force` sobre la entrega terminada: reemplazaría la
copia corregida. El script se utilizó antes de editar fixed, como pide el README.

| Tarea | Fallo original | Corrección en fixed |
| --- | --- | --- |
| T2 Footer | class como propiedad DOM | className |
| T3 MovieCard | Imagen sin alternativa | alt={movie.title} |
| T4 Showtimes | Arreglo vacío verdadero y 0 visible | times.length === 0 |
| T5 MovieList | key por índice | key={movie.id} |
| T6 Synopsis | HTML de terceros interpretado | Interpolación {text} |
| T7 Hero | Espera film y recibe movie | Usar la prop movie |

T1 Header y T8 AgentMessage ya eran correctos en el material original. Las pruebas
no solo cuentan tarjetas: cambian props y verifican identidad DOM al invertir y
recortar la lista. Se conservaron intactas.

## Tres errores JSX y datos de terceros

Con el servidor de desarrollo activo:

- `http://localhost:5173/lab-errors/?case=class`: aviso **Invalid DOM property class. Did you mean className?** Se corrige usando className.
- `http://localhost:5173/lab-errors/?case=roots`: **Adjacent JSX elements must be wrapped in an enclosing tag.** Se corrige con Fragment o un padre.
- `http://localhost:5173/lab-errors/?case=key`: **Each child in a list should have a unique key prop.** Se corrige con key estable en el elemento devuelto por map.

Los ejemplos intencionales no se importan desde la entrada de producción. El JSON
guarda los mensajes de consola originales, con los marcadores `%s` que devuelve
Playwright; aquí se han sustituido para facilitar la lectura. El ejemplo roots
produce un 500 esperado del transformador de Vite; la cartelera final no registra
errores de consola.

Se cambió temporalmente Synopsis a `dangerouslySetInnerHTML` para el experimento
docente. El navegador observó `window.__xss === 1` y dos imágenes inyectadas donde
se reutiliza la sinopsis. La carga de prueba solo activa esa bandera local.
El script restauró el archivo en `finally`: en una página nueva la bandera quedó
sin definir y no hubo imágenes inyectadas. Las pruebas completas se repitieron
después. El mensaje del agente también permanece como texto literal en la versión
final. No se integró un servicio de IA ni se enviaron datos a un modelo externo.

`scripts/verify_lab09.cjs`, en la raíz, reproduce las comprobaciones del navegador
y el experimento temporal. Usa el Playwright del runtime de escritorio y Edge en
las rutas locales que declara el archivo; no es una dependencia para ejecutar la
cartelera. Las comprobaciones incluyen 320, 390, 768, 1024 y 1440px sin
desbordamiento horizontal. No constituyen una auditoría completa de accesibilidad.

## Procedencia y observaciones

Se partió del proyecto acumulativo de Lab08 y se creó frontend con el generador
oficial. Se incorporaron datos, ejercicios, modos y verificador de
`Hellscythe25/dae-s09-react-ia`, revisión
`861176ca6b84f80446928c3fc2484aba2c1dceb0`. `src/data/movies.js`, las pruebas y
`src/duel/ai/` se mantienen idénticos al material de referencia. La configuración
se adaptó al generador Vite actual y a las versiones bloqueadas de dependencias.

El único integrante es Diego Magallanes Linares. Se utilizó asistencia de Codex
para implementar, verificar y documentar. Las respuestas de IA comparadas ya
venían incluidas en el repositorio del docente; no se inventó una nueva sesión
con otro modelo ni trabajo individual sin asistencia. La rúbrica valora autonomía
y la calificación corresponde al docente.

La guía se recibió como texto. El Word se reconstruyó con sus secciones y el
diseño institucional de la entrega anterior. La entrega al campus la realiza el
estudiante. Publicar la rama no despliega la aplicación en internet.

## Conclusiones

1. Vite y el archivo de bloqueo permiten reproducir la instalación, el servidor y la compilación de la interfaz.
2. Componentes pequeños y props mantienen los datos en el padre y las responsabilidades de presentación en los hijos.
3. Las claves basadas en id preservan identidad al reordenar; el índice falló en las pruebas del caso.
4. Los errores JSX requieren distinguir avisos de React y fallos que impiden transformar el archivo.
5. Las pruebas detectaron seis clases de fallos en las respuestas de IA; corregirlas sin tocar el verificador dio una comparación comprobable.
6. La interpolación de texto conservó las sinopsis y mensajes sin ejecutar HTML de terceros. El experimento local y su restauración demostraron la diferencia.

Referencias: [Vite](https://vite.dev/guide/), [JSX](https://react.dev/learn/writing-markup-with-jsx),
[listas y claves](https://react.dev/learn/rendering-lists),
[props](https://react.dev/learn/passing-props-to-a-component).
