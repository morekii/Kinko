<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';

    const categoryId = parseInt($page.params.id);
    let category: any = null; let transactions: any[] = [];
    let isEditing = false; let editName = ''; let loading = false;

    async function loadCatHub() {
        const [resCat, resTx] = await Promise.all([
            fetch('http://127.0.0.1:8000/categories'),
            fetch('http://127.0.0.1:8000/transactions/?limit=300')
        ]);
        const allCats = await resCat.json();
        const allTx = await resTx.json();
        
        category = allCats.find((c: any) => c.id === categoryId);
        if (category) editName = category.name;
        transactions = allTx.filter((tx: any) => tx.entries.some((e: any) => e.category_id === categoryId));
    }
    onMount(loadCatHub);

    async function patchCat() {
        loading = true;
        await fetch(`http://127.0.0.1:8000/categories/${categoryId}`, {
            method: 'PATCH', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: editName })
        });
        isEditing = false; loading = false; await loadCatHub();
    }

    async function delCat() {
        if (!confirm("¿Eliminar categoría?")) return;
        await fetch(`http://127.0.0.1:8000/categories/${categoryId}`, { method: 'DELETE' });
        history.back();
    }
</script>

<main class="p-4 max-w-md mx-auto space-y-4">
    <header class="flex justify-between items-center"><h1 class="text-xl font-bold text-slate-800">Detalle de Categoría</h1><button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">← Volver</button></header>
    {#if category}
        <div class="bg-white p-5 rounded-2xl border shadow-sm space-y-3">
            <div class="flex justify-between items-center"><span class="text-[10px] text-slate-400 font-bold uppercase">Nombre</span><button type="button" on:click={() => isEditing = !isEditing} class="text-xs text-indigo-600 font-semibold">{isEditing ? 'Cancelar' : '✏️ Editar'}</button></div>
            {#if isEditing}
                <div class="flex gap-2"><input type="text" bind:value={editName} class="flex-1 p-2 border rounded-lg text-xs font-bold" /><button type="button" on:click={patchCat} disabled={loading} class="bg-emerald-600 text-white font-bold px-3 rounded-lg text-xs">Guardar</button></div>
            {:else}<h2 class="text-lg font-bold text-slate-800">🏷️ {category.name}</h2>{/if}
            <button type="button" on:click={delCat} class="w-full py-2 bg-red-50 text-red-600 font-bold rounded-lg text-xs">Eliminar</button>
        </div>
        <div class="space-y-2"><span class="text-[10px] text-slate-400 font-bold uppercase block">Operaciones Internas</span>
            {#each transactions as tx}
                <a href="/transactions/{tx.id}" class="p-3 bg-white rounded-xl border shadow-sm flex justify-between block"><span class="font-bold text-xs text-slate-800">{tx.description}</span><span class="font-bold text-xs text-indigo-600">${Math.abs(tx.entries[0]?.amount || 0).toLocaleString()}</span></a>
            {/each}
        </div>
    {/if}
</main>