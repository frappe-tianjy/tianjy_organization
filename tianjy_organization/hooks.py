from . import __version__ as app_version

app_name = "tianjy_organization"
app_title = "Tianjy Organization"
app_publisher = "天玑 Tinajy"
app_description = "天玑组织 Tianjy Organization"
app_email = "天玑 Tinajy"
app_license = "MIT"

after_migrate = 'tianjy_organization.migrate.run'

app_include_css="/assets/tianjy_organization/css/tianjy_organization.css"
app_include_js="tianjy_organization.bundle.js"
permission_query_conditions = {
	"Tianjy Organization": "tianjy_organization.lib.get_organization_permission_query_conditions",
}

has_permission = {
	"Tianjy Organization": "tianjy_organization.lib.has_permission",
}
override_whitelisted_methods = {
	"frappe.desk.desktop.get_workspace_sidebar_items": "tianjy_organization.workspace.get_workspace_sidebar_items"
}

filters_config = "tianjy_organization.filter.get_filters_config"

doc_events = {
	"Tianjy Organization Inheritable": {
		"on_update": "tianjy_organization.tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member.inheritable_on_update",
		"on_trash": "tianjy_organization.tianjy_organization.doctype.tianjy_organization_member.tianjy_organization_member.inheritable_on_trash",
	},
}

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tianjy_organization/css/tianjy_organization.css"
# app_include_js = "/assets/tianjy_organization/js/tianjy_organization.js"

# include js, css files in header of web template
# web_include_css = "/assets/tianjy_organization/css/tianjy_organization.css"
# web_include_js = "/assets/tianjy_organization/js/tianjy_organization.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tianjy_organization/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "tianjy_organization.utils.jinja_methods",
#	"filters": "tianjy_organization.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "tianjy_organization.install.before_install"
# after_install = "tianjy_organization.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tianjy_organization.uninstall.before_uninstall"
# after_uninstall = "tianjy_organization.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tianjy_organization.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"tianjy_organization.tasks.all"
#	],
#	"daily": [
#		"tianjy_organization.tasks.daily"
#	],
#	"hourly": [
#		"tianjy_organization.tasks.hourly"
#	],
#	"weekly": [
#		"tianjy_organization.tasks.weekly"
#	],
#	"monthly": [
#		"tianjy_organization.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "tianjy_organization.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "tianjy_organization.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "tianjy_organization.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tianjy_organization.utils.before_request"]
# after_request = ["tianjy_organization.utils.after_request"]

# Job Events
# ----------
# before_job = ["tianjy_organization.utils.before_job"]
# after_job = ["tianjy_organization.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"tianjy_organization.auth.validate"
# ]
