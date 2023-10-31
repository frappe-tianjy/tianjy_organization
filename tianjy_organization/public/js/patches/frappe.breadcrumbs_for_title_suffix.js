frappe.breadcrumbs.set_workspace_breadcrumb = function(breadcrumbs){
	// get preferred module for breadcrumbs, based on history and module

	if (!breadcrumbs.workspace) {
		this.set_workspace(breadcrumbs);
	}
	if (!breadcrumbs.workspace) {
		return;
	}

	if (
		breadcrumbs.module_info &&
				(breadcrumbs.module_info.blocked ||
					!frappe.visible_modules.includes(breadcrumbs.module_info.module))
	) {
		return;
	}

	$(
		`<li><a href="/app/${frappe.router.slug(breadcrumbs.workspace)}">${__(
			breadcrumbs.workspace.replaceAll(/{{([^}]*)}}/g, ''),
		)}</a></li>`,
	).appendTo(this.$breadcrumbs);
};
