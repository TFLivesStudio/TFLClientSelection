# TFL Selection — Inventario de mods candidatos Fabric 26.3

> Estado: **registro de evaluación**, NO es una release, un manifiesto instalable ni una aprobación legal. Revisado: **2026-10-31**.
>
> Fuente: lista de **56 JARs/versiones aportada por TFLives**. El archivo [CSV auditable](inventory/mc-26.3-fabric-candidates.csv) conserva el nombre exacto del archivo, la versión, la URL del proyecto y el estado de licencias.

## Reglas inmutables

- **No modificar** el pack final seleccionado para 1.8.9 / Ornithe Gen2.
- La selección es **de TFLives**, no de cada usuario. TFL Core es **un único mod aparte**; no catalogar sus HUD ni submódulos aquí.
- No publicar ni añadir binarios a Git, Release o al `drafts/mc-26.3-fabric.json` hasta disponer de bytes verificados (SHA-256), fuente correspondiente, términos de redistribución y prueba de arranque conjunta.
- Los estados de abajo son **hipótesis de incorporación**, no resultados de benchmark ni certificaciones.
- Las licencias en CSV son **etiquetas preliminares de proyecto**, nunca certificación del JAR/version exactos.
- Modrinth/CurseForge solo son referencias de investigación. El launcher oficial descarga mods aprobados **desde las Releases administradas por TFLives**.

## Significado de estados

| Estado | Significado |
| --- | --- |
| BASE PROPUESTA | Candidato central por su función; requiere pruebas y licencia |
| EN EVALUACION | Interesante pero no aprobado aún |
| EXPERIMENTAL | Riesgo elevado de conflictos/alpha o dependencias gráficas |
| SOLO MUNDO LOCAL | Beneficio principal en singleplayer/servidor integrado, no remoto |
| DEPENDENCIA CONDICIONAL | Solo si otros mods finales lo requieren |
| UTILIDAD | Componente de gestión/configuración, revisar su integración |
| ALTERNATIVA NO ACTIVA | No simultanear con motor principal sin pruebas |
| BLOQUEO LEGAL | No redistribuir desde GitHub Releases sin permiso válido |
| REVISION LEGAL | Requiere resolver condiciones de la licencia/autor |
| VERIFICAR VERSION | Hay incertidumbre en los metadatos de esa versión |

## Los 56 componentes aportados

### Renderizado (3)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [ImmediatelyFast](https://modrinth.com/mod/5ZwdcRci) | `1.17.1+26.3` | BASE PROPUESTA | Optimiza rutas render inmediatas; verificar shaders |
| [More Culling](https://modrinth.com/mod/51shyZVL) | `1.9.0` | REVISION LEGAL | GPL declarada pero autor restringe integracion en clientes; revisar mirroring |
| [Sodium](https://modrinth.com/mod/AANobbMI) | `0.9.2+mc26.3` | BLOQUEO LEGAL | PolyForm Shield no es licencia OSS; revisar redistribucion y estrategia |

### Opciones graficas (1)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [Sodium Extra](https://modrinth.com/mod/PtjYWJkn) | `0.9.4+mc26.3` | BASE PROPUESTA | Opciones graficas adicionales |

### Memoria y correcciones (5)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [FerriteCore](https://modrinth.com/mod/uXXizFIs) | `9.0.0` | BASE PROPUESTA | Optimizacion memoria |
| [Jasione](https://modrinth.com/mod/qlDkBPij) | `1.0.9+26.1.2-fabric` | EN EVALUACION | 1.0.9+26.1.2-fabric declared compatible 26.3; test actual JAR |
| [Lithium](https://modrinth.com/mod/gvQqBUqZ) | `0.26.3+mc26.3` | BASE PROPUESTA | Optimizaciones logica Minecraft |
| [Lomka](https://modrinth.com/mod/bd9cFfiC) | `0.7.0` | EN EVALUACION | Reducir allocations y microstutter; verificar solapamiento |
| [ModernFix](https://modrinth.com/mod/TjSm1wrD) | `5.27.20-build.2` | EN EVALUACION | Es ModernFix-mVUS fork; probar solapamientos con Lithium y otros |

### Rendimiento cliente (8)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [BadOptimizations](https://modrinth.com/mod/g96Z4WVZ) | `2.4.1` | EN EVALUACION | Medir solapamiento con Sodium y otras optimizaciones |
| [Blindspot](https://modrinth.com/mod/OQonV5zt) | `0.4.0+26.3` | EN EVALUACION | Optimiza scoreboard TAB y sidebar; riesgo con TFL Core personalizado |
| [Dynamic FPS](https://modrinth.com/mod/LQ3K71Q1) | `3.11.10` | EN EVALUACION | Reduce uso recursos con juego en segundo plano |
| [Entity View Distance](https://modrinth.com/mod/ihnBJ6on) | `1.9.0+26.2` | EN EVALUACION | 1.9.0+26.2 declared compatible with 26.3; only shows entities server already sends |
| [EntityCulling](https://modrinth.com/mod/NNAgCjsB) | `1.11.3` | BLOQUEO LEGAL | Licencia prohibe redistribuir JAR fuera de Modrinth/CurseForge sin permiso |
| [Fast IP Ping](https://modrinth.com/mod/9mtu0sUO) | `1.0.12` | EN EVALUACION | Evita reverse DNS para IPs; confirmar version 26.3 |
| [Ixeris](https://modrinth.com/mod/p8RJPJIC) | `4.6.10+26.3-fabric` | EN EVALUACION | Optimizacion polling entrada; verificar compatibilidad LWJGL |
| [Language Reload](https://modrinth.com/mod/uLbm7CG6) | `1.7.8+26.3` | EN EVALUACION | Optimiza cambio/reload idioma |

### Renderizado y particulas (2)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [AsyncParticles](https://modrinth.com/mod/c3onkd5k) | `26.3.2.1` | EXPERIMENTAL | Validar conflictos con Particle Core y shaders |
| [Particle Core](https://modrinth.com/mod/RSeLon5O) | `0.3.3+fix1+26.2` | EXPERIMENTAL | Version declara 26.3 aunque etiqueta 26.2; prueba con AsyncParticles |

### Logica y mundos (10)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [Alternate Current](https://modrinth.com/mod/r0v8vy1s) | `1.9.0` | SOLO MUNDO LOCAL | Optimizacion de redstone del servidor integrado; no acelera servidores remotos |
| [Clumps](https://modrinth.com/mod/Wnxd13zP) | `26.3.2` | SOLO MUNDO LOCAL | Agrupa orbes experiencia; impacto principalmente en servidor integrado |
| [Concurrent Chunk Management Engine](https://modrinth.com/mod/VSNURh3q) | `0.4.2-alpha.0.114+26.3` | EXPERIMENTAL | Alpha; alto riesgo concurrencia y generacion mundo; probar singleplayer |
| [Fast Noise](https://modrinth.com/mod/OnlVIpq5) | `1.1.2+26.3` | SOLO MUNDO LOCAL | Acelera ruido worldgen solo donde se ejecuta generacion |
| [FastQuit](https://modrinth.com/mod/x1hIzbuY) | `3.1.5+mc26.2` | EN EVALUACION | 3.1.5+mc26.2 declared compatible with 26.3 by publisher; test actual JAR |
| [Ksyxis](https://modrinth.com/mod/2ecVyZ49) | `1.4.6` | SOLO MUNDO LOCAL | Optimizacion apertura mundo; utilidad local |
| [RailOptimization](https://modrinth.com/mod/QSvN5pBU) | `2.5-snapshot.1` | SOLO MUNDO LOCAL | Optimizacion rail logic servidor integrado; snapshot y etiqueta antigua |
| [ScalableLux](https://modrinth.com/mod/Ps1zyz6x) | `0.3.0-alpha.0.6+26.3` | EXPERIMENTAL | Motor iluminacion mundo alpha; beneficio servidor integrado |
| [ServerCore](https://modrinth.com/mod/4WWQxlQP) | `1.5.20+26.3` | SOLO MUNDO LOCAL | Principalmente lado servidor; no ofrece mejora de servidores remotos |
| [Structure Layout Optimizer](https://modrinth.com/mod/ayPU0OHc) | `1.1.4+26.3-fabric` | SOLO MUNDO LOCAL | Optimizacion generacion estructuras local; no afecta servidores remotos |

### Red (1)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [Krypton](https://modrinth.com/mod/fQEb0iXm) | `0.3.2` | EN EVALUACION | Optimizacion red; comprobar version MC y conflictos |

### Shaders (2)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [Iris](https://modrinth.com/mod/YL57xq9U) | `1.11.7+mc26.3` | BASE PROPUESTA | Motor OpenGL shaders; verificar Sodium y LOD |
| [Vitrail](https://modrinth.com/mod/oSIKhgz3) | `0.13.0-beta` | ALTERNATIVA NO ACTIVA | Shader engine Vulkan experimental; no mezclar con Iris hasta probar |

### Resource packs (11)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [Animatica Refabricated](https://modrinth.com/mod/xEyZuswh) | `0.7.0+beta.4+26.3-fabric` | EN EVALUACION | Texturas animadas; comprobar compatibilidad con otros sistemas de packs |
| [BetterGrassify](https://modrinth.com/mod/m5T5xmUy) | `1.8.8+fabric.26.3` | EN EVALUACION | Better grass; revisar solapamiento con Continuity y pack |
| [CIT Resewn: Continued](https://www.curseforge.com/projects/1683111) | `0.1.3` | EN EVALUACION | Comprobar procedencia licencia de fork y CIT con otros mods |
| [Continuity](https://modrinth.com/mod/1IjD5062) | `3.0.1+26.3` | EN EVALUACION | Connected textures; verificar necesidad de Indium/FRAPI segun Sodium |
| [Entity Model Features](https://modrinth.com/mod/4I1XuqiY) | `3.3.12` | EN EVALUACION | Modelos custom entidades; necesita revisar ETF |
| [Entity Texture Features](https://modrinth.com/mod/BVzZfTc1) | `7.2.6` | EN EVALUACION | Texturas de entidades y emissives |
| [OptiGUI](https://modrinth.com/mod/JuksLGBQ) | `2.3.0-beta.10+26.3` | EN EVALUACION | Custom GUI de resource packs; beta |
| [Polytone](https://modrinth.com/mod/3qAYkBMB) | `26.3-6.8.6` | EN EVALUACION | Colormaps y personalizacion recursos |
| [Resource Pack Options](https://modrinth.com/mod/TiF5QWZY) | `26.3.0` | EN EVALUACION | Configuracion personalizada packs |
| [Skyboxify](https://modrinth.com/mod/DWuwk8aA) | `3.4` | EN EVALUACION | Skyboxes tipo Optifine; conflictos posibles con shaders y Polytone |
| [quick-pack](https://modrinth.com/mod/pSISfJ4O) | `1.5.1` | EN EVALUACION | Mejora carga ZIP de resourcepacks y datapacks |

### Visuales (2)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [Better Biome Blend](https://modrinth.com/mod/Rs6c7WyL) | `1.4.1` | EN EVALUACION | Blend de biomas; verificar con shaders y Sodium |
| [LambDynamicLights](https://modrinth.com/mod/yBW8D80W) | `4.13.0+26.3` | EN EVALUACION | Iluminacion dinamica client-side |

### Audio (1)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [Raise Sound Limit Simplified](https://modrinth.com/mod/SKW62Pht) | `1.4.0` | EN EVALUACION | Aumenta fuentes audio; medir uso CPU y conflictos |

### Biblioteca (10)

| Mod | Versión registrada | Estado | Nota |
| --- | --- | --- | --- |
| [Cloth Config v26.3](https://modrinth.com/mod/9s6osm5g) | `26.3.159` | DEPENDENCIA CONDICIONAL | Solo si la requieren mods aprobados |
| [Fabric API](https://modrinth.com/mod/P7dR8mSH) | `0.165.0+26.3` | DEPENDENCIA CONDICIONAL | Base requerida por varios mods |
| [Fabric Language Kotlin](https://modrinth.com/mod/Ha28R6CL) | `1.14.2+kotlin.2.4.21` | DEPENDENCIA CONDICIONAL | Instalar solo al confirmar requisitos |
| [Fzzy Config](https://modrinth.com/mod/hYykXjDp) | `0.7.7+fix3+26.3` | DEPENDENCIA CONDICIONAL | Solo si se necesita |
| [LibJF](https://modrinth.com/mod/WKwQAwke) | `26.3.1` | DEPENDENCIA CONDICIONAL | Solo si la requiere un mod aprobado |
| [Mod Menu](https://modrinth.com/mod/mOgUt4GM) | `21.0.0` | UTILIDAD | Lista/config mods; respetar perfil Selection bloqueado |
| [Placeholder API](https://modrinth.com/mod/eXts2L7r) | `3.2.0+26.3` | DEPENDENCIA CONDICIONAL | Solo si la requieren mods aprobados |
| [Resourcefulconfig](https://modrinth.com/mod/M1953qlQ) | `6.0.2` | DEPENDENCIA CONDICIONAL | Solo si lo requiere mod aprobado |
| [YetAnotherConfigLib](https://modrinth.com/mod/1eAoo2KR) | `3.9.7+26.3-fabric` | DEPENDENCIA CONDICIONAL | Solo si lo necesita mod aprobado |
| [ZConfig](https://modrinth.com/mod/4qmvXRB9) | `1.0.0+26.x` | DEPENDENCIA CONDICIONAL | Solo si lo necesita mod aprobado |

## Diez funciones pactadas del modpack

| Función | Selección o trabajo registrado |
| --- | --- |
| Optimización del renderizado | Sodium, ImmediatelyFast, revisión de culling/partículas |
| Opciones gráficas avanzadas | Sodium Extra, controles gráficos compatibles |
| Optimización de memoria y correcciones | FerriteCore, Lithium, ModernFix-mVUS y candidatos pequeños |
| Profiling y diagnóstico | **Spark** estaba preseleccionado anteriormente; no figura entre los 56 JAR aportados; falta versión/archivo |
| Frame Generation | **PureScale** era candidato previo; no figura entre los 56 JAR; no aprobado aún |
| Shaders | **Iris** principal (OpenGL). Vitrail/Vulkan como experimento separado |
| Extensiones resource packs | Continuity, Animatica, CIT Resewn: Continued, ETF, EMF, OptiGUI, Polytone, Skyboxify, BetterGrassify, Resource Pack Options |
| Renderizado LOD | **Distant Horizons** ya decidido como mod independiente. No figura entre los 56 JAR nuevos y requiere revisión de build/versión para empaquetar |
| Audio/Sonido | Raise Sound Limit Simplified en esta lista; **Sound Physics Remastered** era candidato previo y requiere aprobación separada |
| Mod Core | **TFL Core** (artefacto creado y versionado en TFLClientMOD, nunca incrustar fuentes en este pack) |

## Bloqueos y decisiones que NO se deben omitir

1. **Sodium — PolyForm Shield.** No es OSI/open source. Antes de duplicarlo o publicarlo en nuestras Releases, resolver el alcance de redistribución y restricciones de productos competidores; no aprobar automáticamente por disponibilidad del código. [Licencia/proyecto](https://modrinth.com/mod/AANobbMI).
2. **EntityCulling — tr7zw Protective License.** El autor permite modpacks alojados en Modrinth/CurseForge, pero **prohíbe redistribuir sus JARs en otros destinos** sin permiso. Esto bloquea el modelo de distribución propio de TFL mientras no haya autorización. [Fuente](https://github.com/tr7zw/EntityCulling).
3. **More Culling — GPL-3.0 declarada con aviso del autor sobre fusionarlo en clientes/otros mods.** Mantener independiente si se evalúa y aclarar condiciones de mirroring/atribución, evitando integrar código en TFL Core. [Descripción](https://modrinth.com/mod/moreculling).
4. **ModernFix 5.27.20-build.2** corresponde al fork **ModernFix-mVUS**. Verificar procedencia del upstream, licencia efectiva y conflictos de Mixins con Lithium, Lomka, Jasione, BadOptimizations y otros. [Ficha](https://modrinth.com/mod/modernfix-mvus).
5. **Vitrail** usa el renderer experimental **Vulkan** de Minecraft; **Iris** usa OpenGL. Tratarlo como sustitución experimental, no como segundo motor de shaders simultáneo. [Fuente](https://modrinth.com/mod/oSIKhgz3).
6. **AsyncParticles + Particle Core**, **More Culling + otros culling**, **BetterGrassify + Continuity**, **Skyboxify + Polytone + Iris**, y **C2ME + ScalableLux + ModernFix**: crear pruebas A/B para detectar trabajo duplicado, Mixins incompatibles y regresiones visuales.
7. **Servicios de servidor vs cliente:** Alternate Current, Clumps, Fast Noise, C2ME, Ksyxis, ScalableLux, ServerCore, Structure Layout Optimizer y RailOptimization deben justificarse en singleplayer. Instalar algo en el cliente no puede optimizar el TPS de un servidor remoto.
8. Los sufijos `+26.2` **no prueban incompatibilidad con 26.3**: FastQuit 3.1.5, Entity View Distance 1.9.0, Jasione 1.0.9 y Particle Core 0.3.3 declaran 26.3 en sus páginas; se deben probar sus metadatos/JAR exactos.

## Puertas de salida antes de convertir un candidato en mod oficial

1. Descargar o compilar cada **archivo exacto**; registrar hash SHA-256, tamaño, fuente/tag/commit y metadatos Fabric/MC/Java.
2. Inspeccionar licencia real del **artefacto concreto** y dependencias empacadas; guardar LICENSE, NOTICE y archivos de fuentes correspondientes para copyleft.
3. Determinar si el mod es cliente, servidor integrado o biblioteca; comprobar dependencias sin inventar versiones.
4. Probar arranque, cambio de mundo, servidores vanilla, Iris shaders, Distant Horizons, TFL Core y sesiones largas sin filtraciones.
5. Benchmark con mismos escenarios: FPS promedio, 1% low, frametimes p95/p99, RAM, VRAM, carga y tiempo de arranque. Comparar activando los mods por grupos.
6. Solo después convertir aprobados al **manifiesto firmado** y publicar bytes en GitHub Releases de TFL Selection, según AGENTS.md.

## Seguimiento de fuentes

- [Licencias y política de distribución](SECURITY_AND_LICENSING.md)
- [Matriz del proyecto](SELECTION_MATRIX.md)
- [Contrato de launcher y releases](LAUNCHER_CONTRACT.md)
- [Inventario literal 26.3](inventory/mc-26.3-fabric-candidates.csv)
