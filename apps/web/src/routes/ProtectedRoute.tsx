import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../features/auth/useAuth";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { status } = useAuth();

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-400">
        Loading…
      </div>
    );
  }

  if (status === "anonymous") {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
