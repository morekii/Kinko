<script lang="ts">
    import { onMount } from 'svelte';
    let categories: any[] = []; let name = ''; let loading = false;

    async function loadCats() {
        const res = await fetch('http://127.0.0.1:8000/categories');
        if (res.ok) categories = await res.json();
    }
    onMount(loadCats);

    async function createCat() {
        if (!name.trim()) return;
        loading = true;
        await fetch('http://127.0.0.1:8000/categories', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name.trim(), is_active: true })
        });
        name = ''; loading = false; await loadCats();
    }
</script>

<main class="p-4 max-w-md mx-auto space-y-4">
    <header class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Categorías</h1>
        <button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">← Volver</button>
    </header>

    <form on:submit|preventDefault={createCat} class="flex gap-2"><input type="text" placeholder="Nueva categoría..." bind:value={name} class="flex-1 p-2 border rounded-lg text-xs" required /><button type="submit" disabled={loading} class="bg-indigo-600 text-white px-3 font-bold rounded-lg text-xs">Añadir</button></form>

    <div class="space-y-2">
        {#each categories as cat}
            <a href="/categories/{cat.id}" class="bg-white p-3 rounded-xl border shadow-sm flex justify-between items-center block hover:border-indigo-100"><span class="font-bold text-xs text-slate-800">🏷️ {cat.name}</span><span class="text-[9px] text-indigo-600 font-bold">Ver gastos →</span></a>
        {/each}
    </div>
</main>