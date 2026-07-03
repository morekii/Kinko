<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import {
		getTransaction,
		getAccounts,
		getCategories,
		getPeople,
		updateTransaction,
		deleteTransaction,
		ApiError
	} from '$lib/api';
	import type { Account, Category, Entry, Person, Transaction } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import Input from '$lib/components/Input.svelte';
	import Button from '$lib/components/Button.svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';

	const txId = parseInt($page.params.id as string);

	let tx: Transaction | null = null;
	let accounts: Account[] = [];
	let categories: Category[] = [];
	let people: Person[] = [];
	let loading = true;
	let errorMessage = '';

	let isEditing = false;
	let editDescription = '';
	let editEntries: Entry[] = [];
	let saving = false;
	let confirmDeleteOpen = false;

	async function loadDetail() {
		loading = true;
		try {
			const [txData, accs, cats, ppl] = await Promise.all([
				getTransaction(txId),
				getAccounts(),
				getCategories(),
				getPeople()
			]);
			tx = txData;
			accounts = accs;
			categories = cats;
			people = ppl;
			editDescription = tx.description;
			editEntries = tx.entries.map((e) => ({ ...e, amount: Number(e.amount) }));
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo cargar la transacción.';
		} finally {
			loading = false;
		}
	}
	onMount(loadDetail);

	function resolveEntityName(entry: Entry) {
		const labels: string[] = [];
		if (entry.account_id) labels.push(`💳 ${accounts.find((a) => a.id === entry.account_id)?.name ?? 'Cuenta'}`);
		if (entry.category_id) labels.push(`🏷️ ${categories.find((c) => c.id === entry.category_id)?.name ?? 'Categoría'}`);
		if (entry.person_id) labels.push(`🏢 ${people.find((p) => p.id === entry.person_id)?.name ?? 'Entidad'}`);
		return labels.length > 0 ? labels.join(' | ') : 'Concepto General';
	}

	async function saveChanges() {
		saving = true;
		errorMessage = '';
		try {
			const updatedEntries = editEntries.map((e) => ({
				account_id: e.account_id,
				category_id: e.category_id,
				person_id: e.person_id,
				amount: Number(e.amount),
				base_amount: Number(e.amount)
			}));
			await updateTransaction(txId, { description: editDescription, entries: updatedEntries });
			isEditing = false;
			await loadDetail();
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
			await deleteTransaction(txId);
			history.back();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo eliminar la transacción.';
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28 space-y-4">
	<PageHeader title="Detalle de Operación" />

	{#if errorMessage}
		<div class="p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	{#if tx}
		<Card padding="p-5">
			<div class="flex justify-between items-center">
				<span class="text-[10px] font-bold text-zinc-500 uppercase">Información</span>
				<button type="button" on:click={() => (isEditing = !isEditing)} class="text-xs font-semibold text-blue-400">
					{isEditing ? 'Cancelar' : 'Editar'}
				</button>
			</div>

			{#if isEditing}
				<div class="mt-2">
					<Input label="Descripción" bind:value={editDescription} />
				</div>
			{:else}
				<h2 class="text-lg font-bold text-white mt-2">{tx.description}</h2>
				<span class="text-[10px] text-zinc-500 block">{new Date(tx.date).toLocaleString()}</span>
			{/if}

			<div class="border-t border-zinc-800 pt-3 mt-3 space-y-2">
				<span class="text-[10px] font-bold text-zinc-500 uppercase block">Asientos contables</span>
				{#each editEntries as entry}
					{#if isEditing}
						<div class="p-3 bg-zinc-900 rounded-xl border border-zinc-800 space-y-2">
							<div class="flex justify-between items-center border-b border-zinc-800 pb-2">
								<span class="text-[10px] font-bold text-zinc-500 uppercase">Monto (con signo)</span>
								<input
									type="number"
									step="0.01"
									bind:value={entry.amount}
									class="w-28 p-1 text-right bg-zinc-950 border border-zinc-800 rounded text-white font-bold text-xs"
								/>
							</div>
							<div class="space-y-1.5">
								<select bind:value={entry.account_id} class="w-full text-xs text-white bg-zinc-950 border border-zinc-800 p-1.5 rounded focus:outline-none">
									<option value={null}>Sin Cuenta Bancaria</option>
									{#each accounts as acc}<option value={acc.id}>💳 {acc.entity} - {acc.name}</option>{/each}
								</select>
								<select bind:value={entry.category_id} class="w-full text-xs text-white bg-zinc-950 border border-zinc-800 p-1.5 rounded focus:outline-none">
									<option value={null}>Sin Categoría</option>
									{#each categories as cat}<option value={cat.id}>🏷️ {cat.name}</option>{/each}
								</select>
								<select bind:value={entry.person_id} class="w-full text-xs text-white bg-zinc-950 border border-zinc-800 p-1.5 rounded focus:outline-none">
									<option value={null}>Sin Entidad Asociada</option>
									{#each people as p}<option value={p.id}>🏢 {p.name}</option>{/each}
								</select>
							</div>
						</div>
					{:else}
						<div class="p-2.5 bg-zinc-900 rounded-xl flex justify-between items-center text-xs">
							<span class="font-medium text-zinc-300 pr-2">{resolveEntityName(entry)}</span>
							<span class="font-bold {Number(entry.amount) < 0 ? 'text-white' : 'text-emerald-400'}">
								{Number(entry.amount) < 0 ? '-' : '+'}${Math.abs(Number(entry.amount)).toLocaleString()}
							</span>
						</div>
					{/if}
				{/each}
			</div>

			{#if isEditing}
				<div class="mt-4">
					<Button on:click={saveChanges} disabled={saving}>Confirmar Cambios</Button>
				</div>
			{/if}
		</Card>

		<Button variant="danger" on:click={() => (confirmDeleteOpen = true)}>Deshacer / Borrar Transacción</Button>
	{:else if !loading}
		<p class="text-center text-xs text-zinc-500 py-12">No se encontró la transacción.</p>
	{/if}
</main>

<ConfirmDialog
	open={confirmDeleteOpen}
	title="¿Eliminar esta operación?"
	message="Esta acción borra la transacción y sus asientos de forma permanente."
	confirmLabel="Eliminar"
	on:confirm={confirmDelete}
	on:cancel={() => (confirmDeleteOpen = false)}
/>
