# backend/app/services/drive.py
# Client da API Google Drive.
# Cria pastas por empresa/ano/mês/data e faz upload de arquivos.

import structlog

from app.core.config import get_settings

logger = structlog.get_logger()


class GoogleDriveClient:
    """Client para Google Drive API usando service account."""

    def __init__(self):
        settings = get_settings()
        self.credentials_path = settings.GOOGLE_DRIVE_CREDENTIALS_PATH
        self._service = None

    def _get_service(self):
        """Cria o service client do Google Drive."""
        if self._service:
            return self._service

        if not self.credentials_path:
            logger.warning("drive_nao_configurado")
            return None

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/drive"],
            )
            self._service = build("drive", "v3", credentials=creds)
            return self._service
        except Exception as e:
            logger.error("drive_auth_erro", erro=str(e))
            return None

    def criar_pasta(self, nome: str, parent_id: str | None = None) -> str | None:
        """Cria uma pasta no Drive. Retorna o ID da pasta."""
        service = self._get_service()
        if not service:
            return None

        metadata = {
            "name": nome,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]

        try:
            folder = service.files().create(body=metadata, fields="id").execute()
            logger.info("drive_pasta_criada", nome=nome, id=folder["id"])
            return folder["id"]
        except Exception as e:
            logger.error("drive_criar_pasta_erro", nome=nome, erro=str(e))
            return None

    def criar_estrutura_empresa(self, empresa_nome: str, ano: int, mes: int, dia: int, parent_id: str | None = None) -> dict:
        """
        Cria estrutura de pastas: Empresa/Ano/Mês/Dia
        Retorna dict com IDs de cada nível.
        """
        ids = {}
        ids["empresa"] = self.criar_pasta(empresa_nome, parent_id)
        if ids["empresa"]:
            ids["ano"] = self.criar_pasta(str(ano), ids["empresa"])
        if ids.get("ano"):
            ids["mes"] = self.criar_pasta(f"{mes:02d}", ids["ano"])
        if ids.get("mes"):
            ids["dia"] = self.criar_pasta(f"{dia:02d}", ids["mes"])
        return ids
