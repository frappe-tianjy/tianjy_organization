<template>
	<div class="organization" v-loading="loading">
		<div class="btn-container" v-if="permissions.createPermission">
			<ElButton type="primary" @click="joinOrganization">加入组织</ElButton>
		</div>
		<el-table :data="organizationList" border style="width: 100%" height="100%">
			<el-table-column prop="organization_doc.label" label="组织" />
			<el-table-column prop="default" label="默认组织" >
				<template #default="scope">
					<div>{{ scope.row.default===1?'是':'' }}</div>
				</template>
			</el-table-column>
			<el-table-column align="center" v-if="permissions.writePermission||permissions.deletePermission" prop="address" label="操作" width="340">
				<template #default="scope">
					<ElButton v-if="permissions.writePermission&&scope.row.type_doc?.no_default!==1" type="primary" @click="toggleDefault(scope.row)">{{ scope.row.default===1?'取消默认':'设为默认' }}</ElButton>
					<ElButton v-if="permissions.writePermission" type="primary" @click="editOrganization(scope.row)">编辑</ElButton>
					<ElButton type="primary" @click="viewPermissions(scope.row)">权限</ElButton>
					<ElButton type="primary" @click="viewRoles(scope.row)">角色</ElButton>
					<ElButton v-if="permissions.deletePermission&&type==='organization'" type="danger" @click="outOrganization(scope.row)">退出</ElButton>
				</template>
			</el-table-column>
		</el-table>
		<RolesDialog
			:visible="visible"
			:user="user"
			:organization="viewOrganization"
			@cancel="visible=false"
		></RolesDialog>
		<PermissionsDialog
			:visible="permissionVisible"
			:user="user"
			:organization="viewOrganization"
			@cancel="permissionVisible=false"
		></PermissionsDialog>
	</div>
</template>

<script setup lang='ts'>
import { onMounted, onUnmounted, ref, watch, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

import type { Organization, Permissions } from '../type';

import RolesDialog from './RolesDialog.vue';
import PermissionsDialog from './PermissionsDialog.vue';

const tt = __;
interface Props{
	user: string,
	permissions: Permissions
	type: 'organization'|'inherit'
	allOrganizationList:Organization[]
}
const props = defineProps<Props>();
interface Emit{
	(e:'refresh' ):void
}
const emit = defineEmits<Emit>();
const loading = ref<boolean>(false);
const visible=ref<boolean>(false);
const permissionVisible = ref<boolean>(false);
const viewOrganization=ref<string>('');
const organizationList = computed(()=>props.allOrganizationList?.filter(item=>{
	const is_inherit = props.type === 'organization'?'0':'1';
	return item.is_inherit===is_inherit;
})||[]);

function joinOrganization(){
	const newDoc = frappe.model.make_new_doc_and_get_name('Tianjy Organization Member');
	frappe.model.set_value('Tianjy Organization Member', newDoc, 'user', props.user);
	frappe.set_route(['form', 'Tianjy Organization Member', newDoc]);

}
function editOrganization(organization:Organization){
	frappe.set_route(['form', 'Tianjy Organization Member', organization.name]);
}
function outOrganization(organization:Organization){
	ElMessageBox.confirm(
		'您确认退出此组织吗?',
		'请确认',
		{
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		},
	).then(async () => {
		loading.value=true;
		await frappe.db.delete_doc('Tianjy Organization Member', organization.name);
		loading.value=false;
		emit('refresh');
		ElMessage({
			type: 'success',
			message: '退出成功',
		});
	}).catch(() => {
		ElMessage({
			type: 'info',
			message: '取消退出',
		});
	});
}

function viewRoles(organization:Organization){
	visible.value = true;
	viewOrganization.value = organization.organization;
}
function viewPermissions(organization:Organization){
	permissionVisible.value = true;
	viewOrganization.value = organization.organization;
}

async function toggleDefault(organization:Organization){
	await frappe.call({
		method: 'tianjy_organization.tianjy_organization.page.tianjy_organization_members.tianjy_organization_members.toggle_default',
		args:{
			member_name:organization.name,
		},
	});
	emit('refresh');
}
frappe.socketio.doctype_subscribe('Tianjy Organization Member');
frappe.realtime.on('list_update', p => {
	if (p.doctype !== 'Tianjy Organization Member') { return; }
	emit('refresh');
});

const popstateListener = function (event:any) {
	emit('refresh');
};
onMounted(() => {
	window.addEventListener('popstate', popstateListener);
});
onUnmounted(() => {
	window.removeEventListener('popstate', popstateListener);
});
</script>

<style lang='less' scoped>

.organization{
	height: 100%;
	display: flex;
    flex-direction: column;
	.btn-container{
		text-align: right;
		margin-bottom: 8px;
	}
}
</style>
