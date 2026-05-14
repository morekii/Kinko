<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';

    const entityId = parseInt($page.params.id);
    let entityObj: any = null; 
    let transactions: any[] = [];
    
    let isEditing = false; 
    let editName = ''; 
    let editIsTracker = false;
    let loading = false;

    async function loadEntHub() {
        const [resEnt, resTx] = await Promise.all([
            fetch('http://127.0.0.1:8000/people'),
            fetch('http://127.0.0.1:8000/transactions/?limit=300')
        ]);
        const allEnts = await resEnt.json();
        const allTx = await resTx.json();
        
        entityObj = allEnts.find((e: any) => e.id === entityId);
        if (entityObj) {
            editName = entityObj.name;
            editIsTracker = entityObj.is_debt_tracker;
        }
        transactions = allTx.filter((tx: any) => tx.entries?.some((e: any) => e.person_id === entityId));
    }
    onMount(loadEntHub);

    async function patchEnt() {
        loading = true;
        await fetch(`http://127.0.0.1:8000/people/${entityId}`, {
            method: 'PATCH', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: editName, is_debt_tracker: editIsTracker })
        });
        isEditing = false; loading = false; 
        await loadEntHub();
    }

    async function delEnt() {
        if (!confirm("¿Eliminar este agente externo de forma definitiva?")) return;
        await fetch(`http://127.0.0.1:8000/people/${entityId}`, { method: 'DELETE' });
        history.back();
    }

    function getEntityImpact(tx: any) {
        const entry = tx.entries?.find((e: any) => e.person_id === entityId);
        return entry ? parseFloat(entry.amount) : 0;
    }
</script>

<main class="p-4 max-w-md mx-auto space-y-4">
    <header class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Cuenta Externa</h1>
        <button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">← Volver</button>
    </header>

    {#if entityObj}
        <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm space-y-3">
            <div class="flex justify-between items-center">
                <span class="text-[10px] text-slate-400 font-bold uppercase">Configuración</span>
                <button type="button" on:click={() => isEditing = !isEditing} class="text-xs text-indigo-600 font-semibold">
                    {isEditing ? 'Cancelar' : '✏️ Editar'}
                </button>
            </div>

            {#if isEditing}
                <div class="space-y-2 pt-1">
                    <input type="text" bind:value={editName} class="w-full p-2 border border-slate-200 rounded-lg text-xs font-bold" />
                    <label class="flex items-center gap-2 pt-1 cursor-pointer text-xs text-slate-600 font-medium">
                        <input type="checkbox" bind:checked={editIsTracker} class="rounded text-indigo-600" />
                        <span>Suma a cálculo de Pasivos / Activos</span>
                    </label>
                    <button type="button" on:click={patchEnt} disabled={loading} class="w-full mt-2 bg-emerald-600 text-white font-bold py-2 rounded-lg text-xs">
                        Guardar Cambios
                    </button>
                </div>
            {:else}
                <div>
                    <div class="flex items-center gap-2">
                        <h2 class="text-lg font-bold text-slate-800">🏢 {entityObj.name}</h2>
                        <span class="px-2 py-0.5 rounded text-[8px] font-extrabold {entityObj.is_debt_tracker ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-500'}">
                            {entityObj.is_debt_tracker ? 'CUENTA CORRIENTE' : 'SOLO ETIQUETA'}
                        </span>
                    </div>
                    <span class="text-[9px] text-slate-400 block mt-1">
                        {entityObj.is_debt_tracker ? 'Impacta directamente en tu Patrimonio Global.' : 'Excluido del cálculo de deudas netas.'}
                    </span>
                </div>
            {/if}

            <button type="button" on:click={delEnt} class="w-full mt-2 py-2 bg-red-50 text-red-600 font-bold rounded-xl text-xs hover:bg-red-100 transition-colors">
                Eliminar Entidad
            </button>
        </div>

        <div class="space-y-2 pt-2">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Registro Histórico</span>
            {#each transactions as tx}
                {@const amt = getEntityImpact(tx)}
                <a href="/transactions/{tx.id}" class="p-3 bg-white rounded-xl border border-slate-100 shadow-sm flex justify-between items-center block hover:border-indigo-100 transition-all">
                    <div>
                        <span class="font-bold text-xs text-slate-800 block">{tx.description}</span>
                        <span class="text-[9px] text-slate-400 block">{new Date(tx.date).toLocaleDateString()}</span>
                    </div>
                    <span class="font-extrabold text-xs {amt > 0 ? 'text-emerald-600' : 'text-slate-800'}">
                        ${Math.abs(amt).toLocaleString()}
                    </span>
                </a>
            {:else}
                <p class="text-center text-xs text-slate-400 py-6">No hay movimientos vinculados a esta entidad.</p>
            {/each}
        </div>
    {/if}
</main>