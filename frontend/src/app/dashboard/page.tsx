"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ApiError } from "@/lib/api";
import {
  clearSession,
  getAccessToken,
  getCurrentUser,
} from "@/lib/auth-session";
import {
  listDeploymentRequests,
  listEnvironments,
} from "@/lib/platform-api";
import type {
  DeploymentRequestListResponse,
  EnvironmentListResponse,
} from "@/lib/platform-types";
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

  const [environments, setEnvironments] =
    useState<EnvironmentListResponse | null>(null);

  const [deploymentRequests, setDeploymentRequests] =
    useState<DeploymentRequestListResponse | null>(null);

  const [isLoadingData, setIsLoadingData] = useState(false);

  const [error, setError] = useState<string | null>(null);

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

  useEffect(() => {
    if (!isHydrated || !session.token) {
      return;
    }

    let cancelled = false;

    async function loadDashboardData() {
      setIsLoadingData(true);
      setError(null);

      try {
        const [
          environmentResponse,
          deploymentRequestResponse,
        ] = await Promise.all([
          listEnvironments(session.token as string),
          listDeploymentRequests(session.token as string),
        ]);

        if (cancelled) {
          return;
        }

        setEnvironments(environmentResponse);
        setDeploymentRequests(deploymentRequestResponse);
      } catch (error) {
        if (cancelled) {
          return;
        }

        if (error instanceof ApiError) {
          if (
            error.code === "invalid_token" ||
            error.code === "token_expired" ||
            error.code === "authentication_required"
          ) {
            clearSession();
            router.replace("/login");
            return;
          }

          setError(error.message);
          return;
        }

        setError("Unable to load platform data.");
      } finally {
        if (!cancelled) {
          setIsLoadingData(false);
        }
      }
    }

    void loadDashboardData();

    return () => {
      cancelled = true;
    };
  }, [isHydrated, router, session.token]);

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

  const activeDeploymentCount =
    deploymentRequests?.items.filter(
      (request) =>
        request.status === "queued" ||
        request.status === "processing",
    ).length ?? 0;

  const environmentCount =
    environments?.pagination.total_items ?? 0;

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
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
              Dashboard
            </p>

            <h1 className="mt-2 text-3xl font-bold text-slate-950">
              Welcome, {user.full_name}
            </h1>

            <p className="mt-2 text-slate-600">
              Monitor environments and deployment activity from one place.
            </p>
          </div>

          <Link
            href="/environments"
            className="inline-flex rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
          >
            View environments
          </Link>
        </div>

        {error ? (
          <div className="mt-8 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <div className="mt-10 grid gap-6 md:grid-cols-3">
          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-slate-500">
              Environments
            </p>

            <p className="mt-3 text-3xl font-bold text-slate-950">
              {isLoadingData ? "—" : environmentCount}
            </p>
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-slate-500">
              Active Deployments
            </p>

            <p className="mt-3 text-3xl font-bold text-slate-950">
              {isLoadingData ? "—" : activeDeploymentCount}
            </p>
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-slate-500">
              Role
            </p>

            <p className="mt-3 text-3xl font-bold capitalize text-slate-950">
              {user.role}
            </p>
          </article>
        </div>

        <div className="mt-10 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-950">
                Platform status
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Live data from the Platform Launchpad API.
              </p>
            </div>

            <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
              Connected
            </span>
          </div>
        </div>
      </section>
    </main>
  );
}
