"""SQLAdmin views for user management."""

from sqladmin import ModelView

from users.models import OTP, Group, Permission, Profile, User


class UserAdmin(ModelView, model=User):
    """Admin view for User model."""

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [
        User.id,
        User.email,
        User.phone,
        User.username,
        User.full_name,
        User.is_active,
        User.is_superuser,
        User.is_verified,
        User.created_at,
    ]

    column_searchable_list = [
        User.email,
        User.phone,
        User.username,
        User.full_name,
    ]
    column_sortable_list = [User.id, User.email, User.created_at]
    column_default_sort = [(User.created_at, True)]

    form_excluded_columns = [
        User.hashed_password,
        User.created_at,
        User.updated_at,
    ]

    column_details_exclude_list = [User.hashed_password]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True


class PermissionAdmin(ModelView, model=Permission):
    """Admin view for Permission model."""

    name = "Permission"
    name_plural = "Permissions"
    icon = "fa-solid fa-key"

    column_list = [
        Permission.id,
        Permission.name,
        Permission.codename,
        Permission.description,
        Permission.created_at,
    ]

    column_searchable_list = [
        Permission.name,
        Permission.codename,
        Permission.description,
    ]
    column_sortable_list = [
        Permission.id,
        Permission.name,
        Permission.created_at,
    ]
    column_default_sort = [(Permission.name, False)]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True
    can_view_details = True
    can_export = True


class GroupAdmin(ModelView, model=Group):
    """Admin view for Group model."""

    name = "Group"
    name_plural = "Groups"
    icon = "fa-solid fa-users"

    column_list = [
        Group.id,
        Group.name,
        Group.description,
        Group.created_at,
    ]

    column_searchable_list = [Group.name, Group.description]
    column_sortable_list = [Group.id, Group.name, Group.created_at]
    column_default_sort = [(Group.name, False)]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True


class ProfileAdmin(ModelView, model=Profile):
    """Admin view for Profile model."""

    name = "Profile"
    name_plural = "Profiles"
    icon = "fa-solid fa-id-card"

    column_list = [
        Profile.id,
        Profile.user_id,
        Profile.avatar_url,
        Profile.city,
        Profile.country,
        Profile.created_at,
    ]

    column_searchable_list = [Profile.city, Profile.country, Profile.bio]
    column_sortable_list = [Profile.id, Profile.created_at]
    column_default_sort = [(Profile.created_at, True)]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True


class OTPAdmin(ModelView, model=OTP):
    """Admin view for OTP model."""

    name = "OTP"
    name_plural = "OTPs"
    icon = "fa-solid fa-lock"

    column_list = [
        OTP.id,
        OTP.email,
        OTP.purpose,
        OTP.code,
        OTP.is_used,
        OTP.attempts,
        OTP.expires_at,
        OTP.created_at,
    ]

    column_searchable_list = [OTP.email, OTP.purpose]
    column_sortable_list = [
        OTP.id,
        OTP.created_at,
        OTP.expires_at,
    ]
    column_default_sort = [(OTP.created_at, True)]

    form_excluded_columns = [OTP.created_at]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True
