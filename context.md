# Definición funcional del sistema

## 1. Objetivo principal

El objetivo principal de la **Plataforma Inteligente de Atención de Emergencias Vehiculares** es resolver el problema de la atención lenta, desorganizada y poco confiable ante emergencias vehiculares, conectando de manera inteligente a conductores con talleres y técnicos adecuados según el tipo de avería, la ubicación del incidente, la disponibilidad del taller y la prioridad del caso.

Actualmente, cuando un conductor sufre una falla mecánica, un pinchazo, un problema de batería, un sobrecalentamiento, un accidente leve o situaciones similares, normalmente debe buscar ayuda de forma manual, hacer llamadas, explicar el problema sin estructura y esperar sin saber si realmente recibirá atención adecuada. Esto genera pérdida de tiempo, incertidumbre, mala coordinación y falta de trazabilidad.

La plataforma busca solucionar esto mediante un flujo centralizado en el que el conductor registra la avería, adjunta evidencias, la inteligencia artificial analiza la información, el sistema clasifica y prioriza el incidente, se asigna o selecciona el taller más adecuado, se coordina la atención con técnicos dependientes del taller, se realiza el seguimiento del servicio y finalmente se ejecuta el pago y cierre del caso.

### Problemas que resuelve
- Dificultad para encontrar ayuda confiable en una emergencia vehicular.
- Falta de información estructurada sobre la avería.
- Tiempos de respuesta impredecibles.
- Dificultad para identificar el proveedor correcto.
- Ausencia de trazabilidad del servicio.
- Falta de una plataforma organizada para que los talleres gestionen solicitudes y recursos.

### Resultado esperado
- Atención más rápida y organizada.
- Clasificación preliminar del problema con IA.
- Priorización del incidente.
- Mejor asignación de talleres y técnicos.
- Seguimiento en tiempo real.
- Registro histórico del proceso completo.
- Pago y cierre dentro de la plataforma.

---

## 2. Tipo de usuario

El sistema contempla cuatro tipos principales de usuario: **conductor**, **taller**, **mecánico** y **administrador**.

### 2.1 Conductor
Es el usuario que reporta la emergencia y solicita ayuda para su vehículo.

#### Funciones principales
- Registrarse e iniciar sesión.
- Registrar y administrar sus vehículos.
- Reportar una avería o emergencia.
- Adjuntar texto, audio, imágenes y ubicación.
- Consultar el estado de la solicitud.
- Ver el taller asignado o seleccionado.
- Ver el tiempo estimado de llegada.
- Recibir notificaciones push.
- Comunicarse con el taller o mecánico si aplica.
- Revisar presupuestos.
- Realizar pagos.
- Calificar el servicio recibido.

---

### 2.2 Taller
Es la entidad proveedora del servicio de asistencia. Administra solicitudes, disponibilidad, técnicos y operación del servicio.

#### Funciones principales
- Registrarse en la plataforma.
- Gestionar información del taller.
- Configurar servicios ofrecidos, horarios y cobertura.
- Ver solicitudes disponibles.
- Revisar información estructurada del incidente.
- Aceptar o rechazar órdenes.
- Asignar técnicos.
- Actualizar estados del servicio.
- Generar presupuestos.
- Consultar historial de atenciones.
- Ver clasificación, resumen y prioridad generados por IA.
- Pagar la comisión correspondiente a la plataforma.

---

### 2.3 Mecánico
Es el técnico dependiente de un taller. No opera de forma independiente.

#### Funciones principales
- Recibir asignaciones de servicio.
- Consultar la ubicación del cliente.
- Ver información resumida del incidente.
- Marcar estados operativos como:
  - asignado,
  - en camino,
  - atendiendo,
  - finalizado.
- Registrar observaciones técnicas.
- Contribuir al cierre del servicio.

---

### 2.4 Administrador
Es el usuario encargado del control y supervisión general de la plataforma.

#### Funciones principales
- Gestionar usuarios y roles.
- Supervisar talleres y mecánicos.
- Administrar catálogos del sistema.
- Consultar historial y métricas.
- Monitorear incidentes y desempeño del sistema.
- Dar soporte administrativo y operativo.

---

## 3. Flujo deseado

El flujo principal del sistema se estructura desde el registro del incidente hasta el cierre del servicio.

### 3.1 Flujo principal
1. El conductor inicia sesión en la aplicación móvil.
2. Selecciona uno de sus vehículos registrados o registra uno nuevo.
3. Reporta una avería o emergencia vehicular.
4. Adjunta la información necesaria:
   - descripción textual,
   - audio,
   - fotografías,
   - ubicación actual.
5. El sistema registra la avería.
6. La inteligencia artificial procesa los datos:
   - transcribe el audio,
   - analiza las imágenes,
   - interpreta el texto,
   - clasifica el problema,
   - asigna una prioridad,
   - genera un resumen estructurado.
7. El sistema identifica talleres compatibles considerando:
   - ubicación,
   - tipo de problema,
   - disponibilidad del taller,
   - capacidad operativa,
   - distancia,
   - prioridad del caso.
8. Se genera una orden de servicio.
9. El taller recibe la solicitud.
10. El taller revisa la información del incidente.
11. El taller acepta o rechaza la orden.
12. Si acepta, asigna un técnico.
13. El conductor recibe notificación de la aceptación.
14. El sistema calcula o muestra el tiempo estimado de llegada.
15. El mecánico actualiza su estado:
   - asignado,
   - en camino,
   - atendiendo,
   - finalizado.
16. Si corresponde, el taller genera un presupuesto.
17. El conductor revisa y aprueba o rechaza el presupuesto.
18. Se realiza el pago desde la aplicación.
19. El sistema registra la comisión de la plataforma.
20. Se cierra la orden.
21. Se registra historial, métricas y calificaciones.

---

### 3.2 Flujo alterno: rechazo de orden
1. El taller recibe la solicitud.
2. Determina que no puede atenderla por disponibilidad, cobertura o capacidad.
3. Rechaza la orden.
4. Se actualiza el estado.
5. El conductor es notificado.
6. El sistema busca otra opción o permite generar una nueva orden.

---

### 3.3 Flujo alterno: caso incierto
1. El conductor reporta una avería con información insuficiente.
2. La IA clasifica el caso como incierto.
3. El sistema solicita más información.
4. El conductor adjunta nuevas evidencias.
5. Se vuelve a procesar el incidente o se deriva a revisión manual.

---

## 4. Pantallas o endpoints involucrados

### 4.1 Pantallas del conductor (aplicación móvil)
- Registro de usuario.
- Inicio de sesión.
- Gestión de perfil.
- Gestión de vehículos.
- Registro de avería.
- Carga de evidencias.
- Estado de la solicitud.
- Detalle de la orden de servicio.
- Chat con el taller o técnico.
- Revisión de presupuesto.
- Pago.
- Historial de incidentes.
- Calificación del servicio.

---

### 4.2 Pantallas del taller (aplicación web)
- Inicio de sesión.
- Dashboard principal.
- Gestión del perfil del taller.
- Gestión de horarios, cobertura y disponibilidad.
- Gestión de servicios ofrecidos.
- Lista de solicitudes disponibles.
- Detalle de la orden.
- Asignación de técnicos.
- Seguimiento del servicio.
- Emisión de presupuesto.
- Historial de atenciones.
- Gestión de pagos y comisiones.

---

### 4.3 Pantallas del mecánico
- Inicio de sesión.
- Lista de asignaciones.
- Detalle del incidente.
- Vista de ubicación del cliente.
- Actualización de estado.
- Registro de observaciones.
- Cierre de servicio.

---

### 4.4 Pantallas del administrador
- Dashboard administrativo.
- Gestión de usuarios.
- Gestión de talleres.
- Gestión de mecánicos.
- Supervisión de órdenes.
- Historial y métricas.
- Gestión de categorías de servicio.
- Configuración general del sistema.

---

### 4.5 Endpoints principales del backend
#### Autenticación
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`

#### Perfil y usuarios
- `GET /users/me`
- `PUT /users/me`

#### Vehículos
- `POST /vehiculos`
- `GET /vehiculos`
- `PUT /vehiculos/{id}`
- `DELETE /vehiculos/{id}`

#### Averías
- `POST /averias`
- `GET /averias/{id}`
- `GET /averias`
- `POST /averias/{id}/medios`

#### Diagnóstico IA
- `POST /averias/{id}/diagnostico`
- `GET /averias/{id}/diagnostico`

#### Órdenes de servicio
- `POST /ordenes`
- `GET /ordenes/{id}`
- `PUT /ordenes/{id}/aceptar`
- `PUT /ordenes/{id}/rechazar`
- `PUT /ordenes/{id}/estado`

#### Asignaciones
- `POST /ordenes/{id}/asignar-mecanico`
- `PUT /asignaciones/{id}/estado`

#### Presupuestos
- `POST /ordenes/{id}/presupuestos`
- `PUT /presupuestos/{id}/aprobar`
- `PUT /presupuestos/{id}/rechazar`

#### Pagos
- `POST /pagos`
- `GET /pagos/{id}`

#### Chat
- `POST /chats`
- `GET /chats/{id}/mensajes`
- `POST /chats/{id}/mensajes`

#### Notificaciones
- `GET /notificaciones`
- `POST /dispositivos/push-token`

#### Calificaciones
- `POST /calificaciones`

---

## 5. Datos clave que se guardan o editarán

### 5.1 Usuario
- nombre
- apellido
- correo electrónico
- teléfono
- contraseña
- rol
- foto de perfil
- estado activo

### 5.2 Vehículo
- conductor propietario
- marca
- modelo
- año
- placa
- color
- tipo de combustible
- foto

### 5.3 Taller
- usuario asociado
- nombre del taller
- descripción
- dirección
- latitud y longitud
- radio de cobertura
- teléfono
- disponibilidad
- calificación promedio
- acepta atención a domicilio

### 5.4 Mecánico
- usuario asociado
- taller al que pertenece
- especialidad
- disponibilidad
- ubicación actual
- fecha de última ubicación
- estado activo

### 5.5 Avería
- conductor que reporta
- vehículo afectado
- descripción del conductor
- ubicación del incidente
- dirección referencial
- prioridad
- estado
- indicador de si requiere más información
- fechas de creación y actualización

### 5.6 Evidencias
- avería asociada
- tipo de evidencia
- URL del archivo
- orden de visualización
- fecha de subida

### 5.7 Diagnóstico IA
- avería asociada
- categoría del problema
- clasificación
- urgencia
- nivel de confianza
- transcripción del audio
- análisis generado
- resumen automático
- daños visibles
- recomendación
- costo estimado
- indicador de revisión manual
- historial de conversación

### 5.8 Orden de servicio
- avería asociada
- taller responsable
- categoría de servicio
- estado
- notas del conductor
- notas del taller
- motivo de rechazo
- motivo de cancelación
- tiempo estimado de respuesta
- tiempo estimado de llegada
- fechas del proceso

### 5.9 Asignación de orden
- orden asociada
- mecánico asignado
- usuario que asignó
- estado de la asignación
- fecha de asignación
- salida
- llegada
- finalización

### 5.10 Presupuesto
- orden asociada
- versión
- descripción de trabajos
- detalle de ítems
- monto de repuestos
- monto de mano de obra
- monto total
- estado
- fecha de envío
- fecha de respuesta

### 5.11 Pago
- orden asociada
- presupuesto relacionado
- monto
- método de pago
- estado
- referencia externa
- fecha de pago

### 5.12 Comisión de plataforma
- orden asociada
- pago asociado
- monto base
- porcentaje
- monto comisión
- estado
- fecha de creación
- fecha de pago

### 5.13 Chat y mensajes
- orden asociada
- remitente
- contenido
- tipo de mensaje
- archivo multimedia
- estado de lectura
- fecha de envío

### 5.14 Calificación
- orden asociada
- usuario que califica
- usuario calificado
- puntuación
- comentario
- fecha de creación

### 5.15 Notificación
- usuario destinatario
- orden asociada
- título
- mensaje
- tipo
- estado de lectura
- fecha de creación

### 5.16 Historial y métricas
- cambios de estado
- usuario responsable del cambio
- observación
- tiempo de respuesta
- tiempo de llegada
- tiempo de resolución
- calificación final

---

## 6. Reglas de negocio

### 6.1 Reglas de acceso
- Solo un conductor puede registrar una avería.
- Solo un conductor puede registrar vehículos propios.
- Solo un taller puede aceptar o rechazar órdenes dirigidas a su taller.
- Solo un taller puede asignar un técnico perteneciente a su propio taller.
- Un mecánico pertenece a un único taller.
- Un administrador supervisa el sistema, pero no ejecuta la atención operativa.

---

### 6.2 Reglas sobre averías
- Toda avería debe pertenecer a un conductor y a un vehículo.
- Toda avería debe registrar ubicación.
- Debe existir al menos una descripción básica del problema.
- La avería puede contener múltiples evidencias.
- La avería pasa por estados controlados, no arbitrarios.
- Si la IA detecta incertidumbre, el sistema debe solicitar más información o habilitar revisión manual.

---

### 6.3 Reglas sobre IA
- Cada avería tiene un diagnóstico IA principal.
- La IA debe clasificar el problema en una categoría válida o como incierto.
- La IA debe generar una prioridad.
- La IA debe integrarse al flujo del sistema y no funcionar como un módulo aislado.
- Si el nivel de confianza es bajo, debe marcarse para revisión manual.

---

### 6.4 Reglas sobre órdenes
- Toda orden debe estar asociada a una avería y a un taller.
- Una orden no puede completarse sin haber sido aceptada.
- Una orden rechazada debe registrar motivo.
- Una orden cancelada debe registrar motivo.
- Una orden aceptada puede generar asignación de técnico.
- Una orden debe mantener historial de estados y trazabilidad completa.

---

### 6.5 Reglas sobre asignación de técnicos
- El técnico asignado debe pertenecer al mismo taller de la orden.
- El técnico debe estar disponible.
- La ubicación del técnico debe permitir estimar el tiempo de llegada.
- Un taller puede reasignar la atención si existe una causa válida.

---

### 6.6 Reglas sobre presupuesto y pagos
- Una orden puede tener uno o más presupuestos versionados.
- Solo el conductor puede aprobar o rechazar un presupuesto.
- El pago debe estar asociado a una orden válida.
- La comisión de la plataforma corresponde al 10% del cobro realizado al cliente.
- La factura debe generarse a partir de un pago válido.

---

### 6.7 Reglas sobre calificaciones
- Cada usuario califica una sola vez por orden.
- La puntuación debe estar entre 1 y 5.
- Solo pueden calificarse órdenes finalizadas o completadas.

---

## 7. Prioridad para el MVP

El MVP debe enfocarse en las funciones mínimas que demuestren el valor principal del sistema.

### 7.1 Prioridad alta
#### 1. Autenticación y manejo de roles
Permite diferenciar conductor, taller, mecánico y administrador.

#### 2. Gestión de vehículos
Necesaria para asociar la avería a un vehículo real.

#### 3. Registro de avería
Debe permitir registrar ubicación, descripción, audio e imagen.

#### 4. Diagnóstico IA básico
Debe cubrir al menos:
- transcripción de audio,
- clasificación del problema,
- prioridad,
- resumen preliminar.

#### 5. Registro y configuración de talleres
Debe permitir definir ubicación, cobertura, disponibilidad y servicios.

#### 6. Gestión de órdenes
Incluye crear, aceptar, rechazar y actualizar estados.

#### 7. Asignación de mecánico
Es esencial porque los técnicos forman parte explícita del problema de negocio.

#### 8. Notificaciones
Se requieren para informar cambios importantes al conductor y al taller.

---

### 7.2 Prioridad media
#### 9. Presupuestos
Importantes para formalizar el costo del servicio.

#### 10. Pagos
Idealmente deben entrar al MVP, aunque puede iniciarse con una simulación.

#### 11. Chat
Útil para interacción, pero puede entrar después del flujo principal.

#### 12. Historial y métricas
Muy importantes para trazabilidad y defensa del proyecto.

---

### 7.3 Prioridad baja
#### 13. Facturación completa
Puede implementarse después del flujo principal.

#### 14. Optimización avanzada del motor de asignación
Para el MVP basta una lógica funcional basada en proximidad, disponibilidad y categoría.

#### 15. Reportes administrativos avanzados
Son valiosos, pero no forman parte del núcleo inicial del sistema.

---

## Resumen ejecutivo

### Objetivo
Conectar de forma inteligente a conductores con talleres y técnicos para resolver emergencias vehiculares con mayor rapidez, precisión y trazabilidad.

### Usuarios
- Conductor
- Taller
- Mecánico
- Administrador

### Flujo principal
Registrar avería → procesar con IA → clasificar y priorizar → generar orden → aceptar/rechazar → asignar técnico → atender → presupuestar → pagar → cerrar → calificar.

### Elementos clave del sistema
- Aplicación móvil para conductores
- Aplicación web para talleres
- Técnicos dependientes del taller
- IA integrada al flujo
- Notificaciones push
- Historial y métricas
- Pago y comisión

### MVP
Primero deben construirse:
- autenticación,
- roles,
- vehículos,
- averías,
- IA básica,
- talleres,
- órdenes,
- asignación de mecánico,
- notificaciones.