import './selector';
import './toHome';
import './frappe.ui.filter_utils.set_fieldtype';
const { prototype } = frappe.views.Workspace;
const old_append_item = prototype.append_item;
/** 实现对非当前组织工作区的隐藏 */
prototype.append_item = function append_item(item, container) {
	old_append_item.call(this, item, container);
	const { organization } = item;
	if (!organization) { return; }
	const def = frappe.defaults.get_default('Tianjy Organization');
	if (!def) { return; }
	if (def === organization) { return; }
	const $item_container = this.sidebar_items[item.public ? 'public' : 'private'][item.title];
	$item_container.hide();
};
