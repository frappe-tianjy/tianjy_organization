import frappe
#import traceback

patches_loaded = False
import tianjy_organization.patches.db_query

#traceback.print_stack()

def load_patches():
	global patches_loaded
	import os
	import importlib

	if (
		patches_loaded
		or not getattr(frappe, "conf", None)
		or not "tianjy_organization" in frappe.get_installed_apps()
	):
		return
	patches_loaded = True

	folder = frappe.get_app_path('tianjy_organization', "patches")
	if not os.path.exists(folder): return

	for module_name in os.listdir(folder):
		if not module_name.endswith(".py") or module_name == "__init__.py":
			continue
		importlib.import_module(f"tianjy_organization.patches.{module_name[:-3]}")
