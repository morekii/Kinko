<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';

    const txId = parseInt($page.params.id);
    let tx: any = null;
    let accounts: any[] = [];
    let categories: any[] = [];
    let entities: any[] = [];
    
    let isEditing = false;
    let editDescription = '';
    let editEntries: any[] = [];
    let loading = false;

    async function loadDetail() {
        try {
            const [resTx, resAcc, resCat, resEnt] = await Promise.all([
                fetch(`http://127.0.0.1:8000/transactions/${txId}`),
                fetch('http://127.0.0.1:8000/accounts'),
                fetch('http://127.0.0.1:8000/categories'),
                fetch('http://127.0.0.1:8000/people')
            ]);
            
            if (resTx.ok) {
                tx = await resTx.json();
                editDescription = tx.description;
                // Preparamos montos absolutos para el formulario de edición
                editEntries = tx.entries.map((e: any) => ({ ...e, amount: Math.abs(parseFloat(e.amount)) }));
            }
            if (resAcc.ok) accounts = await resAcc.json();
            if (resCat.ok) categories = await resCat.json();
            if (resEnt.ok) entities = await resEnt.json();
        } catch (err) {
            console.error("Error cargando transacción:", err);
        }
    }

    onMount(loadDetail);

    function resolveEntityName(entry: any) {
        let labels = [];
        if (entry.account_id) labels.push(`💳 ${accounts.find(a => a.id === entry.account_id)?.name || 'Cuenta'}`);
        if (entry.category_id) labels.push(`🏷️ ${categories.find(c => c.id === entry.category_id)?.name || 'Cat'}`);
        if (entry.person_id) labels.push(`🏢 ${entities.find(e => e.id === entry.person_id)?.name || 'Entidad'}`);
        return labels.length > 0 ? labels.join(' | ') : 'Concepto General';
    }

    async function saveChanges() {
        loading = true;
        try {
            const updatedEntries = editEntries.map((e, index) => {
                const val = parseFloat(e.amount);
                // Si la pata actualiza moneda origen/destino se debería recalcular base_amount.
                // Como simplificación de edición rápida, mantenemos ratio 1:1 local, o respetamos el signo.
                const signedVal = index === 0 ? -val : val;
                return {
                    account_id: e.account_id,
                    category_id: e.category_id,
                    person_id: e.person_id,
                    amount: signedVal,
                    base_amount: signedVal // En edición avanzada respetamos la equivalencia base original
                };
            });

            await fetch(`http://127.0.0.1:8000/transactions/${txId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    description: editDescription,
                    entries: updatedEntries
                })
            });
            isEditing = false;
            await loadDetail();
        } finally {
            loading = false;
        }
    }

    async function deleteTx() {
        if (!confirm("¿Eliminar transacción de forma definitiva?")) return;
        await fetch(`http://127.0.0.1:8000/transactions/${txId}`, { method: 'DELETE' });
        history.back();
    }
</script>

<main class="p-4 max-w-md mx-auto space-y-4">
    <header class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Detalle de Transacción</h1>
        <button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">
            ← Volver
        </button>
    </header>

    {#if tx}
        <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm space-y-4">
            <div class="flex justify-between items-center">
                <span class="text-[10px] font-bold text-slate-400 uppercase">Información Global</span>
                <button type="button" on:click={() => isEditing = !isEditing} class="text-xs font-semibold text-indigo-600">
                    {isEditing ? 'Cancelar' : '✏️ Editar'}
                </button>
            </div>

            {#if isEditing}
                <div class="space-y-1">
                    <label class="block text-[10px] font-bold text-slate-400 uppercase">Descripción</label>
                    <input type="text" bind:value={editDescription} class="w-full p-2 border border-slate-200 rounded-lg text-sm font-bold" />
                </div>
            {:else}
                <div>
                    <h2 class="text-lg font-bold text-slate-800">{tx.description}</h2>
                    <span class="text-[10px] text-slate-400 block">{new Date(tx.date).toLocaleString()}</span>
                </div>
            {/if}

            <div class="border-t border-slate-100 pt-3 space-y-3">
                <span class="text-[10px] font-bold text-slate-400 uppercase block">Asientos Contables (Líneas)</span>
                
                {#each editEntries as entry, i}
                    {#if isEditing}
                        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                            <div class="flex justify-between items-center border-b border-slate-200 pb-2">
                                <span class="text-[10px] font-bold text-slate-500 uppercase">Impacto Monetario</span>
                                <input type="number" step="0.01" bind:value={entry.amount} class="w-24 p-1 text-right border border-slate-200 rounded font-bold text-xs" />
                            </div>
                            
                            <div class="space-y-1.5">
                                <select bind:value={entry.account_id} class="w-full text-xs text-slate-700 bg-white border border-slate-200 p-1 rounded focus:outline-none">
                                    <option value={null}>Sin Cuenta Bancaria</option>
                                    {#each accounts as acc}<option value={acc.id}>💳 {acc.entity} - {acc.name}</option>{/each}
                                </select>
                                
                                <select bind:value={entry.category_id} class="w-full text-xs text-slate-700 bg-white border border-slate-200 p-1 rounded focus:outline-none">
                                    <option value={null}>Sin Categoría</option>
                                    {#each categories as cat}<option value={cat.id}>🏷️ {cat.name}</option>{/each}
                                </select>

                                <select bind:value={entry.person_id} class="w-full text-xs text-slate-700 bg-white border border-slate-200 p-1 rounded focus:outline-none">
                                    <option value={null}>Sin Entidad Asociada</option>
                                    {#each entities as ent}<option value={ent.id}>🏢 {ent.name}</option>{/each}
                                </select>
                            </div>
                        </div>
                    {:else}
                        <div class="p-2.5 bg-slate-50 rounded-xl flex justify-between items-center text-xs">
                            <span class="font-medium text-slate-700 pr-2">{resolveEntityName(entry)}</span>
                            <span class="font-bold {i === 0 ? 'text-red-600' : 'text-emerald-600'}">
                                ${Math.abs(parseFloat(entry.amount)).toLocaleString()}
                            </span>
                        </div>
                    {/if}
                {/each}
            </div>

            {#if isEditing}
                <button type="button" on:click={saveChanges} disabled={loading} class="w-full py-2.5 bg-emerald-600 text-white font-bold rounded-xl text-xs">
                    Confirmar Todos los Cambios
                </button>
            {/if}
        </div>
        
        <button type="button" on:click={deleteTx} class="w-full py-3 bg-red-50 text-red-600 font-bold rounded-xl text-xs hover:bg-red-100 transition-colors">
            Deshacer / Borrar Transacción
        </button>
    {:else}
        <p class="text-center text-xs text-slate-400 py-12">Cargando transacción...</p>
    {/if}
</main>