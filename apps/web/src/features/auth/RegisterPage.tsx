import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError } from "../../api/client";
import { useAuth } from "./useAuth";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(email, displayName, password);
      navigate("/");
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 409
          ? "That email is already registered."
          : "Something went wrong.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 rounded-2xl bg-slate-900 p-6 shadow-lg"
      >
        <h1 className="text-xl font-semibold">Create your account</h1>

        <label className="block space-y-1 text-sm">
          <span className="text-slate-300">Display name</span>
          <input
            required
            autoComplete="nickname"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-base focus:border-emerald-500 focus:outline-none"
          />
        </label>

        <label className="block space-y-1 text-sm">
          <span className="text-slate-300">Email</span>
          <input
            type="email"
            required
            autoComplete="email"
            inputMode="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-base focus:border-emerald-500 focus:outline-none"
          />
        </label>

        <label className="block space-y-1 text-sm">
          <span className="text-slate-300">Password</span>
          <input
            type="password"
            required
            minLength={8}
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-base focus:border-emerald-500 focus:outline-none"
          />
        </label>

        {error && (
          <p role="alert" className="text-sm text-red-400">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-emerald-600 px-3 py-2 font-medium text-white disabled:opacity-50"
        >
          {submitting ? "Creating account…" : "Create account"}
        </button>

        <p className="text-center text-sm text-slate-400">
          Already have an account?{" "}
          <Link to="/login" className="text-emerald-400 hover:underline">
            Log in
          </Link>
        </p>
      </form>
    </main>
  );
}
