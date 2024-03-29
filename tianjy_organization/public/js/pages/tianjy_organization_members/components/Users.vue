
<template>
	<div class="sider-container" >
		<div class="btn-container">
			<ElButton v-if="permissions.createPermission" type="primary" @click="createUser">新建人员</ElButton>
		</div>
		<div class="user-container">
			<div>
				<ElForm class="filter-form" inline :model="filterForm">
					<ElFormItem label="状态" clearable>
						<ElSelect v-model="filterForm.enabled">
							<ElOption key="1" label="激活" :value="1"/>
							<ElOption key="0" label="禁用" :value="0"/>
						</ElSelect>
					</ElFormItem>
					<ElFormItem label="用户：">
						<ElInput v-model="filterForm.full_name"></ElInput>
					</ElFormItem>
					<ElFormItem>
						<ElButton type="primary" @click="applyFilter">应用</ElButton>
						<ElButton @click="clearFilter">清除</ElButton>
					</ElFormItem>
				</ElForm>
			</div>
			<ElTable
				ref="tableRef"
				:data="userList"
				border
				style="width: 100%"
				height="100%"
				highlightCurrentRow
				currentRowKey="name"
				@current-change="handleCurrentChange"
			>
				<ElTableColumn fixed prop="full_name" label="用户" >
				</ElTableColumn>
				<ElTableColumn prop="email" label="邮箱" width="180"></ElTableColumn>
				<ElTableColumn prop="enabled" label="状态" width="60" >
					<template #default="scope">
						<div :class="{activity:scope.row.enabled}">{{ scope.row.enabled?'激活':'禁用' }}</div>
					</template>
				</ElTableColumn>
				<ElTableColumn v-if="permissions.deletePermission" prop="address" label="操作" width="80" >
					<template #default="scope">
						<ElButton type="danger" @click="deleteUser(scope.row)">删除</ElButton>
					</template>
				</ElTableColumn>
			</ElTable>
		</div>
	</div>

</template>

<script setup lang='ts'>
import { ref, onMounted, watch, reactive} from 'vue';
import {
	ElForm,
	ElMessageBox,
	ElMessage,
	ElInput,
	ElButton,
	ElFormItem,
	ElSelect,
	ElOption,
	ElTable,
	ElTableColumn,
} from 'element-plus';

import type { User, Permissions } from '../type';

interface Props{
	modelValue?:User
	permissions: Permissions
	loading:boolean
}
const props = defineProps<Props>();
interface Emit{
	(e:'update:modelValue', organization:any ):void
	(e:'update:loading', organization:any ):void
}
const emit = defineEmits<Emit>();
const userList = ref<User[]>([]);
const tableRef = ref<any>();
const filterForm = reactive({
	enabled:'',
	full_name:'',
});
onMounted(()=>{
	getUsers();
});

async function getUsers(){
	emit('update:loading', true);
	const filters = Object.entries(filterForm).map(([key, value])=>{
		if (value===''){ return; }
		if (key==='enable'){ return [key, '=', value]; }
		return [key, 'like', `%${value}%`];
	}).filter(Boolean) as [string, string, any];
	const res = await frappe.db.get_list<User>('User', {filters, limit:0, fields:['*'], order_by:'full_name asc'});
	userList.value = res||[];
	emit('update:modelValue', userList.value[0]);
	emit('update:loading', false);
}
watch([userList, tableRef.value], ()=>{
	if (!tableRef.value||!userList.value.length){ return; }
	tableRef.value.setCurrentRow(userList.value[0]);
});
function handleCurrentChange(value: User){
	emit('update:modelValue', value);
}

function createUser(){
	const newDoc = frappe.model.make_new_doc_and_get_name('User');
	frappe.set_route(['form', 'User', newDoc]);
}

function deleteUser(user:User){
	ElMessageBox.confirm(
		'您确认删除此人员吗?',
		'请确认',
		{
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		},
	).then(async () => {
		emit('update:loading', true);
		await frappe.db.delete_doc('User', user.name);
		emit('update:loading', false);
		getUsers();
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

function applyFilter(){
	getUsers();
}
function clearFilter(){
	filterForm.enabled = '';
	filterForm.full_name = '';
	getUsers();
}
frappe.socketio.doctype_subscribe('User');
frappe.realtime.on('list_update', p => {
	if (p.doctype !== 'User') { return; }
	getUsers();
});


</script>

<style lang='less' scoped>
.filter-form{
	:deep(.el-form-item--small){
		margin-bottom: 8px;
	}
	:deep(label){
		margin-bottom: 0;
	}
}
.sider-container{
	display: flex;
	flex-direction: column;
	height: 100%;
	padding-top: 8px;
	.btn-container{
		margin-bottom: 8px;
	}
	.user-container{
		display: flex;
		flex-direction: column;
		overflow-y: hidden;
	}
	.activity{
		color:#286840
	}
}
</style>
