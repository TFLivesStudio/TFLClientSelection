# Cierre de TFL Selection 1.8.9 — solo 11 mods originales

El paquete del propietario se conserva **sin modificar versiones, nombres de instalación, tamaños ni SHA-256**. No se recompilan ni cambian estos JARs durante la publicación.

## Qué está automatizado en este repositorio

- Cinco assets exactos de GitHub Releases **públicas y originales**: Argentum, Argentum Extras, Cera, Sarcio y OSL.
- Seis assets **propios de TFL Selection**: Amplio 0.1.1, Legacy LWJGL3 1.4.10, Lucerna 0.1.5-tfl.2, Pulse 1.0.0, SoundFix 1.1.0+mc1.8.9 y TFL Core 0.5.0-visual-preview.1.
- TFL Core no puede instalarse desde su Release actual porque `TFLClientMOD` es **privado**. El mismo JAR y su archivo de fuentes GPLv3 se publican desde TFLClientSelection.
- Las fuentes candidatas de los cinco mods públicos están **fijadas a commits de 40 caracteres**, con licencias y avisos. Lucerna y Amplio utilizan los dos forks del propietario.
- El workflow `.github/workflows/publish-selection-189.yml` crea una Release como borrador, verifica los archivos y, tras aprobación explícita del responsable y la firma Ed25519, publica los assets nuevos, verifica su descarga, sube sus licencias/fuentes y activa el catálogo firmado **beta**.

## Instrucciones exactas al propietario (Windows)

### 1. Abrir el borrador que ya creé

**El workflow de GitHub ya creó el borrador automáticamente y su ejecución finalizó con éxito.** Abre [la Release en borrador TFL Selection 1.8.9](https://github.com/TFLivesStudio/TFLClientSelection/releases/tag/untagged-4a4f69c3a1b08af7c4b4) y pulsa **Edit**. No necesitas ejecutar `create-draft` otra vez. Si el enlace no abre, entra en el repositorio → **Releases** → **Drafts** y busca la tag `selection-mc-1.8.9-ornithe-v0.1.0-preview.1`.

### 2. Adjuntar siete archivos exactos

Descarga el `TFLSelection_189_SIX_EXACT_ASSETS_UPLOAD_KIT.zip` preparado en esta conversación. Son **seis archivos de aproximadamente 159 MiB en total**, por lo que su subida puede requerir unos minutos según tu conexión. Extráelo y adjunta a la Release **los seis archivos `sha256-*.bin`**, no el ZIP ni los archivos de texto.

**El séptimo archivo** es `tflcore-source.zip`: accede al [Release privado TFL Core v0.5.0-visual-preview.1](https://github.com/TFLivesStudio/TFLClientMOD/releases/tag/v0.5.0-visual-preview.1), descarga **`tflcore-source.zip`** y añádelo al mismo borrador. SHA-256 esperado `3d19f304eccc6e239fcfc36303d742b83e00165533ca037cc760360910ce0c11`, tamaño **136468685 bytes**. El workflow rechazará otra versión.

**No pulses Publish Release desde la página de edición del borrador.** Solo los workflow validan, firman y publican.

### 3. Verificar sin publicar

Vuelve a Actions y ejecuta el mismo workflow con task = **verify-only**. Comprueba que la ejecución finaliza en verde. Validará las seis copias por SHA-256/bytes/metadata, las cinco descargas públicas, las fuentes de los forks y las fuentes privadas de TFL Core. Descarga solo si quieres el artifact `tfl-selection-189-verification-report`; contiene metadata, no tus JARs.

### 4. Crear una firma propia de TFLives (una sola vez)

No reutilices un secreto de otro servicio ni publiques la clave en un chat o repositorio. En PowerShell de tu PC:

```powershell
py -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

Copia la cadena resultante. Ve a [GitHub repo Settings — Actions Secrets](https://github.com/TFLivesStudio/TFLClientSelection/settings/secrets/actions) → **New repository secret**. Nombre exacto:

```
TFL_SELECTION_SIGNING_SEED_B64
```

Valor: la cadena generada. Es una **semilla Ed25519 privada**: mantenla solo en Secrets y en una copia segura privada. El workflow derivará la clave pública y la almacenará en `keys/current.pub` del repositorio al publicar. No introduzcas ninguna clave privada en este chat.

### 5. Publicar la beta firmada

Revisa el informe, los cinco snapshots de fuente, el ZIP de fuente de TFL Core y las condiciones de redistribución del SDK NVIDIA incluidas en Amplio. Los archivos fuente serán **públicos**, incluida la fuente de TFL Core GPLv3 procedente de tu repositorio privado; comprueba antes que no contengan secretos.

Ejecuta Actions nuevamente con task = **publish-beta**, marcando **confirm_sources_and_nvidia_terms**. El workflow solo completará la publicación si los siete archivos están presentes y todos los hashes, fuentes, licencias y firma pasan la verificación. Creará catálogo firmado **beta**, no estable.

## Cómo sabremos que se terminó la distribución

1. En Releases de TFLClientSelection existe la tag `selection-mc-1.8.9-ornithe-v0.1.0-preview.1` publicada como prerelease, con los seis JARs originales, source-*.zip, notices, `manifest.json` y `manifest.json.sig`.
2. El repo contiene `releases/mc-1.8.9-ornithe/0.1.0-preview.1.json`, su firma, `catalog/current.json`, su firma y `keys/current.pub`.
3. El catálogo apunta a la nueva release **beta**, y sus 11 JARs están accesibles por HTTPS con el hash exacto.
4. TFL Client será una fase posterior: aún faltará probar instalación, Ornithe Gen2, Azul Zulu Java 25, firmas, rollback y ejecución. No afirmar que la prueba de arranque del launcher pasó antes de implementarlo.

**Nota legal:** los commits fuente candidatos están fijados a la versión declarada, pero la metadata del JAR no incluye evidencia criptográfica de su revisión de compilación. Quien autorice la publicación debe comprobar la correspondencia exacta de las modificaciones y las dependencias empaquetadas, especialmente NVIDIA, antes de marcar el consentimiento.
