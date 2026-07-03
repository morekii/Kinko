import { PUBLIC_API_URL } from '$env/static/public';
import type {
	Account,
	AccountBalance,
	Category,
	DebtPayload,
	DebtPaymentPayload,
	Entry,
	ExchangeRate,
	ExpensePayload,
	IncomePayload,
	Notification,
	Person,
	Subscription,
	TotalBalance,
	Transaction,
	TransferPayload
} from './types';

export class ApiError extends Error {
	status: number;
	constructor(status: number, message: string) {
		super(message);
		this.status = status;
	}
}

async function apiFetch<T>(path: string, opts: RequestInit = {}): Promise<T> {
	const res = await fetch(`${PUBLIC_API_URL}${path}`, {
		...opts,
		headers: { 'Content-Type': 'application/json', ...opts.headers }
	});

	if (!res.ok) {
		let detail = `Error ${res.status}`;
		try {
			const body = await res.json();
			detail = body.detail ?? detail;
		} catch {
			// respuesta sin cuerpo JSON, dejamos el detail genérico
		}
		throw new ApiError(res.status, detail);
	}

	if (res.status === 204) return undefined as T;
	return res.json();
}

const get = <T>(path: string) => apiFetch<T>(path);
const post = <T>(path: string, body: unknown) =>
	apiFetch<T>(path, { method: 'POST', body: JSON.stringify(body) });
const patch = <T>(path: string, body: unknown) =>
	apiFetch<T>(path, { method: 'PATCH', body: JSON.stringify(body) });
const del = <T>(path: string) => apiFetch<T>(path, { method: 'DELETE' });

// --- Cuentas ---
export const getAccounts = () => get<Account[]>('/accounts');
export const createAccount = (data: Partial<Account>) => post<Account>('/accounts', data);
export const updateAccount = (id: number, data: Partial<Account>) =>
	patch<Account>(`/accounts/${id}`, data);
export const deleteAccount = (id: number) => del<void>(`/accounts/${id}`);

// --- Categorías ---
export const getCategories = () => get<Category[]>('/categories');
export const createCategory = (data: Partial<Category>) => post<Category>('/categories', data);
export const updateCategory = (id: number, data: Partial<Category>) =>
	patch<Category>(`/categories/${id}`, data);
export const deleteCategory = (id: number) => del<void>(`/categories/${id}`);

// --- Personas / entidades ---
export const getPeople = () => get<Person[]>('/people');
export const createPerson = (data: Partial<Person>) => post<Person>('/people', data);
export const updatePerson = (id: number, data: Partial<Person>) =>
	patch<Person>(`/people/${id}`, data);
export const deletePerson = (id: number) => del<void>(`/people/${id}`);

// --- Transacciones ---
export const getTransactions = (limit = 200) =>
	get<Transaction[]>(`/transactions/?limit=${limit}`);
export const getTransaction = (id: number) => get<Transaction>(`/transactions/${id}`);
export const updateTransaction = (id: number, data: { description: string; date?: string; entries: Partial<Entry>[] }) =>
	patch<{ status: string; transaction_id: number }>(`/transactions/${id}`, data);
export const deleteTransaction = (id: number) => del<void>(`/transactions/${id}`);

export const createExpense = (data: ExpensePayload) =>
	post<{ status: string; transaction_id: number }>('/transactions/expense', data);
export const createIncome = (data: IncomePayload) =>
	post<{ status: string; transaction_id: number }>('/transactions/income', data);
export const createTransfer = (data: TransferPayload) =>
	post<{ status: string; transaction_id: number }>('/transactions/transfer', data);
export const createDebt = (data: DebtPayload) =>
	post<{ status: string; transaction_id: number }>('/transactions/debt', data);
export const createDebtPayment = (data: DebtPaymentPayload) =>
	post<{ status: string; transaction_id: number }>('/transactions/debt-payment', data);

// --- Analítica ---
export const getBalances = () => get<AccountBalance[]>('/analytics/balances');
export const getNetWorth = () => get<TotalBalance>('/analytics/net-worth');

// --- Cotizaciones manuales ---
export const getRates = () => get<ExchangeRate[]>('/settings/rates/');
export const updateRates = (rates: Record<string, number>) =>
	patch<ExchangeRate[]>('/settings/rates/', { rates });

// --- Suscripciones ---
export const getSubscriptions = () => get<Subscription[]>('/subscriptions/');
export const createSubscription = (data: Partial<Subscription>) =>
	post<Subscription>('/subscriptions/', data);
export const deleteSubscription = (id: number) => del<void>(`/subscriptions/${id}`);

// --- Notificaciones ---
export const getNotifications = () => get<Notification[]>('/notifications/');
export const resolveNotification = (id: number) =>
	post<{ status: string }>(`/notifications/${id}/resolve`, {});
export const dismissNotification = (id: number) =>
	post<{ status: string }>(`/notifications/${id}/dismiss`, {});
