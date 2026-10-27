import shlex

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.config.logging_setting import setup_logger
from backend.src.auth.user_auth import verify_user
from backend.src.utils.parse_vm_status import parse_vm_status
from backend.src.utils.ssh import execute_ssh_command, ssh_client

router = APIRouter()
logger = setup_logger("vm_endpoint")


@router.get("/vm")
def list_all_vm(claims: dict = Depends(verify_user), vm_name: str | None = Query(default=None)):
    client = ssh_client()

    try:
        if vm_name:
            safe_vm_name = shlex.quote(vm_name)
            command = f"virsh domstate {safe_vm_name}"
            output, error = execute_ssh_command(client, command)
            output = output.strip().lower()
        else:
            command = "virsh list --all"
            output, error = execute_ssh_command(client, command)
            if output:
                output = parse_vm_status(output)

        if error:
            logger.error("%s encountered error while listing VMs: %s", claims.get("sub"), error)
            raise HTTPException(status_code=500, detail="Unable to fetch VM information")

        logger.info("%s retrieved VM info successfully", claims.get("sub"))
        return {
            "Message": "VM info retrieved successfully",
            "Body": {"output": output},
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error occurred while retrieving VM info")
        raise HTTPException(status_code=500, detail="Unexpected error while retrieving VM info")
    finally:
        client.close()
