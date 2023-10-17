# Copyright (c) 2023, 天玑 Tinajy and contributors
# For license information, please see license.txt

# import frappe
from frappe.cache_manager import clear_user_cache
from frappe.utils.nestedset import NestedSet

from typing import Any
import frappe
from frappe.utils.nestedset import NestedSet

from ..tianjy_organization_type.tianjy_organization_type import TianjyOrganizationType


@frappe.whitelist()
def get_type(type=''):
    type = frappe.get_doc(TianjyOrganizationType.DOCTYPE, type)
    return dict(
        name=type.name,
        parent_types=[type.type for type in type.parent_types],
        doc_types=[type.doc_type for type in type.doc_types],
        root_only=bool(type.root_only),
        no_workspace=bool(type.no_workspace),
    )


class TianjyOrganization(NestedSet):
    DOCTYPE = "Tianjy Organization"

    @classmethod
    def find(cls, name: str) -> 'TianjyOrganization | None':
        try:
            return frappe.get_doc(cls.DOCTYPE, name)
        except:
            return

    def on_trash(self, allow_root_deletion=False):
        return super().on_trash(True)
        # TODO: 删除成员信息

    def after_delete(self):
        frappe.db.delete("DefaultValue", dict(
            defkey='tianjy_organization',
            defvalue=self.name
        ))
        clear_user_cache()
