<template>
	<div class="organization" v-loading="loading">
		<div class="btn-container" v-if="permissions.createPermission">
			<ElButton type="primary" @click="joinOrganization">加入组织</ElButton>
		</div>
		<el-table :data="organizationList" :border="true" style="width: 100%" height="100%">
			<el-table-column fixed prop="organization_doc.label" label="组织" width="180" />
			<el-table-column prop="role_list" label="角色" >
				<template #default="scope">
					<span>{{ scope.row.role_list.map(i=>tt(i.role)).join(',') }}</span>
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

			<el-table-column  v-if="permissions.writePermission||permissions.deletePermission"  prop="address" label="操作" width="180" >
				<template #default="scope">
					<ElButton v-if="permissions.writePermission" type="primary" @click="editOrganization(scope.row)">编辑</ElButton>
					<ElButton v-if="permissions.deletePermission" type="danger" @click="outOrganization(scope.row)">退出</ElButton>
				</template>
			</el-table-column>
		</el-table>
	</div>
</template>

<script setup lang='ts'>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { Organization, Permissions } from '../type';
import { ElMessage, ElMessageBox } from 'element-plus';
const tt = __;
interface Props{
	user:string,
	permissions:Permissions
}
const props = defineProps<Props>();
interface Emit{

}
const emit = defineEmits<Emit>();
const organizationList = ref<Organization[]>([]);
const loading = ref<boolean>(false);
watch(()=>props.user, ()=>{
	getOrganizations()
}, {immediate:true})
async function getOrganizations(){
	if(!props.user){
		return;
	}
	loading.value=true;
	const res = await frappe.call<{ message: Organization[] }>({
		method: 'tianjy_organization.tianjy_organization.page.tianjy_organization_members.tianjy_organization_members.get_organizations',
		args:{
			user_name:props.user
		}
	});
	organizationList.value = res?.message||[]
	loading.value=false;
}

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
			}
		).then(async () => {
			loading.value=true;
			await frappe.db.delete_doc('Tianjy Organization Member', organization.name)
			loading.value=false;
			getOrganizations()
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

frappe.socketio.doctype_subscribe('Tianjy Organization Member');
frappe.realtime.on('list_update', p => {
	if (p.doctype !== 'Tianjy Organization Member') { return; }
	getOrganizations();
});

const popstateListener = function (event:any) {
	getOrganizations();
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
