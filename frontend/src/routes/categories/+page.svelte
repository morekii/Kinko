<script lang="ts">
	import { onMount } from 'svelte';
	import { getCategories, createCategory, ApiError } from '$lib/api';
	import type { Category } from '$lib/types';
	import PageHeader from '$lib/components/PageHeader.svelte';
	import Card from '$lib/components/Card.svelte';
	import Button from '$lib/components/Button.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';

	let categories: Category[] = [];
	let name = '';
	let creating = false;
	let loading = true;
	let errorMessage = '';

	async function loadCategories() {
		loading = true;
		errorMessage = '';
		try {
			categories = await getCategories();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudieron cargar las categorías.';
		} finally {
			loading = false;
		}
	}
	onMount(loadCategories);

	async function addCategory() {
		if (!name.trim()) return;
		creating = true;
		errorMessage = '';
		try {
			await createCategory({ name: name.trim(), is_active: true });
			name = '';
			await loadCategories();
		} catch (err) {
			errorMessage = err instanceof ApiError ? err.message : 'No se pudo crear la categoría.';
		} finally {
			creating = false;
		}
	}
</script>

<main class="p-4 max-w-md mx-auto pt-6 pb-28">
	<PageHeader title="Categorías" />

	{#if errorMessage}
		<div class="p-3 mb-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-card text-xs font-bold text-center">
			{errorMessage}
		</div>
	{/if}

	<form on:submit|preventDefault={addCategory} class="flex gap-2 mb-6">
		<input
			type="text"
			placeholder="Nueva categoría..."
			bind:value={name}
			class="flex-1 p-3 bg-surface border border-zinc-800 rounded-xl text-sm text-white focus:outline-none placeholder-zinc-700"
			required
		/>
		<Button type="submit" disabled={creating} fullWidth={false}>Añadir</Button>
	</form>

	<div class="space-y-2">
		{#if loading}
			<Skeleton count={4} height="h-12" />
		{:else}
			{#each categories as cat}
				<Card href="/categories/{cat.id}" padding="p-3">
					<div class="flex justify-between items-center">
						<span class="font-bold text-xs text-white">🏷️ {cat.name}</span>
						<span class="text-[9px] text-blue-400 font-bold">Ver gastos →</span>
					</div>
				</Card>
			{:else}
				<EmptyState title="Sin categorías" subtitle="Cargá una categoría para empezar a clasificar tus gastos." />
			{/each}
		{/if}
	</div>
</main>
