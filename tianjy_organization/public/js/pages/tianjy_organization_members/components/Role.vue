<template>
	<div class="role" @click="showPermissions">
		{{ tt(role) }}
	</div>
</template>
<script setup lang='ts'>
import { ElMessage, ElMessageBox } from 'element-plus';
import { reactive, ref, watch, computed } from 'vue';
const tt = __;

interface Props{
	role:string,
}
const props = defineProps<Props>();

function showPermDialog(role:string, permissions:any[]) {
	const perm_dialog = new frappe.ui.Dialog({ title: __(role) });
	perm_dialog.$wrapper.css('z-index', '2083');
	perm_dialog.$wrapper
		.find('.modal-dialog')
		.css('width', '1200px')
		.css('max-width', '80vw');
	perm_dialog.show();
	const $body = $(perm_dialog.body);
	if (!permissions.length) {
		$body.append(`<div class="text-muted text-center padding">
			${__('{0} role does not have permission on any doctype', [role])}
		</div>`);
		return;
	}
	const table = document.createElement('table');
	table.className = 'user-perm';
	const thead = table.appendChild(document.createElement('thead'));
	const tr = thead.appendChild(document.createElement('tr'));
	tr.appendChild(document.createElement('th'))
		.appendChild(document.createTextNode(__('Document Type')));
	tr.appendChild(document.createElement('th'))
		.appendChild(document.createTextNode(__('Level')));
	for (const p of frappe.perm.rights) {
		tr.appendChild(document.createElement('th'))
			.appendChild(document.createTextNode(frappe.unscrub(p)));
	}

	const tbody = table.appendChild(document.createElement('thead'));
	for (const perm of permissions) {
		const tr = tbody.appendChild(document.createElement('tr'));
		tr.appendChild(document.createElement('td'))
			.appendChild(document.createTextNode(perm.parent));
		tr.appendChild(document.createElement('td'))
			.appendChild(document.createTextNode(perm.permlevel));
		for (const p of frappe.perm.rights) {
			const td = tr.appendChild(document.createElement('td'));
			td.className = 'text-muted bold';
			if (perm[p]) {
				td.innerHTML = frappe.utils.icon('check', 'xs');
			} else {
				td.appendChild(document.createTextNode('-'));
			}
		}

	}
	$body.append(table);

}

function showPermissions(){
	if (!props.role){ return; }
	frappe
		.xcall('frappe.core.doctype.user.user.get_perm_info', { role:props.role })
		.then(p => showPermDialog(props.role, p as any[]));
}

</script>
<style scoped lang="less">
.role{
	cursor: pointer;
	&:hover{
		text-decoration: underline;
	}
}
</style>
