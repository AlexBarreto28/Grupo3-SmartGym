from datetime import datetime
from http import HTTPStatus


class ReglaNegocioException(Exception):

    def __init__(self, codigo_interno: str, mensaje: str, status_code: int = HTTPStatus.CONFLICT):
        try:
            codigo = int(status_code)
        except (TypeError, ValueError):
            codigo = int(HTTPStatus.CONFLICT)

        self.status_code = codigo
        try:
            self.error = HTTPStatus(codigo).phrase
        except ValueError:
            self.error = "Error"

        self.codigo_interno = codigo_interno
        self.mensaje = mensaje
        self.timestamp = datetime.utcnow().isoformat() + "Z"