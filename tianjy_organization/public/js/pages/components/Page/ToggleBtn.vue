<template>
	<span class="toggle-btn" title="切换边栏" @click="toggleSider">
		<svg class="icon icon-md sidebar-toggle-placeholder">
			<use href="#icon-menu"></use>
		</svg>
		<span class="sidebar-toggle-icon">
			<svg class="icon icon-md">
				<use
					:href="expand ? '#icon-sidebar-collapse' : '#icon-sidebar-expand'" />
			</svg>
		</span>
	</span>
</template>

<script setup lang='ts'>

interface Props{
	expand:boolean
}
const props = defineProps<Props>();
interface Emit{
	(e: 'update:expand', expand: boolean): void
}
const emit = defineEmits<Emit>();

function toggleSider(){
	emit('update:expand', !props.expand);
}
</script>

<style lang='less' scoped>
.toggle-btn {
	display: flex;
	margin-right: var(--margin-sm);
	cursor: pointer;
	--icon-stroke: var(--gray-500);

	.sidebar-toggle-placeholder {
		transition: all 0.5s ease-in-out;
	}

	.sidebar-toggle-icon {
		transition: all 0.5s ease-in-out;
		display: none;
	}

	&:hover {
		.sidebar-toggle-placeholder {
			display: none;
		}

		.sidebar-toggle-icon {
			display: block;
		}
	}


}
</style>
