<script lang="ts">
	export let label: string;
	export let value: string;
	export let tone: 'neutral' | 'positive' | 'negative' = 'neutral';

	const toneClass: Record<string, string> = {
		neutral: 'text-white',
		positive: 'text-emerald-400',
		negative: 'text-red-400'
	};
</script>

<div class="bg-surface border border-zinc-800 rounded-card p-4 flex-1 min-w-0">
	<p class="text-[10px] text-zinc-500 font-bold uppercase tracking-wider truncate">{label}</p>
	<p class="text-lg font-bold mt-1 truncate {toneClass[tone]}">{value}</p>
</div>
