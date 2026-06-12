import os
from pathlib import Path

class CredentialManager:
    @staticmethod
    def read_credential(credential_name: str) -> str:
        credentials_directory = os.getenv("CREDENTIALS_DIRECTORY")

        if credentials_directory:
            credential_path = Path(credentials_directory) / credential_name
        else:
            credential_path = (
                Path.home()
                / ".config"
                / "eswunb_bot"
                / "credentials"
                / f"{credential_name}.cred"
            )

        if not credential_path.is_file():
            raise FileNotFoundError(
                f"A credencial '{credential_name}' não foi encontrada."
            )

        return credential_path.read_text(encoding="utf-8").strip()
