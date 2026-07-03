<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { getCategories, getTransactions, updateCategory, deleteCategory, ApiError } from '$lib/api';
	import type { Category, Transaction } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import Input from '$lib/components/Input.svelte';
	import Button from '$lib/components/Button.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import ConfirmDialog from '$lib/components/ConfirmDialog.svelte';

	const categoryId = parseInt($page.params.id as string);
	let category: Category | null = null;
	let transactions: Transaction[] = [];
	let isEditing = false;
	let editName = '';
	let saving = false;
	let errorMessage = '';
	let confirmDeleteOpen = false;

	async function loadCategoryHub() {
		errorMessage = '';
		try {
			const [cats, tx] = await Promise.all([getCategories(), getTransactions(300)]);
			category = cats.find((c) => c.id === categoryId) ?? null;
			if (category) editName = category.name;
			transactions = tx.filter((t) => t.entries.some((e) => e.category_id === categoryId));
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo cargar la categoría.';
		}
	}
	onMount(loadCategoryHub);

	async function saveChanges() {
		saving = true;
		errorMessage = '';
		try {
			await updateCategory(categoryId, { name: editName });
			isEditing = false;
			await loadCategoryHub();
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
			await deleteCategory(categoryId);
			history.back();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo desactivar la categoría.';
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28 space-y-4">
	<PageHeader title="Detalle de Categoría" />

	{#if errorMessage}
		<div class="p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	{#if category}
		<Card padding="p-5">
			<div class="flex justify-between items-center">
				<span class="text-[10px] text-zinc-500 font-bold uppercase">Nombre</span>
				<button type="button" on:click={() => (isEditing = !isEditing)} class="text-xs text-blue-400 font-semibold">
					{isEditing ? 'Cancelar' : 'Editar'}
				</button>
			</div>
			{#if isEditing}
				<div class="flex gap-2 mt-2">
					<Input bind:value={editName} />
					<Button on:click={saveChanges} disabled={saving} fullWidth={false}>Guardar</Button>
				</div>
			{:else}
				<h2 class="text-lg font-bold text-white mt-2">🏷️ {category.name}</h2>
			{/if}
			<div class="mt-4">
				<Button variant="danger" on:click={() => (confirmDeleteOpen = true)}>Eliminar</Button>
			</div>
		</Card>

		<div class="space-y-2">
			<span class="text-[10px] text-zinc-500 font-bold uppercase block">Operaciones vinculadas</span>
			{#each transactions as tx}
				<Card href="/transactions/{tx.id}" padding="p-3">
					<div class="flex justify-between items-center">
						<span class="font-bold text-xs text-white">{tx.description}</span>
						<span class="font-bold text-xs text-blue-400">${Math.abs(Number(tx.entries[0]?.amount ?? 0)).toLocaleString()}</span>
					</div>
				</Card>
			{:else}
				<EmptyState title="Sin operaciones" subtitle="Todavía no hay gastos en esta categoría." />
			{/each}
		</div>
	{/if}
</main>

<ConfirmDialog
	open={confirmDeleteOpen}
	title="¿Eliminar esta categoría?"
	confirmLabel="Eliminar"
	on:confirm={confirmDelete}
	on:cancel={() => (confirmDeleteOpen = false)}
/>
