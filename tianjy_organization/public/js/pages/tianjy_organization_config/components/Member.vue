<template>
	<div class="member" v-loading="loading">
		<div class="btn-container">
			<ElButton v-if="permissions.createPermission" type="primary" @click="createMember">新增人员</ElButton>
		</div>
		<ElTable :data="memberList" border style="width: 100%" height="100%">
			<ElTableColumn fixed prop="user_doc.full_name" label="用户" width="180" />
			<ElTableColumn prop="role" label="角色" >
				<template #default="scope">
					<span class="role" @click="showPermissions(roleDoc.role)" v-for="roleDoc in scope.row.roles">{{ tt(roleDoc.role) }}</span>
				</template>
			</ElTableColumn>
			<ElTableColumn prop="visible" label="可见" width="60" >
				<template #default="scope">
					{{ scope.row.visible?'是':'否' }}
				</template>
			</ElTableColumn>
			<ElTableColumn prop="viewable" label="可查看" width="60" >
				<template #default="scope">
					{{ scope.row.viewable?'是':'否' }}
				</template>
			</ElTableColumn>
			<ElTableColumn prop="addible" label="可添加" width="60" >
				<template #default="scope">
					{{ scope.row.addible?'是':'否' }}
				</template>
			</ElTableColumn>
			<ElTableColumn prop="editable" label="可编辑" width="60" >
				<template #default="scope">
					{{ scope.row.editable?'是':'否' }}
				</template>
			</ElTableColumn>
			<ElTableColumn prop="deletable" label="可删除" width="60" >
				<template #default="scope">
					{{ scope.row.deletable?'是':'否' }}
				</template>
			</ElTableColumn>
			<ElTableColumn prop="manageable" label="可管理" width="60" >
				<template #default="scope">
					{{ scope.row.manageable?'是':'否' }}
				</template>
			</ElTableColumn>

			<ElTableColumn v-if="permissions.writePermission||permissions.deletePermission" prop="address" label="操作" width="130" >
				<template #default="scope">
					<ElButton v-if="permissions.writePermission" type="primary" @click="editMember(scope.row)">编辑</ElButton>
					<ElButton v-if="permissions.deletePermission" type="danger" @click="deleteMember(scope.row)">删除</ElButton>
				</template>
			</ElTableColumn>
		</ElTable>
	</div>
</template>

<script setup lang='ts'>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import {
	ElMessageBox, ElMessage, ElButton, ElTable, ElTableColumn, vLoading,
} from 'element-plus';

import type { Member, Permissions } from '../type';

import {showPermissions} from './helper';
interface Props{
	organization:string
	permissions:Permissions
}
const props = defineProps<Props>();
const memberList = ref<Member[]>([]);
const loading = ref<boolean>(false);
const tt = __;

watch(()=>props.organization, ()=>{
	getMembers();
}, {immediate: true});

async function getMembers(){
	if (!props.organization){
		return;
	}
	loading.value = true;
	const res = await frappe.call<{ message: Member[] }>({
		method: 'tianjy_organization.tianjy_organization.page.tianjy_organization_config.tianjy_organization_config.get_members',
		args:{
			organization_name:props.organization,
			is_inherit:0,
		},
	});
	memberList.value = res?.message||[];
	loading.value = false;
}

function createMember(){
	const newDoc = frappe.model.make_new_doc_and_get_name('Tianjy Organization Member');
	frappe.model.set_value('Tianjy Organization Member', newDoc, 'organization', props.organization);
	frappe.set_route(['form', 'Tianjy Organization Member', newDoc]);
}

function editMember(member:Member){
	frappe.set_route(['form', 'Tianjy Organization Member', member.name]);
}
function deleteMember(member:Member){
	ElMessageBox.confirm(
		'您确认删除此人员吗?',
		'请确认',
		{
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		},
	).then(async () => {
		loading.value = true;
		await frappe.db.delete_doc('Tianjy Organization Member', member.name);
		getMembers();
		ElMessage({
			type: 'success',
			message: '删除成功',
		});
	}).catch(() => {
		ElMessage({
			type: 'info',
			message: '取消删除',
		});
	});
}

frappe.socketio.doctype_subscribe('Tianjy Organization Member');

frappe.realtime.on('list_update', p => {
	if (p.doctype !== 'Tianjy Organization Member'&&p.doctype !== 'Tianjy Organization Role') { return; }
	getMembers();
});

const popstateListener = function (event:any) {
	getMembers();
};
onMounted(() => {
	window.addEventListener('popstate', popstateListener);
});
onUnmounted(() => {
	window.removeEventListener('popstate', popstateListener);
});
</script>

<style lang='less' scoped>
.member{
	height: 100%;
	display: flex;
    flex-direction: column;
	.btn-container{
		text-align: right;
		margin-bottom: 8px;
	}
	.role{
		cursor: pointer;
		margin-right: 4px;
		&:hover{
			text-decoration: underline;
		}
	}
}

</style>
