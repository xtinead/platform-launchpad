"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";

import {
  clearSession,
  getAccessToken,
  getCurrentUser,
} from "@/lib/auth-session";
import type { UserSummary } from "@/lib/auth-types";

type SessionSnapshot = {
  token: string | null;
  user: UserSummary | null;
};

const EMPTY_SESSION: SessionSnapshot = {
  token: null,
  user: null,
};

let cachedToken: string | null | undefined;
let cachedUserValue: string | null | undefined;
let cachedSnapshot = EMPTY_SESSION;

function subscribe() {
  return () => {};
}

function getServerSessionSnapshot(): SessionSnapshot {
  return EMPTY_SESSION;
}

function getSessionSnapshot(): SessionSnapshot {
  const token = getAccessToken();
  const user = getCurrentUser();
  const userValue = user ? JSON.stringify(user) : null;

  if (
    token === cachedToken &&
    userValue === cachedUserValue
  ) {
    return cachedSnapshot;
  }

  cachedToken = token;
  cachedUserValue = userValue;

  cachedSnapshot = {
    token,
    user,
  };

  return cachedSnapshot;
}

function getServerHydrationSnapshot(): boolean {
  return false;
}

function getHydrationSnapshot(): boolean {
  return true;
}

export default function DashboardPage() {
  const router = useRouter();

  const isHydrated = useSyncExternalStore(
    subscribe,
    getHydrationSnapshot,
    getServerHydrationSnapshot,
  );

  const session = useSyncExternalStore(
    subscribe,
    getSessionSnapshot,
    getServerSessionSnapshot,
  );

  useEffect(() => {
    if (
      isHydrated &&
      (!session.token || !session.user)
    ) {
      router.replace("/login");
    }
  }, [
    isHydrated,
    router,
    session.token,
    session.user,
  ]);

  function handleSignOut() {
    clearSession();
    router.replace("/login");
  }

  if (!isHydrated) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-slate-500">
          Loading Platform Launchpad...
        </p>
      </main>
    );
  }

  if (!session.token || !session.user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-slate-500">
          Redirecting to sign in...
        </p>
      </main>
    );
  }

  const user = session.user;

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-lg font-semibold text-slate-950">
              Platform Launchpad
            </p>

            <p className="text-sm text-slate-500">
              Environment & Deployment Management
            </p>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-slate-900">
                {user.full_name}
              </p>

              <p className="text-xs text-slate-500">
                {user.email}
              </p>
            </div>

            <button
              type="button"
              onClick={handleSignOut}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-6 py-10">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
          Dashboard
        </p>

        <h1 className="mt-2 text-3xl font-bold text-slate-950">
          Welcome, {user.full_name}
        </h1>

        <p className="mt-2 text-slate-600">
          Your platform environments and deployment activity will appear here.
        </p>

        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            ["Environments", "0"],
            ["Active Deployments", "0"],
            ["Role", user.role],
          ].map(([label, value]) => (
            <article
              key={label}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <p className="text-sm font-medium text-slate-500">
                {label}
              </p>

              <p className="mt-3 text-3xl font-bold capitalize text-slate-950">
                {value}
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
