<script lang="ts">
	export let label = '';
	export let value: any = null;
	export let required = false;

	const uid = `select-${Math.random().toString(36).slice(2)}`;
</script>

<div>
	{#if label}
		<label for={uid} class="block text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1">{label}</label>
	{/if}
	<select
		id={uid}
		bind:value
		{required}
		class="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-white focus:outline-none appearance-none"
	>
		<slot />
	</select>
</div>
