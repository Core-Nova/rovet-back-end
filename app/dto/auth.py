from pydantic import BaseModel, EmailStr

# TODO: If Config classes become repeatable across DTOs, extract to a common config module.
# Nested classes are usually avoided in favor of shared configuration.


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
