from enum import StrEnum, auto
from typing import Literal

from pydantic import BaseModel, constr

VmName = constr(regex=r"^[A-Za-z0-9._-]{1,63}$")
Username = constr(strip_whitespace=True, min_length=1, max_length=128)
Password = constr(min_length=1, max_length=256)


class Roles(StrEnum):
    user = auto()
    admin = auto()


class State(StrEnum):
    start = auto()
    shutdown = auto()
    destroy = auto()
    reboot = auto()


class ChangeState(BaseModel):
    state: State
    name: VmName
    expected_state: str | None = None


class CloneRequest(BaseModel):
    vmtoinstall: Literal["Linux", "Windows"]
    name: VmName


class NewVmRequest(BaseModel):
    vmtoinstall: Literal["Linux", "Windows"]
    name: VmName


class LoginRequest(BaseModel):
    username: Username
    password: Password
    auth_provider: Literal["local", "ad"] = "local"


class NewUser(BaseModel):
    username: Username
    password: Password
    role: Roles
