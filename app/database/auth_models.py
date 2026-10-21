
from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user"
    )

    permission_overrides: Mapped[list["UserPermissionOverride"]] = relationship(
        back_populates="user"
    )

class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    users: Mapped[list["UserRole"]] = relationship(
        back_populates="role"
    )

    permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role"
    )

class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.role_id"), primary_key=True
    )
    user: Mapped["User"] = relationship(
        back_populates="roles"
    )
    role: Mapped["Role"] = relationship(
        back_populates="users"
    )

class Permission(Base):
    __tablename__ = "permissions"

    permission_id: Mapped[int] = mapped_column(primary_key=True)
    permission_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    roles: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission"
    )
    user_overrides: Mapped[list["UserPermissionOverride"]] = relationship(
        back_populates="permission"
    )

class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.role_id"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.permission_id"), primary_key=True
    )
    role: Mapped["Role"] = relationship(
        back_populates="permissions"
    )
    permission: Mapped["Permission"] = relationship(
        back_populates="roles"
    )

class UserPermissionOverride(Base):
    __tablename__ = "user_permission_overrides"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.permission_id"), primary_key=True
    )
    is_allowed: Mapped[bool] = mapped_column(
        Boolean, nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="permission_overrides"
    )
    permission: Mapped["Permission"] = relationship(
        back_populates="user_overrides"
    )
