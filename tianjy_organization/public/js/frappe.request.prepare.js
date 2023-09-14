// TODO: 等重构的组织获取接口

function getOrganizationName() {
	return frappe.defaults.get_user_default('Tianjy Organization');
}
const old = frappe.request.prepare;
frappe.request.prepare = function (opts) {
	old.call(this, ...arguments);
	const organization = getOrganizationName();
	if (!organization) { return; }
	if (opts.headers) {
		opts.headers['X-Tianjy-Organization'] = organization;
	} else {
		opts.headers = {'X-Tianjy-Organization': organization};
	}
};
