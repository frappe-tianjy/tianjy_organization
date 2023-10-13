<template>
	<div class="member" v-loading="loading">
		<el-table :data="memberList" border style="width: 100%" height="100%">
			<el-table-column fixed prop="user_doc.full_name" label="用户" width="180" />
			<el-table-column prop="role" label="角色" >
				<template #default="scope">
					<span class="role" @click="showPermissions(roleDoc.role)" v-for="roleDoc in scope.row.roles">{{ tt(roleDoc.role) }}</span>
				</template>
			</el-table-column>
			<el-table-column prop="visible" label="可见" width="60" >
				<template #default="scope">
					{{ scope.row.visible?'是':'否' }}
				</template>
			</el-table-column>
			<el-table-column prop="viewable" label="可查看" width="60" >
				<template #default="scope">
					{{ scope.row.viewable?'是':'否' }}
				</template>
			</el-table-column>
			<el-table-column prop="addible" label="可添加" width="60" >
				<template #default="scope">
					{{ scope.row.addible?'是':'否' }}
				</template>
			</el-table-column>
			<el-table-column prop="editable" label="可编辑" width="60" >
				<template #default="scope">
					{{ scope.row.editable?'是':'否' }}
				</template>
			</el-table-column>
			<el-table-column prop="deletable" label="可删除" width="60" >
				<template #default="scope">
					{{ scope.row.deletable?'是':'否' }}
				</template>
			</el-table-column>
			<el-table-column prop="manageable" label="可管理" width="60" >
				<template #default="scope">
					{{ scope.row.manageable?'是':'否' }}
				</template>
			</el-table-column>

			<el-table-column v-if="permissions.writePermission||permissions.deletePermission" prop="address" label="操作" width="60" >
				<template #default="scope">
					<ElButton v-if="permissions.writePermission" type="primary" @click="editMember(scope.row)">详情</ElButton>
				</template>
			</el-table-column>
		</el-table>
	</div>
</template>

<script setup lang='ts'>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';

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
			is_inherit:1,
		},
	});
	memberList.value = res?.message||[];
	loading.value = false;
}

function editMember(member:Member){
	frappe.set_route(['form', 'Tianjy Organization Member', member.name]);
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
