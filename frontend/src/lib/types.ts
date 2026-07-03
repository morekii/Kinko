export type AccountType =
	| 'savings'
	| 'checking'
	| 'credit_card'
	| 'cash'
	| 'virtual'
	| 'debt'
	| 'investments';

export interface Account {
	id: number;
	name: string;
	entity: string;
	type: AccountType;
	currency: string;
	is_day_to_day: boolean;
	is_active: boolean;
	reserve_account_id: number | null;
	is_main: boolean;
}

export interface AccountBalance {
	account_id: number;
	account_name: string;
	entity: string;
	balance: number;
	base_balance: number;
	currency: string;
	is_day_to_day: boolean;
	is_active: boolean;
}

export interface TotalBalance {
	day_to_day_available: number;
	total_assets: number;
	total_liabilities: number;
	net_worth: number;
}

export interface Category {
	id: number;
	name: string;
	is_active: boolean;
}

export interface Person {
	id: number;
	name: string;
	is_debt_tracker: boolean;
	is_active: boolean;
	balance: number;
}

export interface ExchangeRate {
	currency: string;
	rate_to_base: number;
	updated_at: string;
}

export interface Subscription {
	id: number;
	description: string;
	amount: number;
	currency: string;
	charge_day: number;
	suggested_account_id: number | null;
	category_id: number | null;
	is_active: boolean;
}

export interface Entry {
	id: number;
	account_id: number | null;
	person_id: number | null;
	category_id: number | null;
	amount: number;
	base_amount: number;
}

export interface Transaction {
	id: number;
	description: string;
	date: string;
	entries: Entry[];
}

export interface Notification {
	id: number;
	title: string;
	message: string;
	action_type: string;
	amount: number;
	is_resolved: boolean;
}

// --- Payloads de los endpoints de intención ---

export interface ExpensePayload {
	description?: string;
	date?: string;
	amount: number;
	currency: string;
	account_id: number;
	category_id?: number | null;
	person_id?: number | null;
	reserve_funds?: boolean;
	reserve_source_account_id?: number | null;
}

export interface IncomePayload {
	description?: string;
	date?: string;
	amount: number;
	currency: string;
	account_id: number;
	category_id?: number | null;
	person_id?: number | null;
}

export interface TransferPayload {
	description?: string;
	date?: string;
	amount: number;
	currency: string;
	source_account_id: number;
	destination_account_id: number;
	fee_amount?: number;
	fee_category_id?: number | null;
	destination_amount?: number | null;
}

export interface DebtPayload {
	description?: string;
	date?: string;
	amount: number;
	currency: string;
	person_id: number;
	category_id?: number | null;
}

export interface DebtPaymentPayload {
	description?: string;
	date?: string;
	amount: number;
	currency: string;
	account_id: number;
	person_id: number;
}
