from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.core.di.services import get_group_service
from src.core.di.user import CurrentUser
from src.schemas.group import GroupCreate, GroupInfo, GroupMemberAdd, GroupMemberRemove
from src.services.group import GroupService

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_group(
    data: GroupCreate,
    current_user: CurrentUser,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupInfo:
    return await service.create_group(data, current_user)


@router.get("/{group_id}")
async def get_group(
    group_id: UUID,
    current_user: CurrentUser,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupInfo:
    return await service.get_group(group_id, current_user)


@router.post("/{group_id}/members")
async def add_members(
    group_id: UUID,
    data: GroupMemberAdd,
    current_user: CurrentUser,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupInfo:
    return await service.add_members(group_id, data, current_user)


@router.delete("/{group_id}/members")
async def remove_members(
    group_id: UUID,
    data: GroupMemberRemove,
    current_user: CurrentUser,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> GroupInfo:
    return await service.remove_members(group_id, data, current_user)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: UUID,
    current_user: CurrentUser,
    service: Annotated[GroupService, Depends(get_group_service)],
) -> None:
    await service.delete_group(group_id, current_user)
