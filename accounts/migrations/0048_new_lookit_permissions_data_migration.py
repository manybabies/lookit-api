# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-13 15:53
from __future__ import unicode_literals

from django.db import migrations

from accounts.permissions import LookitGroup, LookitPermission


def _create_groups(
    model_instance, group_enum, group_class, perm_class, group_object_permission_model
):
    uuid_segment = str(model_instance.uuid)[:7]
    object_name = model_instance._meta.object_name
    unique_group_tag = (
        f"{object_name} :: {model_instance.name[:7]}... ({uuid_segment}...)"
    )

    for group_spec in group_enum:
        # Group name is going to be something like "READ :: Lab :: MIT (0235dfa...)
        group_name = f"{group_spec.name} :: {unique_group_tag}"
        group = group_class.objects.create(name=group_name)

        for permission_meta in group_spec.value:
            permission = perm_class.objects.get(codename=permission_meta.codename)

            group_object_permission_model.objects.create(
                content_object=model_instance, permission=permission, group=group
            )
            group.save()

        setattr(model_instance, f"{group_spec.name.lower()}_group", group)

    model_instance.save()


def apply_migration(apps, schema_editor):
    """Lab group changes.

    Args:
        apps: instance of django.apps.registry.Apps
        schema_editor: instance of django.db.backends.base.schema.BaseDatabaseSchemaEditor

    Side Effects:
        Adds Lookit-wide groups & permissions and assigns permissions to groups.
    """

    # Treat this like module scope, since we can't import and have to deal with historical
    # models.
    Lab = apps.get_model("studies", "Lab")
    Study = apps.get_model("studies", "Study")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # Create Lookit-wide permissions
    for perm_spec_obj in LookitPermission:
        perm_spec = perm_spec_obj.value
        if not Permission.objects.filter(codename=perm_spec.codename).exists():
            Permission.objects.create(
                codename=perm_spec.codename,
                name=perm_spec.name,
                content_type=perm_spec.content_type,
            )
        else:
            perm = Permission.objects.get(codename=perm_spec.codename)
            perm.name = perm_spec.name
            perm.content_type = perm_spec.content_type
            perm.save()
    # Create Lookit-wide groups and assign permissions
    for group_spec in LookitGroup:
        if not Group.objects.filter(name=group_spec.name).exists():
            group = Group.objects.create(name=group_spec.name)
        else:
            group = Group.objects.get(name=group_spec.name)
            group.permissions.set(
                Permission.objects.none()
            )  # remove any existing permissions that may be different
        for perm_spec in group_spec.value:
            permission = Permission.objects.get(codename=perm_spec.codename)
            group.permissions.add(permission)
        group.save()


def revert_migration(apps, schema_editor):
    """Reverses the migration, deleting Lookit-wide groups and perms

    Args:
        apps: instance of django.apps.registry.Apps
        schema_editor: instance of django.db.backends.base.schema.BaseDatabaseSchemaEditor
    """
    Lab = apps.get_model("studies", "Lab")
    Study = apps.get_model("studies", "Study")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for group_spec in LookitGroup:
        Group.objects.filter(name=group_spec.value["name"]).delete()

    for perm_spec in LookitPermission:
        Permission.objects.filter(codename=perm_spec.value["codename"]).delete()


class Migration(migrations.Migration):
    dependencies = [("accounts", "0047_remove_user_organization")]

    operations = [migrations.RunPython(apply_migration, revert_migration)]
