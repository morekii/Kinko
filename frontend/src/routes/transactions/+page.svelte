<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';

    let tx: any = null;
    let accounts: any[] = [];
    let categories: any[] = [];
    let entities: any[] = [];
    
    let isEditing = false;
    let editDescription = '';
    let editEntries: any[] = [];
    let loading = false;
    const txId = $page.params.id;

    async function loadDetail() {
        const [resTx, resAcc, resCat, resEnt] = await Promise.all([
            fetch('http://127.0.0.1:8000/transactions/'),
            fetch('http://127.0.0.1:8000/accounts'),
            fetch('http://127.0.0.1:8000/categories'),
            fetch('http://127.0.0.1:8000/people')
        ]);
        const allTx = await resTx.json();
        accounts = await resAcc.json();
        categories = await resCat.json();
        entities = await resEnt.json();
        
        tx = allTx.find((t: any) => t.id == txId);
        if (tx) {
            editDescription = tx.description;
            editEntries = tx.entries.map((e: any) => ({ ...e, amount: Math.abs(e.amount) }));
        }
    }

    onMount(loadDetail);

    function resolveEntityName(entry: any) {
        if (entry.account_id) {
            const acc = accounts.find(a => a.id === entry.account_id);
            return acc ? `💳 ${acc.entity} - ${acc.name}` : `Cuenta ID: ${entry.account_id}`;
        }
        if (entry.category_id) {
            const cat = categories.find(c => c.id === entry.category_id);
            return cat ? `🏷️ ${cat.name}` : `Categoría ID: ${entry.category_id}`;
        }
        if (entry.person_id) {
            const ent = entities.find(e => e.id === entry.person_id);
            return ent ? `🏢 ${ent.name}` : `Entidad ID: ${entry.person_id}`;
        }
        return 'Concepto General';
    }

    async function saveTxChanges() {
        loading = true;
        const updatedEntries = editEntries.map((e, index) => {
            const val = parseFloat(e.amount);
            const signedVal = index === 0 ? -val : val;
            return { ...e, amount: signedVal, base_amount: signedVal };
        });

        await fetch(`http://127.0.0.1:8000/transactions/${txId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: editDescription, entries: updatedEntries })
        });
        isEditing = false; loading = false;
        await loadDetail();
    }

    async function deleteTx() {
        if (!confirm("¿Eliminar operación de forma completa?")) return;
        await fetch(`http://127.0.0.1:8000/transactions/${txId}`, { method: 'DELETE' });
        history.back();
    }
</script>

<main class="p-4 max-w-md mx-auto space-y-4">
    <header class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Detalle Contable</h1>
        <button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">
            ← Volver
        </button>
    </header>

    {#if tx}
        <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm space-y-4">
            <div class="flex justify-between items-center">
                <span class="text-[10px] font-bold text-slate-400 uppercase">Información</span>
                <button type="button" on:click={() => isEditing = !isEditing} class="text-xs font-semibold text-indigo-600">
                    {isEditing ? 'Cancelar' : '✏️ Editar'}
                </button>
            </div>

            {#if isEditing}
                <input type="text" bind:value={editDescription} class="w-full p-2 border border-slate-200 rounded-lg text-sm font-bold" />
            {:else}
                <h2 class="text-lg font-bold text-slate-800">{tx.description}</h2>
                <span class="text-[10px] text-slate-400 block">{new Date(tx.date).toLocaleString()}</span>
            {/if}

            <div class="border-t border-slate-100 pt-3 space-y-2">
                <span class="text-[10px] font-bold text-slate-400 uppercase block">Asientos de la Partida Doble</span>
                {#each editEntries as entry, i}
                    <div class="p-2.5 bg-slate-50 rounded-xl flex justify-between items-center text-xs">
                        <span class="font-medium text-slate-700">{resolveEntityName(entry)}</span>
                        {#if isEditing}
                            <input type="number" step="0.01" bind:value={entry.amount} class="w-24 p-1 text-right border border-slate-200 rounded font-bold" />
                        {:else}
                            <span class="font-bold {i === 0 ? 'text-red-600' : 'text-emerald-600'}">
                                ${parseFloat(entry.amount).toLocaleString()}
                            </span>
                        {/if}
                    </div>
                {/each}
            </div>

            {#if isEditing}
                <button type="button" on:click={saveTxChanges} disabled={loading} class="w-full py-2.5 bg-emerald-600 text-white font-bold rounded-xl text-xs">
                    Confirmar Cambios
                </button>
            {/if}
        </div>
        <button type="button" on:click={deleteTx} class="w-full py-3 bg-red-50 text-red-600 font-bold rounded-xl text-xs hover:bg-red-100 transition-colors">
            Deshacer / Borrar Transacción
        </button>
    {/if}
</main>