frappe.ui.Page.prototype.set_title = function (title, icon = null, strip = true, tab_title = '') {
	if (!title) { title = ''; }
	if (strip) {
		title = strip_html(title).replaceAll(/{{([^}]*)}}/g, '');
	}
	this.title = title;
	frappe.utils.set_title(tab_title || title);
	if (icon) {
		title = `${frappe.utils.icon(icon)} ${title}`;
	}
	let title_wrapper = this.$title_area.find('.title-text');
	title_wrapper.html(title);
	title_wrapper.attr('title', this.title);
};
