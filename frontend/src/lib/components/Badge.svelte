<script lang="ts">
	export let color: 'zinc' | 'emerald' | 'red' | 'amber' | 'blue' = 'zinc';

	const colors: Record<string, string> = {
		zinc: 'bg-zinc-800 text-zinc-400',
		emerald: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
		red: 'bg-red-500/10 text-red-400 border border-red-500/20',
		amber: 'bg-amber-500/10 text-amber-500 border border-amber-500/20',
		blue: 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
	};
</script>

<span
	class="text-[9px] font-extrabold uppercase tracking-wider px-1.5 py-0.5 rounded-md inline-block {colors[
		color
	]}"
>
	<slot />
</span>
