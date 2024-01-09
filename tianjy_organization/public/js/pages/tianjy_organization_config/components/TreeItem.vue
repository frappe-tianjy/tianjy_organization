
<template>
	<div class="custom-tree-node">
		<span>{{ node.label }}</span>
		<ElDropdown @command="command" v-if="node.data.permissions.createPermission||node.data.permissions.deletePermission">
			<span class="el-dropdown-link">
				<ElIcon class="el-icon--right" @click="e=>e.stopPropagation()">
					<MoreFilled />
				</ElIcon>
			</span>
			<template #dropdown>
				<ElDropdownMenu>
					<template v-if="childTypes.length>0&&node.data.permissions.createPermission">
						<ElDropdownItem
							command="add"
							v-for="type in childTypes"
							@click="createByType(type)"
						>
							新建{{ tt(type.name) }}
						</ElDropdownItem>
					</template>
					<ElDropdownItem
						command="delete"
						v-if="node.data.permissions.deletePermission&&!node.data.children?.length"
					>
						<span class="delete">删除</span>
					</ElDropdownItem>
				</ElDropdownMenu>
			</template>
		</ElDropdown>
	</div>
</template>

<script setup lang='ts'>
import { computed } from 'vue';
import type Node from 'element-plus/es/components/tree/src/model/node';
import { MoreFilled } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox, ElIcon, ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element-plus';

import type { OrganizationType } from '../type';

interface Props{
	node:Node,
}
const props = defineProps<Props>();
interface Emit{
	(e:'update:modelValue', organization:any ):void
	(e:'reload' ):void
}
const tt = __;
const emit = defineEmits<Emit>();

async function deleteOrganization() {
	ElMessageBox.confirm(
		'您确认删除此组织吗?',
		'请确认',
		{
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		},
	).then(async () => {
		await frappe.db.delete_doc('Tianjy Organization', props.node.data.name);
		emit('reload');
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

const childTypes = computed(()=>props.node.data.child_type_list);
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
