<script lang="ts">
    import { onMount } from 'svelte';

    let people: any[] = [];
    let name = '';
    let loading = false;

    async function loadPeople() {
        const res = await fetch('http://127.0.0.1:8000/people');
        if (res.ok) people = await res.json();
    }

    onMount(loadPeople);

    async function createPerson() {
        if (!name.trim()) return;
        loading = true;
        try {
            const res = await fetch('http://127.0.0.1:8000/people', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name.trim(), is_active: true })
            });
            if (res.ok) {
                name = '';
                await loadPeople();
            }
        } finally {
            loading = false;
        }
    }

    async function deletePerson(id: int) {
        if (!confirm("¿Ocultar a esta persona?")) return;
        await fetch(`http://127.0.0.1:8000/people/${id}`, { method: 'DELETE' });
        await loadPeople();
    }
</script>

<main class="p-4 max-w-md mx-auto bg-slate-50 min-h-screen">
    <header class="mb-6 flex justify-between items-center">
        <h1 class="text-xl font-bold text-slate-800">Amigos & Deudas</h1>
        <a href="/" class="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-xl border border-indigo-100">← Volver</a>
    </header>

    <form on:submit|preventDefault={createPerson} class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm mb-6 flex gap-2">
        <input type="text" placeholder="Nombre del amigo..." bind:value={name} class="flex-1 p-2 border border-slate-200 rounded-xl text-sm focus:outline-none" required />
        <button type="submit" disabled={loading} class="bg-slate-800 text-white font-bold px-4 py-2 rounded-xl text-sm hover:bg-slate-900">Add</button>
    </form>

    <div class="space-y-2">
        {#each people as prs}
            <div class="bg-white p-3 rounded-xl border border-slate-100 flex justify-between items-center text-sm">
                <span class="font-medium text-slate-800">👥 {prs.name}</span>
                <button type="button" on:click={() => deletePerson(prs.id)} class="text-slate-300 hover:text-red-500 font-bold px-2">✕</button>
            </div>
        {/each}
    </div>
</main>