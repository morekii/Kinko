<script lang="ts">
    import { page } from '$app/stores';
    import { onMount } from 'svelte';

    const accountId = parseInt($page.params.id);
    let account: any = null;
    let transactions: any[] = [];
    
    let isEditing = false;
    let editName = ''; 
    let editEntity = ''; 
    let editType = ''; 
    let editCurrency = '';
    let editIsDayToDay = true; 
    let loading = false;

    async function loadHub() {
        try {
            const [resAcc, resTx] = await Promise.all([
                fetch('http://127.0.0.1:8000/accounts'),
                fetch('http://127.0.0.1:8000/transactions/?limit=300')
            ]);
            const allAccs = await resAcc.json();
            const allTx = await resTx.json();
            
            account = allAccs.find((a: any) => a.id === accountId);
            if (account) {
                editName = account.name; 
                editEntity = account.entity; 
                editType = account.type;
                editCurrency = account.currency; 
                editIsDayToDay = account.is_day_to_day;
            }
            
            // Filtramos las transacciones donde participe esta cuenta
            transactions = allTx.filter((tx: any) => 
                tx.entries?.some((e: any) => e.account_id === accountId)
            );
        } catch (err) {
            console.error("Error cargando detalle de cuenta:", err);
        }
    }

    onMount(loadHub);

    async function patchAcc() {
        loading = true;
        try {
            await fetch(`http://127.0.0.1:8000/accounts/${accountId}`, {
                method: 'PATCH', 
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    name: editName, 
                    entity: editEntity, 
                    type: editType, 
                    currency: editCurrency, 
                    is_day_to_day: editIsDayToDay 
                })
            });
            isEditing = false; 
            await loadHub();
        } finally {
            loading = false;
        }
    }

    async function delAcc() {
        if (!confirm("¿Eliminar esta cuenta de forma definitiva?")) return;
        await fetch(`http://127.0.0.1:8000/accounts/${accountId}`, { method: 'DELETE' });
        history.back();
    }

    // Función auxiliar limpia para obtener el monto específico de esta cuenta en JS puro
    function getAccountImpact(tx: any) {
        const entry = tx.entries?.find((e: any) => e.account_id === accountId);
        return entry ? parseFloat(entry.amount) : 0;
    }
</script>

<main class="p-4 max-w-md mx-auto space-y-4">
    <header class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Detalle de Cuenta</h1>
        <button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">
            ← Volver
        </button>
    </header>

    {#if account}
        <div class="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm space-y-3">
            <div class="flex justify-between items-center">
                <span class="text-[10px] font-bold text-slate-400 uppercase">Propiedades</span>
                <button type="button" on:click={() => isEditing = !isEditing} class="text-xs text-indigo-600 font-semibold">
                    {isEditing ? 'Cancelar' : '✏️ Editar'}
                </button>
            </div>

            {#if isEditing}
                <div class="space-y-2 pt-1">
                    <input type="text" placeholder="Nombre de cuenta" bind:value={editName} class="w-full p-2 border border-slate-200 rounded-lg text-xs font-bold" />
                    <input type="text" placeholder="Entidad bancaria" bind:value={editEntity} class="w-full p-2 border border-slate-200 rounded-lg text-xs font-bold" />
                    
                    <div class="grid grid-cols-2 gap-2">
                        <select bind:value={editType} class="p-2 border border-slate-200 rounded-lg text-xs bg-white">
                            <option value="savings">Ahorro</option>
                            <option value="checking">Corriente</option>
                            <option value="credit_card">Crédito</option>
                            <option value="cash">Efectivo</option>
                            <option value="virtual">Virtual</option>
                        </select>
                        <select bind:value={editCurrency} class="p-2 border border-slate-200 rounded-lg text-xs bg-white">
                            <option value="ARS">ARS</option>
                            <option value="USD">USD</option>
                            <option value="USDT">USDT</option>
                            <option value="BTC">BTC</option>
                        </select>
                    </div>

                    <label class="flex items-center gap-2 pt-1 text-xs text-slate-600 font-medium cursor-pointer">
                        <input type="checkbox" bind:checked={editIsDayToDay} class="rounded text-indigo-600" />
                        <span>Suma a liquidez Día a Día</span>
                    </label>

                    <button type="button" on:click={patchAcc} disabled={loading} class="w-full mt-2 bg-emerald-600 text-white font-bold py-2 rounded-lg text-xs">
                        Guardar Cambios
                    </button>
                </div>
            {:else}
                <div>
                    <h2 class="text-lg font-bold text-slate-800">💳 {account.entity} - {account.name}</h2>
                    <span class="text-[10px] font-semibold text-slate-400 block uppercase">{account.type} • {account.currency}</span>
                </div>
            {/if}

            <button type="button" on:click={delAcc} class="w-full mt-2 py-2 bg-red-50 text-red-600 font-bold rounded-xl text-xs hover:bg-red-100 transition-colors">
                Eliminar Cuenta
            </button>
        </div>

        <div class="space-y-2 pt-2">
            <span class="text-[10px] font-bold text-slate-400 uppercase block">Movimientos Asociados</span>
            
            {#each transactions as tx}
                {@const amt = getAccountImpact(tx)}
                <a href="/transactions/{tx.id}" class="p-3 bg-white rounded-xl border border-slate-100 shadow-sm flex justify-between items-center block hover:border-indigo-100 transition-all">
                    <div>
                        <span class="font-bold text-xs text-slate-800 block">{tx.description}</span>
                        <span class="text-[9px] text-slate-400 block">{new Date(tx.date).toLocaleDateString()}</span>
                    </div>
                    <span class="font-extrabold text-xs {amt < 0 ? 'text-slate-800' : 'text-emerald-600'}">
                        ${Math.abs(amt).toLocaleString()}
                    </span>
                </a>
            {:else}
                <p class="text-center text-xs text-slate-400 py-6">No hay operaciones registradas en esta cuenta.</p>
            {/each}
        </div>
    {/if}
</main>