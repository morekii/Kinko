<script lang="ts">
    import { onMount } from 'svelte';

    let transactions: any[] = [];
    let categories: any[] = [];
    let query = '';
    let selectedCategory = '';
    let startDate = '';
    let endDate = '';

    async function loadSearchData() {
        const [resTx, resCat] = await Promise.all([
            fetch('http://127.0.0.1:8000/transactions/?limit=500'),
            fetch('http://127.0.0.1:8000/categories')
        ]);
        if (resTx.ok) transactions = await resTx.json();
        if (resCat.ok) categories = await resCat.json();
    }

    onMount(loadSearchData);

    // Motor de filtrado reactivo
    $: filteredResults = transactions.filter(tx => {
        const matchTxt = tx.description.toLowerCase().includes(query.toLowerCase());
        const matchCat = selectedCategory === '' || tx.entries.some((e: any) => e.category_id === parseInt(selectedCategory));
        
        let matchDt = true;
        if (startDate || endDate) {
            const txTime = new Date(tx.date).getTime();
            const start = startDate ? new Date(startDate).getTime() : 0;
            const end = endDate ? new Date(endDate).getTime() : Infinity;
            matchDt = txTime >= start && txTime <= end;
        }
        return matchTxt && matchCat && matchDt;
    });
</script>

<main class="p-4 max-w-md mx-auto space-y-4">
    <header class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Buscar Gastos</h1>
        <button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">
            ← Volver
        </button>
    </header>

    <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm space-y-3">
        <input type="text" placeholder="Filtrar por concepto..." bind:value={query} class="w-full p-2 bg-slate-50 rounded-xl text-xs focus:outline-none" />
        
        <select bind:value={selectedCategory} class="w-full p-2 bg-slate-50 rounded-xl text-xs text-slate-700 focus:outline-none">
            <option value="">Todas las categorías</option>
            {#each categories as cat}<option value={cat.id}>{cat.name}</option>{/each}
        </select>

        <div class="grid grid-cols-2 gap-2 pt-1">
            <div>
                <span class="text-[9px] font-bold text-slate-400 block mb-0.5 uppercase">Desde</span>
                <input type="date" bind:value={startDate} class="w-full p-1.5 bg-slate-50 rounded-lg text-xs text-slate-600" />
            </div>
            <div>
                <span class="text-[9px] font-bold text-slate-400 block mb-0.5 uppercase">Hasta</span>
                <input type="date" bind:value={endDate} class="w-full p-1.5 bg-slate-50 rounded-lg text-xs text-slate-600" />
            </div>
        </div>
    </div>

    <div class="space-y-2">
        <span class="text-[10px] font-bold text-slate-400 uppercase block">Resultados ({filteredResults.length})</span>
        {#each filteredResults as tx}
            <a href="/transactions/{tx.id}" class="p-3 bg-white rounded-xl border border-slate-100 shadow-sm flex justify-between items-center block hover:border-indigo-100">
                <div>
                    <span class="font-bold text-xs text-slate-800 block">{tx.description}</span>
                    <span class="text-[9px] text-slate-400 block">{new Date(tx.date).toLocaleDateString()}</span>
                </div>
                <span class="font-extrabold text-xs text-indigo-600">
                    ${Math.abs(tx.entries[0]?.amount || 0).toLocaleString()}
                </span>
            </a>
        {/each}
    </div>
</main>