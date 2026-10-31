# TFL Selection

Repositorio **privado** para definir los perfiles y lanzamientos del modpack multimodo TFL Selection, consumidos exclusivamente mediante el contrato del **TFL Client Launcher**.

> **Estado:** fundación de arquitectura; no hay releases ni binarios descargables publicados. Este repositorio no es un servidor de descargas.

## Responsabilidades

- Definir qué mods, configuraciones y recursos corresponden a cada versión de Minecraft.
- Mantener manifiestos versionados, hashes SHA-256, políticas de instalación y procedencia/licencias.
- Validar y aprobar los cambios antes de publicar un canal (`stable`, `beta` o `dev`).
- Coordinar el TFL Core (compilado en su propio repositorio) sin incorporar su código fuente aquí.

La distribución de archivos privados se realizará desde almacenamiento de objetos y una API controlada. **Nunca** debe incluirse un token GitHub, clave de almacenamiento ni secreto de firma en el launcher.

## Arquitectura objetivo

```text
TFL Client (launcher abierto)
   -> API de distribución TFL (catálogo y manifiestos firmados)
   -> tickets de descarga de duración limitada
   -> almacenamiento de objetos privados / fuentes oficiales autorizadas
   -> verificación SHA-256 y actualización transaccional local

TFL Selection (este repositorio privado)
   -> esquemas, manifiestos, revisión y automatización del lanzamiento
TFL Core (repositorio independiente)
   -> binarios propios versionados consumidos por Selection
```

La privatización evita publicar el repositorio y su configuración de lanzamiento, pero **no impide** que un usuario autorizado extraiga los archivos que se instalan en su computadora. Las licencias de terceros deben respetarse por separado.

## Versiones objetivo (iniciales)

- Minecraft **1.8.9**, loader **Ornithe Gen2**.
- Minecraft **26.3**, loader **Fabric**.
- El diseño admitirá versiones adicionales sin cambiar el protocolo.

## Desarrollo

La propuesta inicial se trabajará en una rama y se integrará tras revisión. Consultar `docs/` para arquitectura, seguridad, protocolo y proceso de release.
