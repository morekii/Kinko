<script lang="ts">
    import { onMount } from 'svelte';

    let totalBalance = { day_to_day_available: 0, total_assets: 0, total_liabilities: 0, net_worth: 0 };
    let accounts: any[] = [];
    let transactions: any[] = [];
    let categories: any[] = [];
    let showAmounts = true;
    let activeTab: 'list' | 'chart' | 'accounts' = 'list';

    async function fetchData() {
        try {
            const [resNet, resAcc, resTx, resCat] = await Promise.all([
                fetch('http://127.0.0.1:8000/analytics/net-worth'),
                fetch('http://127.0.0.1:8000/analytics/balances'),
                fetch('http://127.0.0.1:8000/transactions/?limit=20'),
                fetch('http://127.0.0.1:8000/categories')
            ]);
            if (resNet.ok) totalBalance = await resNet.json();
            if (resAcc.ok) accounts = await resAcc.json();
            if (resTx.ok) transactions = await resTx.json();
            if (resCat.ok) categories = await resCat.json();
        } catch (err) {
            console.error("Error cargando datos principales:", err);
        }
    }

    onMount(fetchData);

    $: fmt = (val: number, prefix = '$') => showAmounts ? `${prefix}${val.toLocaleString()}` : '••••••';

    // Mapeo dinámico y tipado correcto para los gráficos
    $: categoryTotals = transactions.reduce((acc: Record<string, number>, tx: any) => {
        const catEntry = tx.entries?.find((e: any) => e.category_id && e.amount > 0);
        if (catEntry) {
            const catObj = categories.find(c => c.id === catEntry.category_id);
            const label = catObj ? catObj.name : `Categoría ID: ${catEntry.category_id}`;
            acc[label] = (acc[label] || 0) + parseFloat(catEntry.base_amount);
        }
        return acc;
    }, {} as Record<string, number>);

    $: maxCategoryValue = Math.max(...Object.values(categoryTotals).concat(1));
    $: dailyAccounts = accounts.filter(a => a.is_day_to_day && a.is_active);
    $: savingsAccounts = accounts.filter(a => !a.is_day_to_day && a.is_active);
</script>

<main class="p-4 max-w-md mx-auto pb-12">
    <div class="flex justify-between items-center mb-4">
        <h1 class="text-xl font-extrabold text-slate-800">Estado Financiero</h1>
        <button type="button" on:click={() => showAmounts = !showAmounts} class="text-[10px] font-bold uppercase tracking-wider bg-slate-200/70 text-slate-700 px-2.5 py-1 rounded-lg transition-all hover:bg-slate-300">
            {showAmounts ? '🙈 Ocultar Saldos' : '👁️ Mostrar'}
        </button>
    </div>

    <div class="bg-indigo-600 rounded-3xl p-6 text-white shadow-xl mb-4 relative overflow-hidden">
        <div class="absolute right-0 top-0 translate-x-4 -translate-y-4 w-32 h-32 bg-indigo-500/30 rounded-full blur-xl"></div>
        <span class="text-indigo-100 text-xs uppercase tracking-wider font-semibold block">Disponible Día a Día</span>
        <h2 class="text-4xl font-extrabold mt-1">{fmt(totalBalance.day_to_day_available)}</h2>
        <div class="mt-5 pt-3 border-t border-indigo-500/60 flex justify-between items-center text-xs">
            <span class="text-indigo-100">Patrimonio Neto Global</span>
            <span class="font-bold text-white text-sm">{fmt(totalBalance.net_worth)}</span>
        </div>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-6">
        <div class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Activos Totales</span>
            <span class="text-sm font-bold text-emerald-600">{fmt(totalBalance.total_assets, '+$')}</span>
        </div>
        <div class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm text-right">
            <span class="text-[10px] text-slate-400 font-bold uppercase block">Pasivos Totales</span>
            <span class="text-sm font-bold text-red-600">{fmt(totalBalance.total_liabilities, '-$')}</span>
        </div>
    </div>

    <div class="flex justify-between items-center mb-3">
        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Actividad & Métricas</h3>
        <div class="bg-slate-200/60 p-0.5 rounded-lg flex gap-1 text-[10px] font-semibold w-2/3">
            <button type="button" on:click={() => activeTab = 'list'} class="flex-1 py-1 rounded-md transition-all {activeTab === 'list' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'}">Último Mes</button>
            <button type="button" on:click={() => activeTab = 'chart'} class="flex-1 py-1 rounded-md transition-all {activeTab === 'chart' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'}">📊 Gráfico</button>
            <button type="button" on:click={() => activeTab = 'accounts'} class="flex-1 py-1 rounded-md transition-all {activeTab === 'accounts' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'}">💳 Cuentas</button>
        </div>
    </div>

    {#if activeTab === 'list'}
        <div class="space-y-2.5 animate-fade-in">
            {#each transactions as tx}
                <a href="/transactions/{tx.id}" class="bg-white p-3.5 rounded-2xl shadow-sm flex justify-between items-center border border-slate-100 block hover:border-indigo-100 transition-all">
                    <div class="flex-1 pr-2">
                        <p class="font-semibold text-slate-800 text-sm truncate">{tx.description}</p>
                        <p class="text-[10px] text-slate-400">{new Date(tx.date).toLocaleDateString()}</p>
                    </div>
                    <div class="text-right">
                        <p class="font-bold text-sm {tx.entries?.[0]?.amount < 0 ? 'text-slate-800' : 'text-emerald-600'}">
                            {showAmounts ? `${tx.entries?.[0]?.amount < 0 ? '-' : '+'}$${Math.abs(tx.entries?.[0]?.amount).toLocaleString()}` : '••••'}
                        </p>
                    </div>
                </a>
            {:else}
                <p class="text-center text-xs text-slate-400 py-6">No hay transacciones recientes.</p>
            {/each}
        </div>
    {:else if activeTab === 'chart'}
        <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm space-y-3 animate-fade-in">
            <p class="text-[11px] text-slate-400 font-medium">Distribución de gastos categorizados:</p>
            {#each Object.entries(categoryTotals) as [catName, total]}
                <div>
                    <div class="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                        <span class="truncate pr-2">{catName}</span>
                        <span>{fmt(total)}</span>
                    </div>
                    <div class="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                        <div class="bg-indigo-600 h-full rounded-full transition-all duration-500" style="width: {(total / maxCategoryValue) * 100}%"></div>
                    </div>
                </div>
            {:else}
                <p class="text-center text-xs text-slate-400 py-4">Sin datos suficientes de categorías.</p>
            {/each}
        </div>
    {:else if activeTab === 'accounts'}
        <div class="space-y-2 animate-fade-in">
            {#each [...dailyAccounts, ...savingsAccounts] as acc}
                <a href="/accounts/{acc.account_id}" class="bg-white p-3 rounded-xl shadow-sm flex justify-between items-center border border-slate-100 block hover:border-indigo-100 transition-all">
                    <div>
                        <p class="font-medium text-slate-800 text-sm">{acc.account_name}</p>
                        <p class="text-[10px] text-slate-400 uppercase">{acc.entity}</p>
                    </div>
                    <div class="text-right">
                        <p class="font-bold text-sm {acc.balance < 0 ? 'text-red-500' : 'text-emerald-600'}">
                            {fmt(parseFloat(acc.balance), acc.currency + ' ')}
                        </p>
                    </div>
                </a>
            {:else}
                <p class="text-center text-xs text-slate-400 py-6">No hay cuentas disponibles.</p>
            {/each}
        </div>
    {/if}
</main>