<script lang="ts">
    import { onMount } from 'svelte';

    let accounts: any[] = [];
    let categories: any[] = [];
    let entities: any[] = [];
    let rates: any[] = [];

    let type: 'gasto' | 'ingreso' | 'transferencia' | 'deuda' | 'pago_deuda' = 'gasto';

    let description = '';
    let amount = '';
    let targetAmount = ''; // Se auto-calcula
    
    // Variables para Impuestos/Tasas en transferencias
    let feeAmount = '';
    let feeCategoryId: any = null;

    let selectedCurrency = 'ARS';
    let primaryAccountId: any = null;
    
    // Ahora coexisten libremente
    let selectedCategoryId: any = null;
    let selectedPersonId: any = null;
    let destinationAccountId: any = null;

    let loading = false;
    let successMessage = '';
    let errorMessage = '';

    async function loadFormHub() {
        try {
            const [resAcc, resCat, resEnt, resRates] = await Promise.all([
                fetch('http://127.0.0.1:8000/accounts'),
                fetch('http://127.0.0.1:8000/categories'),
                fetch('http://127.0.0.1:8000/people'),
                fetch('http://127.0.0.1:8000/settings/rates/')
            ]);
            if (resAcc.ok) accounts = await resAcc.json();
            if (resCat.ok) categories = await resCat.json();
            if (resEnt.ok) entities = await resEnt.json();
            if (resRates.ok) rates = await resRates.json();

            if (accounts.length > 0) {
                primaryAccountId = accounts[0].id;
                selectedCurrency = accounts[0].currency;
            }
        } catch {
            errorMessage = 'Error conectando al backend.';
        }
    }

    onMount(loadFormHub);

    $: {
        if (primaryAccountId && (type === 'gasto' || type === 'ingreso' || type === 'transferencia' || type === 'pago_deuda')) {
            const acc = accounts.find(a => a.id == primaryAccountId);
            if (acc) selectedCurrency = acc.currency;
        }
    }

    $: isMultiCurrencyTransfer = (() => {
        if (type !== 'transferencia' || !primaryAccountId || !destinationAccountId) return false;
        const src = accounts.find(a => a.id == primaryAccountId);
        const dst = accounts.find(a => a.id == destinationAccountId);
        return src && dst && src.currency !== dst.currency;
    })();

    // Auto-cálculo reactivo para cruce de divisas
    $: {
        if (isMultiCurrencyTransfer && amount && rates.length > 0) {
            const srcRateObj = rates.find(r => r.currency === selectedCurrency);
            const dstCurr = accounts.find(a => a.id == destinationAccountId)?.currency || 'ARS';
            const dstRateObj = rates.find(r => r.currency === dstCurr);
            
            const srcRate = srcRateObj ? parseFloat(srcRateObj.rate_to_base) : 1;
            const dstRate = dstRateObj ? parseFloat(dstRateObj.rate_to_base) : 1;
            
            const baseVal = parseFloat(amount) * srcRate;
            targetAmount = (baseVal / dstRate).toFixed(2);
        }
    }

    function switchMode(newMode: 'gasto' | 'ingreso' | 'transferencia' | 'deuda' | 'pago_deuda') {
        type = newMode;
        destinationAccountId = null;
        selectedCategoryId = null;
        selectedPersonId = null;
        targetAmount = '';
        feeAmount = '';
        errorMessage = '';
        successMessage = '';
        if (type === 'deuda') selectedCurrency = 'ARS';
    }

    function toBaseAmount(val: number, curr: string) {
        if (curr === 'ARS') return val;
        const rateObj = rates.find(r => r.currency === curr);
        const rate = rateObj ? parseFloat(rateObj.rate_to_base) : 1000;
        return val * rate;
    }

    async function submitOperation() {
        if (!amount || parseFloat(amount) <= 0) {
            errorMessage = 'Monto ingresado no válido.'; return;
        }
        if (type !== 'deuda' && !primaryAccountId) {
            errorMessage = 'Seleccioná la cuenta afectada.'; return;
        }
        if (type === 'transferencia' && (!destinationAccountId || primaryAccountId == destinationAccountId)) {
            errorMessage = 'Cuenta destino inválida.'; return;
        }
        if ((type === 'deuda' || type === 'pago_deuda') && !selectedPersonId) {
            errorMessage = 'Seleccioná la entidad correspondiente.'; return;
        }

        loading = true;
        errorMessage = '';
        successMessage = '';

        const val = parseFloat(amount);
        const baseVal = toBaseAmount(val, selectedCurrency);
        const feeVal = feeAmount ? parseFloat(feeAmount) : 0;
        const baseFeeVal = toBaseAmount(feeVal, selectedCurrency);

        let entries: any[] = [];

        if (type === 'gasto') {
            entries = [
                { account_id: parseInt(primaryAccountId), amount: -val, base_amount: -baseVal },
                { 
                    amount: val, base_amount: baseVal,
                    category_id: selectedCategoryId ? parseInt(selectedCategoryId) : null,
                    person_id: selectedPersonId ? parseInt(selectedPersonId) : null
                }
            ];
        } else if (type === 'ingreso') {
            entries = [
                { account_id: parseInt(primaryAccountId), amount: val, base_amount: baseVal },
                { 
                    amount: -val, base_amount: -baseVal,
                    category_id: selectedCategoryId ? parseInt(selectedCategoryId) : null,
                    person_id: selectedPersonId ? parseInt(selectedPersonId) : null
                }
            ];
        } else if (type === 'transferencia') {
            const dstVal = isMultiCurrencyTransfer ? parseFloat(targetAmount) : val;
            
            // Si hay comisión, se resta extra de la cuenta origen
            entries = [
                { account_id: parseInt(primaryAccountId), amount: -(val + feeVal), base_amount: -(baseVal + baseFeeVal) },
                { account_id: parseInt(destinationAccountId), amount: dstVal, base_amount: baseVal }
            ];

            // Pata contable exclusiva para el impuesto
            if (feeVal > 0) {
                entries.push({
                    amount: feeVal, base_amount: baseFeeVal,
                    category_id: feeCategoryId ? parseInt(feeCategoryId) : null
                });
            }
        } else if (type === 'deuda') {
            entries = [
                { amount: val, base_amount: baseVal, category_id: selectedCategoryId ? parseInt(selectedCategoryId) : null },
                { amount: -val, base_amount: -baseVal, person_id: primaryAccountId ? parseInt(primaryAccountId) : null }
            ];
        } else if (type === 'pago_deuda') {
            entries = [
                { account_id: parseInt(primaryAccountId), amount: -val, base_amount: -baseVal },
                { amount: val, base_amount: baseVal, person_id: parseInt(selectedPersonId) }
            ];
        }

        const fallbackDesc = { gasto: 'Gasto', ingreso: 'Ingreso', transferencia: 'Transferencia', deuda: 'Gasto a Pagar', pago_deuda: 'Pago de Deuda' };
        const payload = {
            description: description.trim() || fallbackDesc[type],
            entries
        };

        try {
            const res = await fetch('http://127.0.0.1:8000/transactions/', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error();
            
            successMessage = '¡Operación registrada con éxito!';
            description = ''; amount = ''; targetAmount = ''; feeAmount = '';
            selectedCategoryId = null; selectedPersonId = null; destinationAccountId = null;
            setTimeout(() => successMessage = '', 3000);
        } catch {
            errorMessage = 'No se pudo procesar la transacción.';
        } finally {
            loading = false;
        }
    }
</script>

<main class="p-4 max-w-md mx-auto space-y-4 pb-12">
    <header class="flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Cargar Operación</h1>
        <button type="button" on:click={() => history.back()} class="text-xs font-bold text-indigo-600 px-3 py-1.5 bg-indigo-50 rounded-xl">← Volver</button>
    </header>

    {#if successMessage}<div class="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-xs font-bold text-center">{successMessage}</div>{/if}
    {#if errorMessage}<div class="p-3 bg-red-50 text-red-600 rounded-xl text-xs font-bold text-center">{errorMessage}</div>{/if}

    <div class="flex bg-slate-200/70 p-1 rounded-xl gap-0.5">
        <button type="button" on:click={() => switchMode('gasto')} class="flex-1 py-1.5 text-[9px] font-bold rounded-lg transition-all {type === 'gasto' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'}">GASTO</button>
        <button type="button" on:click={() => switchMode('ingreso')} class="flex-1 py-1.5 text-[9px] font-bold rounded-lg transition-all {type === 'ingreso' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'}">INGRESO</button>
        <button type="button" on:click={() => switchMode('transferencia')} class="flex-1 py-1.5 text-[9px] font-bold rounded-lg transition-all {type === 'transferencia' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500'}">TRANSF.</button>
        <button type="button" on:click={() => switchMode('deuda')} class="flex-1 py-1.5 text-[9px] font-bold rounded-lg transition-all {type === 'deuda' ? 'bg-red-600 text-white shadow-sm' : 'text-slate-500'}">A PAGAR</button>
        <button type="button" on:click={() => switchMode('pago_deuda')} class="flex-1 py-1.5 text-[9px] font-bold rounded-lg transition-all {type === 'pago_deuda' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-500'}">SALDAR</button>
    </div>

    <form on:submit|preventDefault={submitOperation} class="space-y-3">
        <div class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm flex justify-between items-center gap-2">
            <div class="flex-1">
                <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">Monto {isMultiCurrencyTransfer ? 'Origen' : ''}</label>
                <input type="number" step="0.01" placeholder="0.00" bind:value={amount} class="w-full text-2xl font-bold text-slate-800 focus:outline-none" required />
            </div>
            <div class="w-24 border-l pl-2">
                <label class="block text-[9px] font-bold text-slate-400 uppercase mb-1">Divisa</label>
                <select bind:value={selectedCurrency} class="w-full text-xs font-bold text-indigo-600 bg-slate-50 p-1 rounded focus:outline-none">
                    <option value="ARS">ARS</option>
                    <option value="USD">USD</option>
                    <option value="USDT">USDT</option>
                    <option value="BTC">BTC</option>
                </select>
            </div>
        </div>

        {#if isMultiCurrencyTransfer}
            <div class="bg-indigo-50/50 p-3.5 rounded-2xl border border-indigo-100 shadow-sm animate-fade-in">
                <label class="block text-[10px] font-bold text-indigo-600 uppercase mb-1">Monto de Ingreso Auto-Calculado</label>
                <div class="flex items-center justify-between">
                    <input type="number" step="0.01" bind:value={targetAmount} class="w-full text-xl font-bold text-slate-800 bg-transparent focus:outline-none" required />
                    <span class="text-xs font-extrabold text-indigo-600 bg-white px-2 py-1 rounded border shadow-sm">
                        {accounts.find(a => a.id == destinationAccountId)?.currency}
                    </span>
                </div>
            </div>
        {/if}

        <div class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm">
            <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">Concepto</label>
            <input type="text" placeholder="Detalle de la operación..." bind:value={description} class="w-full text-sm text-slate-700 focus:outline-none" />
        </div>

        {#if type === 'transferencia'}
            <div class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm">
                <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">Cuenta Origen</label>
                <select bind:value={primaryAccountId} class="w-full text-sm font-medium text-slate-700 bg-white focus:outline-none">
                    {#each accounts as acc}<option value={acc.id}>{acc.entity} - {acc.name}</option>{/each}
                </select>
            </div>
            <div class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm">
                <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">Cuenta Destino</label>
                <select bind:value={destinationAccountId} class="w-full text-sm font-medium text-slate-700 bg-white focus:outline-none" required>
                    <option value={null}>Seleccionar destino...</option>
                    {#each accounts.filter(a => a.id != primaryAccountId) as acc}<option value={acc.id}>{acc.entity} - {acc.name}</option>{/each}
                </select>
            </div>
            <div class="bg-red-50/50 p-3.5 rounded-2xl border border-red-100 shadow-sm">
                <label class="block text-[10px] font-bold text-red-500 uppercase mb-1">Tasas / Impuestos Bancarios (Opcional)</label>
                <div class="flex gap-2">
                    <input type="number" step="0.01" placeholder="0.00" bind:value={feeAmount} class="w-24 p-2 bg-white rounded-lg text-sm font-bold border border-red-100 focus:outline-none" />
                    <select bind:value={feeCategoryId} class="flex-1 text-xs text-slate-700 bg-white border border-red-100 rounded-lg px-2 focus:outline-none">
                        <option value={null}>Sin categorizar...</option>
                        {#each categories as cat}<option value={cat.id}>{cat.name}</option>{/each}
                    </select>
                </div>
            </div>

        {:else}
            <div class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm">
                <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">
                    {type === 'deuda' ? 'Acreedor (Entidad)' : type === 'pago_deuda' ? 'Cuenta de Pago (Origen)' : type === 'ingreso' ? 'Cuenta Receptora' : 'Cuenta de Pago'}
                </label>
                <select bind:value={primaryAccountId} class="w-full text-sm font-medium text-slate-700 bg-white focus:outline-none" required>
                    <option value={null}>Seleccionar...</option>
                    {#if type === 'deuda'}
                        {#each entities as ent}<option value={ent.id}>{ent.name}</option>{/each}
                    {:else}
                        {#each accounts as acc}<option value={acc.id}>{acc.entity} - {acc.name}</option>{/each}
                    {/if}
                </select>
            </div>

            <div class="grid grid-cols-2 gap-2">
                <div class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm">
                    <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">Categoría</label>
                    <select bind:value={selectedCategoryId} class="w-full text-xs text-slate-700 bg-white focus:outline-none" disabled={type === 'pago_deuda'}>
                        <option value={null}>Ninguna</option>
                        {#each categories as cat}<option value={cat.id}>{cat.name}</option>{/each}
                    </select>
                </div>
                <div class="bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm">
                    <label class="block text-[10px] font-bold text-slate-400 uppercase mb-1">Entidad</label>
                    <select bind:value={selectedPersonId} class="w-full text-xs text-slate-700 bg-white focus:outline-none" required={type === 'pago_deuda'}>
                        <option value={null}>Ninguna</option>
                        {#each entities as ent}<option value={ent.id}>{ent.name}</option>{/each}
                    </select>
                </div>
            </div>
        {/if}

        <button type="submit" disabled={loading} class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl shadow-lg mt-2 text-sm transition-all">
            {loading ? 'Procesando...' : 'Confirmar Movimiento'}
        </button>
    </form>
</main>