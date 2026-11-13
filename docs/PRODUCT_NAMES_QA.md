# Verificación de nomenclatura

TFL Selection es la biblioteca; TFLClient es el cliente final; TFL Client es el
launcher. Referencia: [PRODUCT_NAMES.md](PRODUCT_NAMES.md).

El publicador aplica el nombre del cliente en futuras generaciones antes de
firmarlas. Los consumidores normalizan etiquetas históricas para mostrarlas.
No se modificaron catálogo actual, firmas ni manifiestos publicados; los tags
y assets existentes conservan su identidad. No se publicó otra generación.

Validación: cinco JSON correctos con scripts/validate_manifests.py y 45 pruebas
correctas con python -m unittest discover -s tests -v.
