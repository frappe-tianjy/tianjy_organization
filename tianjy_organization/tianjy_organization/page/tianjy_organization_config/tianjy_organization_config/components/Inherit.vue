<template>
	<div class="inheritable-organization " v-loading="loading">
		<div class="btn-container">
			<ElButton v-if="permissions.createPermission" type="primary" @click="createInherit">继承组织</ElButton>
		</div>
		<el-table :data="inheritList" border style="width: 100%" height="100%">
			<el-table-column prop="inherit_from_organization_doc.label" label="继承自" ></el-table-column>
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

			<el-table-column v-if="permissions.writePermission||permissions.deletePermission" prop="address" label="操作" width="130" >
				<template #default="scope">
					<ElButton v-if="permissions.writePermission" type="primary" @click="editInherit(scope.row)">编辑</ElButton>
					<ElButton v-if="permissions.deletePermission" type="danger" @click="deleteInherit(scope.row)">删除</ElButton>
				</template>
			</el-table-column>
		</el-table>
	</div>
</template>

<script setup lang='ts'>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';

import type { InheritOrganization, Permissions } from '../type';

interface Props{
	organization:string
	permissions:Permissions
}
const props = defineProps<Props>();
const inheritList = ref<InheritOrganization[]>([]);
const loading = ref<boolean>(false);

watch(()=>props.organization, ()=>{
	getInherits();
}, {immediate: true});

async function getInherits(){
	if (!props.organization){
		return;
	}
	loading.value = true;
	const res = await frappe.call<{ message: InheritOrganization[] }>({
		method: 'tianjy_organization.tianjy_organization.page.tianjy_organization_config.tianjy_organization_config.get_inherit',
		args:{
			organization_name:props.organization,
		},
	});
	inheritList.value = res?.message||[];
	loading.value = false;
}

function createInherit(){
	const newDoc = frappe.model.make_new_doc_and_get_name('Tianjy Organization Inheritable');
	frappe.model.set_value('Tianjy Organization Inheritable', newDoc, 'organization', props.organization);
	frappe.set_route(['form', 'Tianjy Organization Inheritable', newDoc]);
}

function editInherit(inheritOrganization:InheritOrganization){
	frappe.set_route(['form', 'Tianjy Organization Inheritable', inheritOrganization.name]);
}
function deleteInherit(inheritOrganization:InheritOrganization){
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
		await frappe.db.delete_doc('Tianjy Organization Inheritable', inheritOrganization.name);
		getInherits();
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

frappe.socketio.doctype_subscribe('Tianjy Organization Inheritable');

frappe.realtime.on('list_update', p => {
	if (p.doctype !== 'Tianjy Organization Inheritable') { return; }
	getInherits();
});

// const popstateListener = function (event:any) {
// 	getInherits();
// };
// onMounted(() => {
// 	window.addEventListener('popstate', popstateListener);
// });
// onUnmounted(() => {
// 	window.removeEventListener('popstate', popstateListener);
// });
</script>

<style lang='less' scoped>
.inheritable-organization{
	height: 100%;
	display: flex;
    flex-direction: column;
	.btn-container{
		text-align: right;
		margin-bottom: 8px;
	}
}

</style>
