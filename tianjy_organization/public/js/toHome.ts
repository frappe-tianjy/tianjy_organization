/** 跳转到 /app/ 目录下时，不再进入 home 工作区 */

frappe.router.make_url = function make_url(params) {
	let path_string = $.map(params, function (a) {
		if ($.isPlainObject(a)) {
			frappe.route_options = a;
			return null;
		}
		return encodeURIComponent(String(a));

	}).join('/');
	// let private_home = frappe.workspaces[`home-${frappe.user.name.toLowerCase()}`];
	// let default_page = private_home
	// 	? 'private/home'
	// 	: frappe.workspaces.home
	// 		? 'home'
	// 		: Object.keys(frappe.workspaces)[0];
	return `/app/${path_string || ''}`;
};
