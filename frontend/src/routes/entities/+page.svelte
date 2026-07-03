<script lang="ts">
	import { onMount } from 'svelte';
	import { Plus } from 'lucide-svelte';
	import { getPeople, createPerson, ApiError } from '$lib/api';
	import type { Person } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import Input from '$lib/components/Input.svelte';
	import Button from '$lib/components/Button.svelte';
	import Badge from '$lib/components/Badge.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';

	let entities: Person[] = [];
	let name = '';
	let isDebtTracker = false;
	let creating = false;
	let loading = true;
	let showAddForm = false;
	let errorMessage = '';

	async function loadEntities() {
		loading = true;
		errorMessage = '';
		try {
			entities = await getPeople();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudieron cargar los contactos.';
		} finally {
			loading = false;
		}
	}
	onMount(loadEntities);

	async function addEntity() {
		if (!name.trim()) return;
		creating = true;
		errorMessage = '';
		try {
			await createPerson({ name: name.trim(), is_debt_tracker: isDebtTracker, is_active: true });
			name = '';
			isDebtTracker = false;
			showAddForm = false;
			await loadEntities();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo crear el contacto.';
		} finally {
			creating = false;
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<PageHeader title="Contactos" />

	{#if errorMessage}
		<div class="p-3 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	{#if !showAddForm}
		<button
			on:click={() => (showAddForm = true)}
			class="w-full bg-surface border border-dashed border-zinc-700 rounded-card p-6 mb-6 flex flex-col items-center justify-center text-zinc-500 hover:text-white hover:bg-zinc-800 transition-all cursor-pointer"
		>
			<Plus size={28} class="mb-2 text-blue-500" />
			<span class="text-sm font-bold tracking-wide">Registrar Contacto</span>
		</button>
	{:else}
		<form on:submit|preventDefault={addEntity} class="bg-surface border border-blue-500/30 p-5 rounded-card shadow-lg shadow-blue-900/10 mb-6 space-y-4">
			<div class="flex justify-between items-center mb-2">
				<span class="text-[10px] font-bold text-blue-400 uppercase tracking-wider">Nuevo Contacto</span>
				<button type="button" on:click={() => (showAddForm = false)} class="text-xs font-bold text-zinc-500 hover:text-white">Cancelar</button>
			</div>

			<Input label="Nombre del Contacto" placeholder="Ej. Empleador, Pedro, McDonald's..." bind:value={name} required />

			<label class="flex items-center gap-2 pt-2 text-xs text-zinc-400 font-medium cursor-pointer border-t border-zinc-800 mt-2">
				<input type="checkbox" bind:checked={isDebtTracker} class="rounded bg-zinc-900 border-zinc-700 text-blue-500" />
				<span>Rastrear Saldo en Activos/Pasivos</span>
			</label>

			<Button type="submit" disabled={creating}>Guardar</Button>
		</form>
	{/if}

	<div class="space-y-3">
		<span class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block mb-2">Directorio Activo</span>
		{#if loading}
			<Skeleton count={3} />
		{:else}
			{#each entities as ent}
				<Card href="/entities/{ent.id}" padding="p-4">
					<div class="flex justify-between items-center">
						<div class="flex items-center gap-4">
							<div class="w-10 h-10 bg-zinc-900 rounded-xl flex items-center justify-center border border-zinc-800">
								<span class="text-xl">🏢</span>
							</div>
							<div>
								<p class="font-bold text-sm text-white">{ent.name}</p>
								{#if ent.is_debt_tracker}<Badge color="amber">Patrimonial</Badge>{/if}
							</div>
						</div>
						<div class="text-right">
							<p class="font-extrabold text-sm {ent.balance > 0 ? 'text-emerald-400' : ent.balance < 0 ? 'text-red-400' : 'text-zinc-500'}">
								${Math.abs(Number(ent.balance)).toLocaleString()}
							</p>
							<span class="text-[9px] text-zinc-500 block uppercase font-medium mt-0.5 tracking-wider">
								{ent.balance > 0 ? 'A cobrar' : ent.balance < 0 ? 'A pagar' : 'Saldado'}
							</span>
						</div>
					</div>
				</Card>
			{:else}
				<EmptyState title="Directorio vacío" subtitle="Cargá contactos para vincular tus gastos." />
			{/each}
		{/if}
	</div>
</main>
