import os
from django.conf import settings

ALLOWED_FILE_EXTENSIONS = {
    '.pdf',
    '.doc', '.docx',
    '.xls', '.xlsx',
    '.ppt', '.pptx',
    '.stp',
}

# Magic bytes/header → extensiones compatibles con esa firma.
# OLE2 cubre los formatos Office clásicos (.doc, .xls, .ppt).
# ZIP cubre Office Open XML (.docx, .xlsx, .pptx).
# STP (ISO-10303) es texto ASCII — su cabecera es 'ISO-10303'.
_MAGIC = {
    b'%PDF':                     {'.pdf'},
    b'\xD0\xCF\x11\xE0':        {'.doc', '.xls', '.ppt'},
    b'PK\x03\x04':              {'.docx', '.xlsx', '.pptx'},
    b'ISO-10303':                {'.stp'},
}


def _mime_valido(archivo, ext):
    """Lee los primeros 16 bytes y verifica que correspondan a la extensión declarada."""
    header = archivo.read(16)
    archivo.seek(0)
    for magic, extensiones in _MAGIC.items():
        if header.startswith(magic):
            return ext in extensiones
    return False


def validar_archivos(archivos):
    """
    Valida extensión, MIME real, tamaño y cantidad de archivos.
    Devuelve un dict con los errores encontrados; vacío si todo es válido.

    Claves posibles del dict:
        'cantidad'  — se superó MAX_FILES_PER_REQUEST
        'invalidos' — lista de nombres con extensión no permitida
        'mime'      — lista de nombres cuyo contenido no coincide con la extensión
        'tamanio'   — lista de nombres que superan MAX_UPLOAD_SIZE_MB
    """
    max_archivos = getattr(settings, 'MAX_FILES_PER_REQUEST', 10)
    max_mb       = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 10)
    max_bytes    = max_mb * 1024 * 1024

    errores = {}

    if len(archivos) > max_archivos:
        errores['cantidad'] = f'Se permiten máximo {max_archivos} archivos por solicitud. Se recibieron {len(archivos)}.'
        return errores  # no seguir si ya supera el límite global

    ext_invalida = []
    mime_invalido = []
    muy_grande    = []

    for archivo in archivos:
        ext = os.path.splitext(archivo.name)[1].lower()

        if ext not in ALLOWED_FILE_EXTENSIONS:
            ext_invalida.append(archivo.name)
            continue  # no checar MIME si ya la extensión es inválida

        if archivo.size > max_bytes:
            muy_grande.append(archivo.name)

        if not _mime_valido(archivo, ext):
            mime_invalido.append(archivo.name)

    if ext_invalida:
        errores['invalidos'] = ext_invalida
    if mime_invalido:
        errores['mime'] = mime_invalido
    if muy_grande:
        errores['tamanio'] = muy_grande

    return errores
