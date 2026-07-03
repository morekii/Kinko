<script lang="ts">
	export let title: string;
	export let subtitle: string | null = null;
</script>

<header class="flex justify-between items-center mb-6 gap-3">
	<div class="min-w-0">
		<h1 class="text-2xl font-extrabold text-white tracking-tight truncate">{title}</h1>
		{#if subtitle}
			<p class="text-xs text-zinc-500 mt-1 font-medium">{subtitle}</p>
		{/if}
	</div>
	<div class="flex items-center gap-2 shrink-0">
		<slot name="actions" />
		<button
			type="button"
			on:click={() => history.back()}
			class="text-xs font-bold text-zinc-400 bg-zinc-900 px-4 py-2 rounded-full hover:text-white transition-colors"
		>
			Volver
		</button>
	</div>
</header>
