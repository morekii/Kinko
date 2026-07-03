<script lang="ts">
	export let label = '';
	export let type: 'text' | 'number' | 'date' = 'text';
	export let value: any = '';
	export let placeholder = '';
	export let required = false;
	export let step: string | undefined = undefined;
	export let min: string | number | undefined = undefined;
	export let max: string | number | undefined = undefined;

	const uid = `input-${Math.random().toString(36).slice(2)}`;
</script>

<div>
	{#if label}
		<label for={uid} class="block text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1">{label}</label>
	{/if}
	{#if type === 'number'}
		<input
			id={uid}
			type="number"
			bind:value
			{placeholder}
			{required}
			{step}
			{min}
			{max}
			class="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-white focus:outline-none placeholder-zinc-700"
		/>
	{:else if type === 'date'}
		<input
			id={uid}
			type="date"
			bind:value
			{placeholder}
			{required}
			class="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-white focus:outline-none placeholder-zinc-700"
		/>
	{:else}
		<input
			id={uid}
			type="text"
			bind:value
			{placeholder}
			{required}
			class="w-full p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-sm text-white focus:outline-none placeholder-zinc-700"
		/>
	{/if}
</div>
