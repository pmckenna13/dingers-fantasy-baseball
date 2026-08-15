import { useAuth } from "../features/auth/useAuth";

export default function DashboardPage() {
  const { user, logout } = useAuth();

  return (
    <main className="min-h-screen px-4 py-6">
      <header className="mb-6 flex items-center justify-between">
        <h1 className="text-lg font-semibold">Fantasy Baseball</h1>
        <button
          onClick={() => void logout()}
          className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-300"
        >
          Log out
        </button>
      </header>

      <p className="text-slate-300">Welcome, {user?.display_name}.</p>
      <p className="mt-2 text-sm text-slate-500">
        Leagues, rosters, drafts, and live scoring land in later phases — this
        screen is Phase 0's proof that auth + routing work end-to-end.
      </p>
    </main>
  );
}
