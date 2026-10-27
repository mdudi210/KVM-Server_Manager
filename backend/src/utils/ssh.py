import os

import paramiko
from dotenv import load_dotenv
from fastapi import HTTPException

from backend.config.logging_setting import setup_logger

load_dotenv()

hostname = os.getenv("SSH_HOSTNAME")
username = os.getenv("SSH_USERNAME")
password = os.getenv("SSH_PASSWORD")
SSH_CONNECT_TIMEOUT = int(os.getenv("SSH_CONNECT_TIMEOUT", "10"))
SSH_AUTO_ADD_HOST_KEYS = os.getenv("SSH_AUTO_ADD_HOST_KEYS", "true").lower() in {"1", "true", "yes"}

logger = setup_logger("ssh_command")


def ssh_client() -> paramiko.SSHClient:
    if not hostname or not username or not password:
        raise HTTPException(status_code=500, detail="SSH configuration is incomplete")

    try:
        client = paramiko.SSHClient()
        if SSH_AUTO_ADD_HOST_KEYS:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=hostname,
            username=username,
            password=password,
            timeout=SSH_CONNECT_TIMEOUT,
            banner_timeout=SSH_CONNECT_TIMEOUT,
            auth_timeout=SSH_CONNECT_TIMEOUT,
        )
        return client
    except paramiko.AuthenticationException:
        logger.warning("SSH authentication failed")
        raise HTTPException(status_code=500, detail="SSH authentication failed")
    except paramiko.SSHException as e:
        logger.warning("SSH connection error: %s", e)
        raise HTTPException(status_code=500, detail="SSH connection failed")
    except Exception as e:
        logger.exception("Unexpected SSH error")
        raise HTTPException(status_code=500, detail="SSH connection failed")


def execute_ssh_command(client: paramiko.SSHClient, command: str) -> tuple[str, str]:
    try:
        _, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        return output, error
    except Exception:
        logger.exception("SSH command execution failed")
        raise HTTPException(status_code=500, detail="SSH command execution failed")
