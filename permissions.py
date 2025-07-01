
from glean_indexing_api_client.model.document_permissions_definition import DocumentPermissionsDefinition

permissions = DocumentPermissionsDefinition(
            allowed_users=[author] if author else [],
            allowed_groups=ALLOWED_GROUPS,
            allowed_group_intersections=[],
            allow_anonymous_access=False
        )
