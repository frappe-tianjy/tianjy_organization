import { createApp } from 'vue';

import OrganizationMembers from './tianjy_organization_members/index.vue';
import OrganizationConfig from './tianjy_organization_config/index.vue';

frappe.provide('frappe.pages');
function definePage(name, on_page_load) {
	let page = frappe.pages[name];
	if (page) {
		page.on_page_load = on_page_load;
	}
	Object.defineProperty(frappe.pages, name, {
		set(value) {
			page = value;
			if (page) {
				page.on_page_load = on_page_load;
			}
		},
		get() { return page; },
		configurable: true,
	});
}
definePage('tianjy_organization_config', function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: '组织配置',
		single_column: true,
	});
	const app = createApp(OrganizationConfig);
	app.mount(page.parent);
});
definePage('tianjy_organization_members', function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: '组织人员',
		single_column: true,
	});
	const app = createApp(OrganizationMembers);
	app.mount(page.parent);
});
