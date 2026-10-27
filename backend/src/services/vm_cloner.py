from fastapi import APIRouter, HTTPException, Depends
from backend.src.utils.ssh import ssh_client, execute_ssh_command
from backend.src.schema.schema import CloneRequest
from backend.src.auth.admin_auth import verify_admin
from backend.config.logging_setting import setup_logger
from backend.src.services.vm_events import publish_event
import shlex 
import os
from dotenv import load_dotenv

load_dotenv()

LINUX_TEMPLATE = os.getenv("LINUX_TEMPLATE")
WIN_TEMPLATE = os.getenv("WIN_TEMPLATE")

router = APIRouter()
logger = setup_logger("vm_clone")


@router.post("/vm/clone")
def create_clone(data: CloneRequest, claims=Depends(verify_admin)):
    client = ssh_client()

    safe_vm_name = shlex.quote(data.name)

    if data.vmtoinstall == "Linux":
        command = f"sudo virt-clone --original {LINUX_TEMPLATE} --name {safe_vm_name} --file /home/{safe_vm_name}.qcow2"
    elif data.vmtoinstall == "Windows":
        command = f"sudo virt-clone --original {WIN_TEMPLATE} --name {safe_vm_name} --file /home/{safe_vm_name}.qcow2"
    else:
        logger.warning(f"Invalid VM type entered: {data.vmtoinstall}")
        raise HTTPException(status_code=400, detail="Invalid VM Type")

    try:
        output, error = execute_ssh_command(client, command)

        if error:
            logger.error(
                f"{claims.get('sub')} encountered error while cloning {data.vmtoinstall} VM '{data.name}': {error}"
            )
            raise HTTPException(status_code=500, detail="Failed to clone VM")

        logger.info(
            f"{claims.get('sub')} cloned {data.vmtoinstall} VM successfully: {data.name}"
        )
        publish_event(
            {
                "event": "vm_cloned",
                "vm_name": data.name,
                "vm_type": data.vmtoinstall,
                "cloned_by": claims.get("sub"),
            }
        )
        return {
            "Message": f"{data.vmtoinstall} VM cloned successfully",
            "Body": {"output": output},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during VM clone operation")
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        client.close()
