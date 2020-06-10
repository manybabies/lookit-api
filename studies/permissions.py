"""
Data structures & functions for the object-based permissions in Lookit.

These must be defined *outside* of the database/guardian tables for two
purposes:
1) serving as a source of truth,
and
2) usage in migrations.

We are using naming conventions that build upon that set by Django itself,
while adding some structural and syntactical elements that help us reason
about permissions in a more queryset-centric way.

As of 2.0, the default per-model permissions added by django.contrib.auth
include:

- ${app_name}.add_${model}
- ${app_name}.change_${model}
- ${app_name}.delete_${model}
- ${app_name}.view_${model}

To enhance this while still leveraging the generated defaults, we have
a few additional field-specific conventions.

- ${app_name}.edit_${model}__${field}
- ${app_name}.read_${model}__${field}

In this context, "Edit" is analogous to "Change", but restricted to a single
field within the specified model. Similarly, "Read" is analogous to "View"
for a single field within a model.

If the specified field is a relationship of some kind (OneToOne, ForeignKey,
etc.) then the model-level variant of the permission (i.e. "Change" or "View")
applies, but only to the *related* model instance(s). The "dunder" syntax should
feel familiar from querysets, and allows for for arbitrary nesting as such:

- ${app_name}.read_${model}__${field}__${subfield}__...

and even filters, using postfixed parenthetical key-value pairs:

read_study__responses(is_preview=True)

The final subfield may have or'd regex-like syntax for multiple fields,
like so:

read_study__[name|public|state|min_age_years|max_age_years|...]

To complete the correspondence between per-model and per-object permissions,
we need two additional field-level permissions to associate and dissociate
existing instances of the relation's specified model.

- ${app_name}.associate_${model}__${field}
- ${app_name}.dissociate_${model}__${field}

This allows us to be MECE with the "Add" and "Delete" permissions of the
related model.

There will be the occasional case where we wish to specify data that is
either a composite of many fields, or some kind of summary data.
Given the 100 char max length of Permission, we can't list too many
fields or a complex queryset serialization, so there's the choice
of arbitrary delimiters in ANGRY_SNAKE_CASE, caret-delimited style:

read_study__<ANALYTICS>
read_study__<DETAILS>

This gives the permission author the flexibility to "kick the can down the
road" in terms of properly segmenting permissions, or represent things
that simply aren't modeled in the database.
"""

from collections import namedtuple
from enum import Enum

# Upgrade to python 3.8 for cached_property
# from functools import cached_property
from typing import NamedTuple, Tuple

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from project.permissions import _PermissionMeta, _PermissionName, _PermissionParts


def create_lab_version(study_permission: _PermissionMeta):
    permission, model_name, relationship_path, target_fields = study_permission.parts
    if model_name == "lab":
        raise TypeError("This permission is already lab specific!")

    description = study_permission.description

    relationship_path = (model_name,) + relationship_path

    return _PermissionMeta.from_parts(
        permission,
        "lab",
        relationship_path,
        target_fields,
        f"{description} (for all studies in the lab)",
    )


class StudyPermission(_PermissionMeta, Enum):
    READ_STUDY_DETAILS = _PermissionMeta(
        codename=f"read_study__<DETAILS>",
        description="Read study details and preview study",
    )
    WRITE_STUDY_DETAILS = _PermissionMeta(
        codename=f"edit_study__<DETAILS>", description="Write study details"
    )
    CHANGE_STUDY_STATUS = _PermissionMeta(
        codename="edit_study__status", description="Change study status"
    )
    MANAGE_STUDY_RESEARCHERS = _PermissionMeta(
        codename="edit_study__<GROUP>__user_set", description="Manage study researchers"
    )
    READ_STUDY_RESPONSE_DATA = _PermissionMeta(
        codename="read_study__responses",
        description="View/download study response data",
    )
    READ_STUDY_PREVIEW_DATA = _PermissionMeta(
        codename="read_study__responses(is_preview=True)",
        description="View/download preview data",
    )
    CODE_STUDY_CONSENT = _PermissionMeta(
        codename="edit_study__responses__consent_rulings",
        description="Code consent for study",
    )
    CONTACT_STUDY_PARTICIPANTS = _PermissionMeta(
        codename="edit_study__message_set", description="Contact participants for study"
    )
    EDIT_STUDY_FEEDBACK = _PermissionMeta(
        codename="edit_study__feedback", description="Edit feedback for study"
    )
    CHANGE_STUDY_LAB = _PermissionMeta(
        codename="edit_study__lab", description="Change the associated lab for study"
    )
    DELETE_ALL_PREVIEW_DATA = _PermissionMeta(
        codename="delete_study__responses(is_preview=True)",
        description="Delete preview data for study",
    )


UMBRELLA_LAB_PERMISSION_MAP = {
    study_perm: create_lab_version(study_perm) for study_perm in StudyPermission
}


class LabPermission(_PermissionMeta, Enum):
    CREATE_LAB_ASSOCIATED_STUDY = _PermissionMeta(
        codename="associate_lab__study", description="Associate a study with a lab"
    )
    MANAGE_LAB_RESEARCHERS = _PermissionMeta(
        codename="edit_lab__<GROUPS>", description="Manage researchers in a lab"
    )
    EDIT_LAB_METADATA = _PermissionMeta(
        codename="edit_lab__<DETAILS>", description="Edit the metadata for a lab"
    )

    READ_STUDY_DETAILS = UMBRELLA_LAB_PERMISSION_MAP[StudyPermission.READ_STUDY_DETAILS]

    WRITE_STUDY_DETAILS = UMBRELLA_LAB_PERMISSION_MAP[
        StudyPermission.WRITE_STUDY_DETAILS
    ]

    CHANGE_STUDY_STATUS = UMBRELLA_LAB_PERMISSION_MAP[
        StudyPermission.CHANGE_STUDY_STATUS
    ]

    MANAGE_STUDY_RESEARCHERS = UMBRELLA_LAB_PERMISSION_MAP[
        StudyPermission.MANAGE_STUDY_RESEARCHERS
    ]

    READ_STUDY_RESPONSE_DATA = UMBRELLA_LAB_PERMISSION_MAP[
        StudyPermission.READ_STUDY_RESPONSE_DATA
    ]

    READ_STUDY_PREVIEW_DATA = UMBRELLA_LAB_PERMISSION_MAP[
        StudyPermission.READ_STUDY_PREVIEW_DATA
    ]

    CODE_STUDY_CONSENT = UMBRELLA_LAB_PERMISSION_MAP[StudyPermission.CODE_STUDY_CONSENT]

    CONTACT_STUDY_PARTICIPANTS = UMBRELLA_LAB_PERMISSION_MAP[
        StudyPermission.CONTACT_STUDY_PARTICIPANTS
    ]

    EDIT_STUDY_FEEDBACK = UMBRELLA_LAB_PERMISSION_MAP[
        StudyPermission.EDIT_STUDY_FEEDBACK
    ]

    CHANGE_STUDY_LAB = UMBRELLA_LAB_PERMISSION_MAP[StudyPermission.CHANGE_STUDY_LAB]

    DELETE_ALL_PREVIEW_DATA = UMBRELLA_LAB_PERMISSION_MAP[
        StudyPermission.DELETE_ALL_PREVIEW_DATA
    ]


class LabGroup(set, Enum):
    READ = {LabPermission.READ_STUDY_DETAILS, LabPermission.READ_STUDY_PREVIEW_DATA}
    ADMIN = {
        # Umbrella permissions
        LabPermission.READ_STUDY_PREVIEW_DATA,
        LabPermission.WRITE_STUDY_DETAILS,
        LabPermission.CHANGE_STUDY_STATUS,
        LabPermission.MANAGE_LAB_RESEARCHERS,
        # Lab-centric permissions
        LabPermission.CREATE_LAB_ASSOCIATED_STUDY,
        LabPermission.EDIT_LAB_METADATA,
        LabPermission.MANAGE_STUDY_RESEARCHERS,
    }


class StudyGroup(set, Enum):
    PREVIEW = {
        StudyPermission.READ_STUDY_DETAILS,
        StudyPermission.READ_STUDY_PREVIEW_DATA,
    }
    DESIGN = {
        StudyPermission.READ_STUDY_DETAILS,
        StudyPermission.READ_STUDY_PREVIEW_DATA,
        StudyPermission.DELETE_ALL_PREVIEW_DATA,
        StudyPermission.WRITE_STUDY_DETAILS,
    }
    ANALYSIS = {
        StudyPermission.READ_STUDY_DETAILS,
        StudyPermission.READ_STUDY_PREVIEW_DATA,
        StudyPermission.DELETE_ALL_PREVIEW_DATA,
        StudyPermission.READ_STUDY_RESPONSE_DATA,
    }
    SUBMISSION_PROCESSOR = {
        StudyPermission.READ_STUDY_DETAILS,
        StudyPermission.READ_STUDY_PREVIEW_DATA,
        StudyPermission.DELETE_ALL_PREVIEW_DATA,
        StudyPermission.CHANGE_STUDY_STATUS,
        StudyPermission.CODE_STUDY_CONSENT,
        StudyPermission.EDIT_STUDY_FEEDBACK,
        StudyPermission.CONTACT_STUDY_PARTICIPANTS,
    }
    RESEARCHER = {
        StudyPermission.READ_STUDY_DETAILS,
        StudyPermission.READ_STUDY_PREVIEW_DATA,
        StudyPermission.DELETE_ALL_PREVIEW_DATA,
        StudyPermission.CHANGE_STUDY_STATUS,
        StudyPermission.READ_STUDY_RESPONSE_DATA,
        StudyPermission.CODE_STUDY_CONSENT,
        StudyPermission.EDIT_STUDY_FEEDBACK,
        StudyPermission.CONTACT_STUDY_PARTICIPANTS,
    }
    MANAGER = {
        StudyPermission.READ_STUDY_DETAILS,
        StudyPermission.READ_STUDY_PREVIEW_DATA,
        StudyPermission.DELETE_ALL_PREVIEW_DATA,
        StudyPermission.WRITE_STUDY_DETAILS,
        StudyPermission.CHANGE_STUDY_STATUS,
        StudyPermission.MANAGE_STUDY_RESEARCHERS,
    }
    ADMIN = {
        StudyPermission.READ_STUDY_DETAILS,
        StudyPermission.READ_STUDY_PREVIEW_DATA,
        StudyPermission.DELETE_ALL_PREVIEW_DATA,
        StudyPermission.WRITE_STUDY_DETAILS,
        StudyPermission.EDIT_STUDY_FEEDBACK,
        StudyPermission.MANAGE_STUDY_RESEARCHERS,
        StudyPermission.READ_STUDY_RESPONSE_DATA,
        StudyPermission.CODE_STUDY_CONSENT,
        StudyPermission.CONTACT_STUDY_PARTICIPANTS,
        StudyPermission.CHANGE_STUDY_LAB,
    }


# Permissions for Lookit-wide groups affecting all studies/labs.
# Minimal now but a placeholder for where
# we can flesh out permissions for e.g. RAs working on tech support vs. recruitment.
# In studies app because perms do apply to Study, Lab models specifically; Lookit-wide
# groups are defined under accounts and perms relating to all users may be there also in the
# future.
# Codenames used here are NOT directly in line with model/study level perms used elsewhere
# for ease of avoiding conflicts and removing these permissions later.
