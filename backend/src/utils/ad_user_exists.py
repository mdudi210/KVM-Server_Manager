import os
import uuid

import ldap3
from dotenv import load_dotenv
from fastapi import HTTPException
from ldap3.core.exceptions import LDAPException

from backend.config.logging_setting import setup_logger

load_dotenv()
logger = setup_logger("ad_user_check")

ad_server = os.getenv("AD_SERVER")
ad_base_dn = os.getenv("AD_BASE_DN")
ad_bind_user = os.getenv("AD_BIND_USER")
ad_bind_password = os.getenv("AD_BIND_PASSWORD")


def ad_user_exists(user_id: str) -> bool:
    if not ad_server or not ad_base_dn or not ad_bind_user or not ad_bind_password:
        raise HTTPException(status_code=500, detail="AD user lookup configuration is incomplete")

    try:
        server = ldap3.Server(ad_server, get_info=ldap3.ALL)

        clean_id = user_id.strip("{}")
        guid_obj = uuid.UUID(clean_id)
        escaped = "".join([f"\\{b:02X}" for b in guid_obj.bytes_le])
        search_filter = f"(objectGUID={escaped})"

        with ldap3.Connection(
            server,
            user=ad_bind_user,
            password=ad_bind_password,
            auto_bind=True,
            check_names=True,
        ) as conn:
            conn.search(search_base=ad_base_dn, search_filter=search_filter, attributes=["cn"])
            if not conn.entries:
                raise HTTPException(status_code=403, detail="User disabled/removed in AD")
            return True

    except HTTPException:
        raise
    except (ValueError, LDAPException):
        raise HTTPException(status_code=400, detail="Problem with AD server")
