<script lang="ts">
	import { Repeat, Users, Tag, FileText, Coins, TrendingUp, ChevronRight } from 'lucide-svelte';
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<header class="mb-8">
		<h1 class="text-3xl font-extrabold text-white tracking-tight">Menú Principal</h1>
		<p class="text-xs text-zinc-500 mt-1 font-medium tracking-wide">Gestión y configuración de Kinko</p>
	</header>

	<div class="mb-6">
		<span class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block mb-2 px-2">Gestión Diaria</span>
		<div class="bg-surface border border-zinc-800 rounded-card overflow-hidden shadow-lg">
			<a href="/subscriptions" class="flex items-center justify-between p-4 border-b border-zinc-800 hover:bg-zinc-800 transition-colors group">
				<div class="flex items-center gap-3">
					<div class="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
						<Repeat size={18} />
					</div>
					<span class="font-bold text-sm text-white group-hover:text-indigo-400 transition-colors">Suscripciones Fijas</span>
				</div>
				<ChevronRight size={16} class="text-zinc-600" />
			</a>

			<a href="/entities" class="flex items-center justify-between p-4 border-b border-zinc-800 hover:bg-zinc-800 transition-colors group">
				<div class="flex items-center gap-3">
					<div class="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
						<Users size={18} />
					</div>
					<span class="font-bold text-sm text-white group-hover:text-emerald-400 transition-colors">Contactos & Deudas</span>
				</div>
				<ChevronRight size={16} class="text-zinc-600" />
			</a>

			<a href="/categories" class="flex items-center justify-between p-4 hover:bg-zinc-800 transition-colors group">
				<div class="flex items-center gap-3">
					<div class="w-8 h-8 rounded-lg bg-orange-500/20 text-orange-400 flex items-center justify-center">
						<Tag size={18} />
					</div>
					<span class="font-bold text-sm text-white group-hover:text-orange-400 transition-colors">Categorías de Gastos</span>
				</div>
				<ChevronRight size={16} class="text-zinc-600" />
			</a>
		</div>
	</div>

	<div class="mb-6">
		<span class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block mb-2 px-2">Auditoría & Sistema</span>
		<div class="bg-surface border border-zinc-800 rounded-card overflow-hidden shadow-lg">
			<a href="/transactions" class="flex items-center justify-between p-4 border-b border-zinc-800 hover:bg-zinc-800 transition-colors group">
				<div class="flex items-center gap-3">
					<div class="w-8 h-8 rounded-lg bg-zinc-700 text-zinc-300 flex items-center justify-center">
						<FileText size={18} />
					</div>
					<span class="font-bold text-sm text-white group-hover:text-zinc-300 transition-colors">Historial Completo</span>
				</div>
				<ChevronRight size={16} class="text-zinc-600" />
			</a>

			<a href="/settings/rates" class="flex items-center justify-between p-4 hover:bg-zinc-800 transition-colors group">
				<div class="flex items-center gap-3">
					<div class="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center">
						<Coins size={18} />
					</div>
					<span class="font-bold text-sm text-white group-hover:text-blue-400 transition-colors">Cotizaciones Manuales</span>
				</div>
				<ChevronRight size={16} class="text-zinc-600" />
			</a>
		</div>
	</div>

	<div>
		<span class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block mb-2 px-2">Próximamente</span>
		<div class="bg-zinc-900/50 border border-dashed border-zinc-700 rounded-card overflow-hidden opacity-70">
			<div class="flex items-center justify-between p-4">
				<div class="flex items-center gap-3">
					<div class="w-8 h-8 rounded-lg bg-zinc-800 text-zinc-500 flex items-center justify-center">
						<TrendingUp size={18} />
					</div>
					<span class="font-bold text-sm text-zinc-400">Portafolio & APIs</span>
				</div>
				<span class="text-[8px] bg-zinc-800 text-zinc-500 px-2 py-1 rounded-md uppercase font-bold tracking-widest">En Desarr.</span>
			</div>
		</div>
	</div>
</main>
