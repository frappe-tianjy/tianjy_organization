frappe.views.Workspace.prototype.initialize_new_page = function () {
	var me = this;
	this.get_parent_pages();
	const d = new frappe.ui.Dialog({
		title: __('New Workspace'),
		fields: [
			{
				label: __('Title'),
				fieldtype: 'Data',
				fieldname: 'title',
				reqd: 1,
			},
			{
				label: __('Suffix'),
				fieldtype: 'Data',
				fieldname: 'suffix',
			},
			{
				label: __('Parent'),
				fieldtype: 'Select',
				fieldname: 'parent',
				options: this.private_parent_pages,
			},
			{
				label: __('Public'),
				fieldtype: 'Check',
				fieldname: 'is_public',
				depends_on: `eval:${this.has_access}`,
				onchange() {
					d.set_df_property(
						'parent',
						'options',
						this.get_value() ? me.public_parent_pages : me.private_parent_pages
					);
				},
			},
			{
				fieldtype: 'Column Break',
			},
			{
				label: __('Icon'),
				fieldtype: 'Icon',
				fieldname: 'icon',
			},
		],
		primary_action_label: __('Create'),
		primary_action: values => {
			values.title = frappe.utils.escape_html(`${values.title}${values.suffix ? `{{${values.suffix}}}` : ''}`);
			if (!this.validate_page(values)) { return; }
			d.hide();
			this.initialize_editorjs_undo();
			this.setup_customization_buttons({ is_editable: true });

			let name = values.title + (values.is_public ? '' : `-${frappe.session.user}`);
			let blocks = [
				{
					type: 'header',
					data: { text: values.title.replaceAll(/{{([^}]*)}}/g, '') },
				},
			];

			let new_page = {
				content: JSON.stringify(blocks),
				name,
				label: name,
				title: values.title,
				public: values.is_public || 0,
				for_user: values.is_public ? '' : frappe.session.user,
				icon: values.icon,
				parent_page: values.parent || '',
				is_editable: true,
				selected: true,
			};

			this.editor
				.render({
					blocks,
				})
				.then(async () => {
					if (this.editor.configuration.readOnly) {
						this.is_read_only = false;
						await this.editor.readOnly.toggle();
					}

					frappe.call({
						method: 'frappe.desk.doctype.workspace.workspace.new_page',
						args: {
							new_page,
						},
						callback(res) {
							if (res.message) {
								let message = __('Workspace {0} Created Successfully', [
									new_page.title.bold(),
								]);
								frappe.show_alert({
									message,
									indicator: 'green',
								});
							}
						},
					});

					this.update_cached_values(new_page, new_page, true, true);

					let pre_url = new_page.public ? '' : 'private/';
					let route = pre_url + frappe.router.slug(new_page.title);
					frappe.set_route(route);

					this.make_sidebar();
					this.show_sidebar_actions();
					localStorage.setItem("new_workspace", JSON.stringify(new_page));
				});
		},
	});
	d.show();
};
frappe.views.Workspace.prototype.edit_page = function (item) {
	var me = this;
	let old_item = item;
	let parent_pages = this.get_parent_pages(item);
	let idx = parent_pages.findIndex(x => x == item.title);
	if (idx !== -1) { parent_pages.splice(idx, 1); }
	const title = item.title.replaceAll(/{{([^}]+)}}/g, '');
	const res = item.title.match(/{{([^}]+)}}/);
	const suffix = res?.[1] || '';
	const d = new frappe.ui.Dialog({
		title: __('Update Details'),
		fields: [
			{
				label: __('Title'),
				fieldtype: 'Data',
				fieldname: 'title',
				reqd: 1,
				default: title,
			},
			{
				label: __('Suffix'),
				fieldtype: 'Data',
				fieldname: 'suffix',
				default: suffix,
			},
			{
				label: __('Parent'),
				fieldtype: 'Select',
				fieldname: 'parent',
				options: parent_pages,
				default: item.parent_page,
			},
			{
				label: __('Public'),
				fieldtype: 'Check',
				fieldname: 'is_public',
				depends_on: `eval:${this.has_access}`,
				default: item.public,
				onchange() {
					d.set_df_property(
						'parent',
						'options',
						this.get_value() ? me.public_parent_pages : me.private_parent_pages
					);
				},
			},
			{
				fieldtype: 'Column Break',
			},
			{
				label: __('Icon'),
				fieldtype: 'Icon',
				fieldname: 'icon',
				default: item.icon,
			},
		],
		primary_action_label: __('Update'),
		primary_action: values => {
			values.title = frappe.utils.escape_html(`${values.title}${values.suffix ? `{{${values.suffix}}}` : ''}`);
			let is_title_changed = values.title != old_item.title;
			let is_section_changed = values.is_public != old_item.public;
			if (
				(is_title_changed || is_section_changed) &&
				!this.validate_page(values, old_item)
			) { return; }
			d.hide();

			frappe.call({
				method: 'frappe.desk.doctype.workspace.workspace.update_page',
				args: {
					name: old_item.name,
					title: values.title,
					icon: values.icon || '',
					parent: values.parent || '',
					public: values.is_public || 0,
				},
				callback(res) {
					if (res.message) {
						let message = __('Workspace {0} Edited Successfully', [
							old_item.title.bold(),
						]);
						frappe.show_alert({ message, indicator: 'green' });
					}
				},
			});

			this.update_sidebar(old_item, values);

			if (this.make_page_selected) {
				let pre_url = values.is_public ? '' : 'private/';
				let route = pre_url + frappe.router.slug(values.title);
				frappe.set_route(route);

				this.make_page_selected = false;
			}

			this.make_sidebar();
			this.show_sidebar_actions();
		},
	});
	d.show();
};
frappe.views.Workspace.prototype.sidebar_item_container = function (item) {
	return $(`
			<div
				class="sidebar-item-container ${item.is_editable ? 'is-draggable' : ''}"
				item-parent="${item.parent_page}"
				item-name="${item.title}"
				item-public="${item.public || 0}"
				item-is-hidden="${item.is_hidden || 0}"
			>
				<div class="desk-sidebar-item standard-sidebar-item ${item.selected ? 'selected' : ''}">
					<a
						href="/app/${item.public
			? frappe.router.slug(item.title)
			: `private/${frappe.router.slug(item.title)}`
		}"
						class="item-anchor ${item.is_editable ? '' : 'block-click'}" title="${__(item.title)}"
					>
						<span class="sidebar-item-icon" item-icon=${item.icon || 'folder-normal'}>${frappe.utils.icon(
			item.icon || 'folder-normal',
			'md'
		)}</span>
						<span class="sidebar-item-label">${__(item.title.replaceAll(/{{([^}]+)}}/g, ''))}<span>
					</a>
					<div class="sidebar-item-control"></div>
				</div>
				<div class="sidebar-child-item nested-container"></div>
			</div>
		`);
};

frappe.views.Workspace.prototype.duplicate_page = function (page) {
	var me = this;
	let new_page = { ...page };
	if (!this.has_access && new_page.public) {
		new_page.public = 0;
	}
	let parent_pages = this.get_parent_pages({ public: new_page.public });
	const d = new frappe.ui.Dialog({
		title: __('Create Duplicate'),
		fields: [
			{
				label: __('Title'),
				fieldtype: 'Data',
				fieldname: 'title',
				reqd: 1,
			},
			{
				label: __('Suffix'),
				fieldtype: 'Data',
				fieldname: 'suffix',
			},
			{
				label: __('Parent'),
				fieldtype: 'Select',
				fieldname: 'parent',
				options: parent_pages,
				default: new_page.parent_page,
			},
			{
				label: __('Public'),
				fieldtype: 'Check',
				fieldname: 'is_public',
				depends_on: `eval:${this.has_access}`,
				default: new_page.public,
				onchange() {
					d.set_df_property(
						'parent',
						'options',
						this.get_value() ? me.public_parent_pages : me.private_parent_pages
					);
				},
			},
			{
				fieldtype: 'Column Break',
			},
			{
				label: __('Icon'),
				fieldtype: 'Icon',
				fieldname: 'icon',
				default: new_page.icon,
			},
		],
		primary_action_label: __('Duplicate'),
		primary_action: values => {
			values.title = `${values.title}${values.suffix ? `{{${values.suffix}}}` : ''}`;
			if (!this.validate_page(values)) { return; }
			d.hide();
			frappe.call({
				method: 'frappe.desk.doctype.workspace.workspace.duplicate_page',
				args: {
					page_name: page.name,
					new_page: values,
				},
				callback(res) {
					if (res.message) {
						let new_page = res.message;
						let message = __(
							'Duplicate of {0} named as {1} is created successfully',
							[page.title.bold(), new_page.title.bold()]
						);
						frappe.show_alert({ message, indicator: 'green' });
					}
				},
			});

			new_page.title = values.title;
			new_page.public = values.is_public || 0;
			new_page.name = values.title + (new_page.public ? '' : `-${frappe.session.user}`);
			new_page.label = new_page.name;
			new_page.icon = values.icon;
			new_page.parent_page = values.parent || '';
			new_page.for_user = new_page.public ? '' : frappe.session.user;
			new_page.is_editable = !new_page.public;
			new_page.selected = true;

			this.update_cached_values(page, new_page, true);

			let pre_url = values.is_public ? '' : 'private/';
			let route = pre_url + frappe.router.slug(values.title);
			frappe.set_route(route);

			me.make_sidebar();
			me.show_sidebar_actions();
		},
	});
	d.show();
};
