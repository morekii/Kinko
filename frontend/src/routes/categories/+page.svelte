
<script lang="ts">
    import { onMount } from 'svelte';

    let categories: any[] = [];
    let name = '';
    let loading = false;
    let message = '';

    async function loadCategories() {
        const res = await fetch('http://127.0.0.1:8000/categories');
        if (res.ok) categories = await res.json();
    }

    onMount(loadCategories);

    async function createCategory() {
        if (!name.trim()) return;
        loading = true;
        try {
            const res = await fetch('http://127.0.0.1:8000/categories', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name.trim(), is_active: true })
            });
            if (res.ok) {
                name = '';
                message = 'Categoría creada.';
                await loadCategories();
            }
        } finally {
            loading = false;
        }
    }

    async function deleteCategory(id: int) {
        if (!confirm("¿Ocultar esta categoría?")) return;
        await fetch(`http://127.0.0.1:8000/categories/${id}`, { method: 'DELETE' });
        await loadCategories();
    }
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen">
    <header class="mb-6 flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Categorías</h1>
        <a href="/" class="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-xl border border-indigo-100">← Volver</a>
    </header>

    <form on:submit|preventDefault={createCategory} class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm mb-6 flex gap-2">
        <input type="text" placeholder="Nueva categoría..." bind:value={name} class="flex-1 p-2 border border-slate-200 rounded-xl text-sm focus:outline-none" required />
        <button type="submit" disabled={loading} class="bg-indigo-600 text-white font-bold px-4 py-2 rounded-xl text-sm hover:bg-indigo-700">Add</button>
    </form>

    <div class="space-y-2">
        <h2 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Disponibles</h2>
        {#each categories as cat}
            <div class="bg-white p-3 rounded-xl border border-slate-100 flex justify-between items-center text-sm">
                <span class="font-medium text-slate-700">{cat.name}</span>
                <button type="button" on:click={() => deleteCategory(cat.id)} class="text-slate-300 hover:text-red-500 font-bold px-2 py-1">✕</button>
            </div>
        {/each}
    </div>
</main>