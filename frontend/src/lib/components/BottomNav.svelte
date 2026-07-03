<script lang="ts">
	import { page } from '$app/stores';
	import { Home, Landmark, Plus, Menu } from 'lucide-svelte';
</script>

<nav
	class="fixed bottom-0 w-full bg-surface-alt border-t border-zinc-800 flex justify-between items-center h-[68px] px-2 z-50 pb-safe"
>
	<a
		href="/"
		class="flex flex-col items-center justify-center w-full h-full {$page.url.pathname === '/'
			? 'text-white'
			: 'text-zinc-500'} hover:text-zinc-300 transition-colors"
	>
		<Home size={22} class="mb-0.5" />
		<span class="text-[9px] font-bold tracking-wide">Inicio</span>
	</a>

	<a
		href="/accounts"
		class="flex flex-col items-center justify-center w-full h-full {$page.url.pathname.startsWith(
			'/accounts'
		)
			? 'text-white'
			: 'text-zinc-500'} hover:text-zinc-300 transition-colors"
	>
		<Landmark size={22} class="mb-0.5" />
		<span class="text-[9px] font-bold tracking-wide">Cuentas</span>
	</a>

	<div class="flex flex-col items-center justify-center w-full h-full relative -top-2">
		<a
			href="/new"
			class="bg-accent hover:bg-accent-hover text-white rounded-full w-12 h-12 flex items-center justify-center shadow-lg shadow-blue-900/40 transform transition active:scale-95"
		>
			<Plus size={24} strokeWidth={2.5} />
		</a>
	</div>

	<a
		href="/settings"
		class="flex flex-col items-center justify-center w-full h-full {$page.url.pathname.startsWith(
			'/settings'
		)
			? 'text-white'
			: 'text-zinc-500'} hover:text-zinc-300 transition-colors"
	>
		<Menu size={22} class="mb-0.5" />
		<span class="text-[9px] font-bold tracking-wide">Más</span>
	</a>
</nav>
