
<template>
	<div class="custom-tree-node">
		<span>{{ node.label }}</span>
		<el-dropdown @command="command" v-if="node.data.permissions.createPermission||node.data.permissions.deletePermission">
			<span class="el-dropdown-link">
				<el-icon class="el-icon--right" @click="e=>e.stopPropagation()">
					<MoreFilled />
				</el-icon>
			</span>
			<template #dropdown>
				<el-dropdown-menu>
					<el-dropdown-item v-if="childTypes.length>0&&node.data.permissions.createPermission" command="add">
						<el-popover :popper-style="{padding:0}" placement="right-start" trigger="hover" :offset="15">
							<template #reference>
								<span>新建子节点</span>
							</template>
							<el-menu class="create-menu" mode="vertical">
								<el-menu-item class="create_type" v-for="type in childTypes" @click="createByType(type)">{{ type.name }}</el-menu-item>
							</el-menu>
						</el-popover>
					</el-dropdown-item>
					<el-dropdown-item 
						command="delete" 
						v-if="node.data.permissions.deletePermission&&!node.data.children?.length"
					><span class="delete">删除</span></el-dropdown-item>
				</el-dropdown-menu>
			</template>
		</el-dropdown>
	</div>
</template>

<script setup lang='ts'>
import { ref, onMounted, computed, toRaw} from 'vue';
import type { Organization, OrganizationType } from '../type';
import type Node from 'element-plus/es/components/tree/src/model/node'
import { MoreFilled } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

interface Props{
	node:Node,
}
const props = defineProps<Props>();
interface Emit{
	(e:'update:modelValue', organization:any ):void
	(e:'reload' ):void
}
const emit = defineEmits<Emit>();

async function deleteOrganization() {
	ElMessageBox.confirm(
			'您确认删除此组织吗?',
			'请确认',
			{
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'warning',
			}
		).then(async () => {
			await frappe.db.delete_doc('Tianjy Organization', props.node.data.name)
			emit('reload')
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

const childTypes = computed(()=>props.node.data.child_type_list)
function command(v: string) {
	switch (v) {
		case 'delete': return deleteOrganization();
	}
}

function createByType(type:OrganizationType){
	const newDoc = frappe.model.make_new_doc_and_get_name('Tianjy Organization');
	frappe.model.set_value('Tianjy Organization', newDoc, 'type', type.name);
	frappe.model.set_value('Tianjy Organization', newDoc, 'parent_organization', props.node.data.name);
	frappe.set_route(['form', 'Tianjy Organization', newDoc]);
}
</script>

<style lang='less' scoped>
:deep(.delete){
	color: #f00;
}
.create_type{
	height: 24px;	
}
.create-menu{
	border-right: 0;
	padding:0;
}
.custom-tree-node{
	display: flex;
    align-items: center;
    justify-content: space-between;
    flex: 1;
	padding-right: 8px;
	.el-dropdown-link {
		cursor: pointer;
		display: flex;
		align-items: center;
		visibility: hidden;
	}
	&:hover{
		.el-dropdown-link{
			visibility: visible;
		}
	}
}

</style>
