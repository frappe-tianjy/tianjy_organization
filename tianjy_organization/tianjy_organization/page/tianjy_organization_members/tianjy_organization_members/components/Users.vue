
<template>
	<div class="sider-container" >
		<div class="btn-container">
			<el-button v-if="permissions.createPermission" type="primary" @click="createUser">新建人员</el-button>
		</div>
		<div class="user-container">
			<el-table 
				ref="tableRef"
				:data="userList" 
				:border="true" 
				style="width: 100%" 
				height="100%"
				highlight-current-row
				current-row-key="name"
				@current-change="handleCurrentChange"
			>
				<el-table-column fixed prop="full_name" label="用户" />
				<el-table-column prop="email" label="邮箱"  width="180"></el-table-column>
				<el-table-column prop="enabled" label="状态" width="60" >
					<template #default="scope">
						<div :class="{activity:scope.row.enabled}">{{ scope.row.enabled?'激活':'禁用' }}</div>
					</template>
				</el-table-column>
				<el-table-column v-if="permissions.deletePermission" prop="address" label="操作" width="80" >
					<template #default="scope">
						<ElButton type="danger" @click="deleteUser(scope.row)">删除</ElButton>
					</template>
				</el-table-column>
			</el-table>
		</div>
	</div>

</template>

<script setup lang='ts'>
import { ref, onMounted, computed, toRaw, watch} from 'vue';
import type { User, Permissions } from '../type';
import { ElMessageBox, ElMessage } from 'element-plus';

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
const tableRef = ref<any>()
onMounted(()=>{
	getUsers();
})
async function getUsers(){
	emit('update:loading', true)
	const res = await frappe.db.get_list('User',{limit:'', fields:['*']})
	userList.value = res||[]
	emit('update:modelValue', userList.value[0])
	emit('update:loading', false)
}
watch([userList, tableRef.value], ()=>{
	if(!tableRef.value||!userList.value.length){return}
	tableRef.value.setCurrentRow(userList.value[0])
})
function handleCurrentChange(value: User){
	emit('update:modelValue', value)
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
			}
		).then(async () => {
			emit('update:loading', true)
			await frappe.db.delete_doc('User', user.name)
			emit('update:loading', false)
			getUsers()
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

frappe.socketio.doctype_subscribe('User');
frappe.realtime.on('list_update', p => {
	if (p.doctype !== 'User') { return; }
	getUsers();
});


</script>

<style lang='less' scoped>
.sider-container{
	display: flex;
	flex-direction: column;
	height: 100%;
	padding-top: 8px;
	.btn-container{
		margin-bottom: 8px;
	}
	.user-container{
		overflow-y: auto;
	}
	.activity{
		color:#286840
	}
}
</style>
