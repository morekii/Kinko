<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { getPeople, getTransactions, updatePerson, deletePerson, ApiError } from '$lib/api';
	import type { Person, Transaction } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import Input from '$lib/components/Input.svelte';
	import Button from '$lib/components/Button.svelte';
	import Badge from '$lib/components/Badge.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';

	const entityId = parseInt($page.params.id as string);
	let entity: Person | null = null;
	let transactions: Transaction[] = [];

	let isEditing = false;
	let editName = '';
	let editIsTracker = false;
	let saving = false;
	let errorMessage = '';
	let confirmDeleteOpen = false;

	async function loadEntityHub() {
		errorMessage = '';
		try {
			const [people, tx] = await Promise.all([getPeople(), getTransactions(300)]);
			entity = people.find((p) => p.id === entityId) ?? null;
			if (entity) {
				editName = entity.name;
				editIsTracker = entity.is_debt_tracker;
			}
			transactions = tx.filter((t) => t.entries.some((e) => e.person_id === entityId));
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo cargar la entidad.';
		}
	}
	onMount(loadEntityHub);

	function impactOf(tx: Transaction) {
		return Number(tx.entries.find((e) => e.person_id === entityId)?.amount ?? 0);
	}

	async function saveChanges() {
		saving = true;
		errorMessage = '';
		try {
			await updatePerson(entityId, { name: editName, is_debt_tracker: editIsTracker });
			isEditing = false;
			await loadEntityHub();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudieron guardar los cambios.';
		} finally {
			saving = false;
		}
	}

	async function confirmDelete() {
		confirmDeleteOpen = false;
		errorMessage = '';
		try {
			await deletePerson(entityId);
			history.back();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo eliminar la entidad.';
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28 space-y-4">
	<PageHeader title="Cuenta Externa" />

	{#if errorMessage}
		<div class="p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	{#if entity}
		<Card padding="p-5">
			<div class="flex justify-between items-center">
				<span class="text-[10px] text-zinc-500 font-bold uppercase">Configuración</span>
				<button type="button" on:click={() => (isEditing = !isEditing)} class="text-xs text-blue-400 font-semibold">
					{isEditing ? 'Cancelar' : 'Editar'}
				</button>
			</div>

			{#if isEditing}
				<div class="space-y-2 mt-2">
					<Input bind:value={editName} />
					<label class="flex items-center gap-2 pt-1 cursor-pointer text-xs text-zinc-400 font-medium">
						<input type="checkbox" bind:checked={editIsTracker} class="rounded bg-zinc-900 border-zinc-700 text-blue-500" />
						<span>Suma a cálculo de Pasivos / Activos</span>
					</label>
					<Button on:click={saveChanges} disabled={saving}>Guardar Cambios</Button>
				</div>
			{:else}
				<div class="mt-2">
					<div class="flex items-center gap-2">
						<h2 class="text-lg font-bold text-white">🏢 {entity.name}</h2>
						<Badge color={entity.is_debt_tracker ? 'amber' : 'zinc'}>
							{entity.is_debt_tracker ? 'Cuenta corriente' : 'Solo etiqueta'}
						</Badge>
					</div>
					<span class="text-[9px] text-zinc-500 block mt-1">
						{entity.is_debt_tracker ? 'Impacta directamente en tu Patrimonio Global.' : 'Excluido del cálculo de deudas netas.'}
					</span>
				</div>
			{/if}

			<div class="mt-4">
				<Button variant="danger" on:click={() => (confirmDeleteOpen = true)}>Eliminar Entidad</Button>
			</div>
		</Card>

		<div class="space-y-2">
			<span class="text-[10px] text-zinc-500 font-bold uppercase block">Registro Histórico</span>
			{#each transactions as tx}
				{@const amt = impactOf(tx)}
				<Card href="/transactions/{tx.id}" padding="p-3">
					<div class="flex justify-between items-center">
						<div>
							<span class="font-bold text-xs text-white block">{tx.description}</span>
							<span class="text-[9px] text-zinc-500 block">{new Date(tx.date).toLocaleDateString()}</span>
						</div>
						<span class="font-extrabold text-xs {amt > 0 ? 'text-emerald-400' : 'text-white'}">
							${Math.abs(amt).toLocaleString()}
						</span>
					</div>
				</Card>
			{:else}
				<EmptyState title="Sin movimientos" subtitle="No hay operaciones vinculadas a esta entidad." />
			{/each}
		</div>
	{/if}
</main>

<ConfirmDialog
	open={confirmDeleteOpen}
	title="¿Eliminar esta entidad?"
	message="Se elimina de forma definitiva."
	confirmLabel="Eliminar"
	on:confirm={confirmDelete}
	on:cancel={() => (confirmDeleteOpen = false)}
/>
