<script lang="ts">
	export let title: string;
	export let subtitle = '';
</script>

<div class="py-8 text-center bg-zinc-900/50 rounded-card border border-zinc-800">
	<p class="text-sm font-bold text-zinc-400">{title}</p>
	{#if subtitle}
		<p class="text-[10px] text-zinc-600 mt-1">{subtitle}</p>
	{/if}
</div>
