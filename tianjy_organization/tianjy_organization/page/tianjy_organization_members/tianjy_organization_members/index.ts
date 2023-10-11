import { createApp } from 'vue';
import OrganizationMembers from './index.vue';
import ElementPlus from 'element-plus';
import zhCn from 'element-plus/dist/locale/zh-cn';


frappe.pages['tianjy_organization_members'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: '组织人员',
		single_column: true
	});
	const app = createApp(OrganizationMembers, {});
	app.use(app => { app.config.globalProperties.$page = page; });
	app.use(ElementPlus, { size: 'small', locale: zhCn });
	app.mount(page.parent);
}
