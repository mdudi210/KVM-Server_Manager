import os

import ldap3
from dotenv import load_dotenv
from fastapi import HTTPException
from ldap3.core.exceptions import LDAPException
from ldap3.utils.conv import escape_filter_chars

from backend.config.logging_setting import setup_logger
from backend.src.schema.schema import Roles

load_dotenv()
logger = setup_logger("ad_auth")

ad_server = os.getenv("AD_SERVER")
ad_base_dn = os.getenv("AD_BASE_DN")
ad_bind_user = os.getenv("AD_BIND_USER")
ad_bind_password = os.getenv("AD_BIND_PASSWORD")


def authenticate_with_ad(username: str, password: str) -> list:
    if not ad_server or not ad_base_dn:
        raise HTTPException(status_code=500, detail="AD configuration is incomplete")

    try:
        server = ldap3.Server(ad_server, get_info=ldap3.ALL)

        # Authenticate using supplied AD credentials.
        with ldap3.Connection(server, user=username, password=password, auto_bind=True, check_names=True):
            search_user = escape_filter_chars(username.split("@")[0])
            search_filter = f"(sAMAccountName={search_user})"

            # Query attributes with a service bind when available; fallback to user bind.
            bind_user = ad_bind_user or username
            bind_password = ad_bind_password or password

            with ldap3.Connection(server, user=bind_user, password=bind_password, auto_bind=True, check_names=True) as query_conn:
                query_conn.search(
                    search_base=ad_base_dn,
                    search_filter=search_filter,
                    attributes=["KVMrole", "objectGUID"],
                )

                if not query_conn.entries:
                    raise HTTPException(status_code=401, detail="Invalid AD credentials")

                user_entry = query_conn.entries[0]
                role = user_entry.KVMrole.value
                if role not in Roles.__members__:
                    logger.warning("Invalid role '%s' for AD user '%s'", role, username)
                    raise HTTPException(status_code=403, detail="Invalid role type")

                uid = str(user_entry.objectGUID.value)
                return [True, role, uid]

    except HTTPException:
        raise
    except LDAPException:
        raise HTTPException(status_code=401, detail="Invalid AD credentials")
