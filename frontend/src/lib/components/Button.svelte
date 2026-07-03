<script lang="ts">
	export let variant: 'primary' | 'secondary' | 'danger' | 'ghost' = 'primary';
	export let type: 'button' | 'submit' = 'button';
	export let disabled = false;
	export let fullWidth = true;

	const variants: Record<string, string> = {
		primary: 'bg-accent hover:bg-accent-hover text-white shadow-lg',
		secondary: 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800',
		danger: 'bg-red-500/10 text-red-500 hover:bg-red-500/20',
		ghost: 'bg-transparent text-zinc-500 hover:text-white'
	};
</script>

<button
	{type}
	{disabled}
	on:click
	class="{fullWidth
		? 'w-full'
		: ''} font-bold rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed px-4 py-3 text-sm {variants[
		variant
	]}"
>
	<slot />
</button>
