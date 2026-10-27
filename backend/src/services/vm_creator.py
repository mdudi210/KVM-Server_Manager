from fastapi import APIRouter, HTTPException, Depends
from backend.src.utils.ssh import ssh_client, execute_ssh_command
from backend.src.schema.schema import NewVmRequest
from backend.src.auth.admin_auth import verify_admin
from backend.config.logging_setting import setup_logger
from backend.src.services.vm_events import publish_event
import shlex
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
logger = setup_logger("vm_new")

LINUX_ISO = os.getenv("LINUX_ISO")
WIN_ISO = os.getenv("WIN_ISO")


@router.post("/vm/new")
def create_new_vm(data: NewVmRequest, claims=Depends(verify_admin)):
    client = ssh_client()

    safe_vm_name = shlex.quote(data.name)

    if data.vmtoinstall == "Linux":
        command = (
            f"sudo virt-install --name {safe_vm_name} --memory 2534 --vcpus 2 "
            f"--cpu host-passthrough --os-variant centos-stream9 "
            f"--disk path=/home/{safe_vm_name}.qcow2,size=50,format=qcow2,bus=virtio "
            f"--cdrom {LINUX_ISO} "
            f"--network network=default,model=virtio --graphics vnc,listen=127.0.0.1 "
            f"--video virtio --channel unix,target_type=virtio,name=org.qemu.guest_agent.0 "
            f"--boot cdrom,hd --controller type=sata --features acpi=on,apic=on "
            f"--noautoconsole"
        )
    elif data.vmtoinstall == "Windows":
        command = (
            f"sudo virt-install --name {safe_vm_name} --memory 5192 --vcpus 2 "
            f"--cpu host-passthrough --os-variant win11 "
            f"--disk path=/home/{safe_vm_name}.qcow2,size=50,format=qcow2,bus=sata "
            f"--cdrom {WIN_ISO} "
            f"--network network=default,model=e1000e --graphics vnc --video bochs "
            f"--boot hd --controller type=sata --features acpi=on,apic=on "
            f"--noautoconsole"
        )
    else:
        logger.warning(f"Invalid VM type entered: {data.vmtoinstall}")
        raise HTTPException(status_code=400, detail="Invalid VM Type")

    try:
        output, error = execute_ssh_command(client, command)

        if error:
            logger.error(
                f"{claims.get('sub')} encountered error while creating {data.vmtoinstall} VM '{data.name}': {error}"
            )
            raise HTTPException(status_code=500, detail="Failed to create VM")

        logger.info(
            f"{claims.get('sub')} created {data.vmtoinstall} VM successfully: {data.name}"
        )
        publish_event(
            {
                "event": "vm_created",
                "vm_name": data.name,
                "vm_type": data.vmtoinstall,
                "created_by": claims.get("sub"),
            }
        )
        return {
            "Message": f"{data.vmtoinstall} VM created successfully",
            "Body": {"output": output},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during VM creation")
        raise HTTPException(status_code=500, detail=f"{e}")
    finally:
        client.close()
