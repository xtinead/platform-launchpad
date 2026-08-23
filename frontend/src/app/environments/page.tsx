"use client";

import Link from "next/link";
import {
  FormEvent,
  useCallback,
  useEffect,
  useState,
  useSyncExternalStore,
} from "react";
import { useRouter } from "next/navigation";

import { ApiError } from "@/lib/api";
import {
  clearSession,
  getAccessToken,
  getCurrentUser,
} from "@/lib/auth-session";
import {
  createEnvironment,
  listEnvironments,
} from "@/lib/platform-api";
import type {
  EnvironmentCreateRequest,
  EnvironmentListResponse,
  EnvironmentStatus,
  EnvironmentType,
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

const statusStyles: Record<EnvironmentStatus, string> = {
  pending: "bg-amber-100 text-amber-700",
  provisioning: "bg-blue-100 text-blue-700",
  active: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
  destroying: "bg-orange-100 text-orange-700",
  destroyed: "bg-slate-200 text-slate-700",
};

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function EnvironmentsPage() {
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

  const [environmentList, setEnvironmentList] =
    useState<EnvironmentListResponse | null>(null);

  const [name, setName] = useState("");
  const [environmentType, setEnvironmentType] =
    useState<EnvironmentType>("development");
  const [applicationVersion, setApplicationVersion] =
    useState("1.0.0");
  const [description, setDescription] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  const [loadError, setLoadError] =
    useState<string | null>(null);

  const [createError, setCreateError] =
    useState<string | null>(null);

  const [createSuccess, setCreateSuccess] =
    useState<string | null>(null);

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

  const loadEnvironments = useCallback(async () => {
    if (!session.token) {
      return;
    }

    setIsLoading(true);
    setLoadError(null);

    try {
      const response = await listEnvironments(
        session.token,
      );

      setEnvironmentList(response);
    } catch (error) {
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

        setLoadError(error.message);
      } else {
        setLoadError("Unable to load environments.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [router, session.token]);

 useEffect(() => {
  if (!isHydrated || !session.token) {
    return;
  }

  const timeoutId = window.setTimeout(() => {
    void loadEnvironments();
  }, 0);

  return () => {
    window.clearTimeout(timeoutId);
  };
}, [
  isHydrated,
  loadEnvironments,
  session.token,
]);

  async function handleCreateEnvironment(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!session.token) {
      router.replace("/login");
      return;
    }

    setIsCreating(true);
    setCreateError(null);
    setCreateSuccess(null);

    const request: EnvironmentCreateRequest = {
      name,
      environment_type: environmentType,
      application_version: applicationVersion,
      description: description.trim() || null,
    };

    try {
      const environment = await createEnvironment(
        session.token,
        request,
      );

      setCreateSuccess(
        `Environment "${environment.name}" created in pending state.`,
      );

      setName("");
      setEnvironmentType("development");
      setApplicationVersion("1.0.0");
      setDescription("");

      await loadEnvironments();
    } catch (error) {
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

        setCreateError(error.message);
      } else {
        setCreateError(
          "Unable to create environment.",
        );
      }
    } finally {
      setIsCreating(false);
    }
  }

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

  const environments = environmentList?.items ?? [];

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-lg font-semibold text-slate-950">
              Platform Launchpad
            </p>

            <p className="text-sm text-slate-500">
              Environment Management
            </p>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="text-sm font-medium text-slate-600 hover:text-slate-950"
            >
              Dashboard
            </Link>

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
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
            Environments
          </p>

          <h1 className="mt-2 text-3xl font-bold text-slate-950">
            Manage application environments
          </h1>

          <p className="mt-2 max-w-2xl text-slate-600">
            Define environments here, then queue lifecycle
            operations separately through the platform worker.
          </p>
        </div>

        <div className="mt-10 grid gap-8 lg:grid-cols-[380px_1fr]">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-950">
              Create environment
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              New environments begin in pending state.
            </p>

            <form
              onSubmit={handleCreateEnvironment}
              className="mt-6 space-y-5"
            >
              <div>
                <label
                  htmlFor="environment-name"
                  className="block text-sm font-medium text-slate-700"
                >
                  Name
                </label>

                <input
                  id="environment-name"
                  value={name}
                  onChange={(event) =>
                    setName(event.target.value)
                  }
                  required
                  minLength={3}
                  maxLength={100}
                  placeholder="payments-dev"
                  pattern="[a-z0-9][a-z0-9-]*[a-z0-9]"
                  className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />

                <p className="mt-2 text-xs leading-5 text-slate-500">
                  Lowercase letters, numbers, and hyphens only.
                </p>
              </div>

              <div>
                <label
                  htmlFor="environment-type"
                  className="block text-sm font-medium text-slate-700"
                >
                  Environment type
                </label>

                <select
                  id="environment-type"
                  value={environmentType}
                  onChange={(event) =>
                    setEnvironmentType(
                      event.target.value as EnvironmentType,
                    )
                  }
                  className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  <option value="development">
                    Development
                  </option>
                  <option value="staging">
                    Staging
                  </option>
                  <option value="demo">
                    Demo
                  </option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="application-version"
                  className="block text-sm font-medium text-slate-700"
                >
                  Application version
                </label>

                <input
                  id="application-version"
                  value={applicationVersion}
                  onChange={(event) =>
                    setApplicationVersion(
                      event.target.value,
                    )
                  }
                  required
                  maxLength={100}
                  className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              <div>
                <label
                  htmlFor="description"
                  className="block text-sm font-medium text-slate-700"
                >
                  Description
                </label>

                <textarea
                  id="description"
                  value={description}
                  onChange={(event) =>
                    setDescription(event.target.value)
                  }
                  maxLength={1000}
                  rows={4}
                  placeholder="Purpose of this environment..."
                  className="mt-2 w-full resize-none rounded-lg border border-slate-300 px-3 py-2.5 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              {createError ? (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {createError}
                </div>
              ) : null}

              {createSuccess ? (
                <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
                  {createSuccess}
                </div>
              ) : null}

              <button
                type="submit"
                disabled={isCreating}
                className="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isCreating
                  ? "Creating..."
                  : "Create environment"}
              </button>
            </form>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-6 py-5">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-slate-950">
                    Environment inventory
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    {environmentList
                      ? `${environmentList.pagination.total_items} total`
                      : "Loading environments..."}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() =>
                    void loadEnvironments()
                  }
                  disabled={isLoading}
                  className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60"
                >
                  Refresh
                </button>
              </div>
            </div>

            {loadError ? (
              <div className="m-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {loadError}
              </div>
            ) : null}

            {!loadError &&
            !isLoading &&
            environments.length === 0 ? (
              <div className="px-6 py-16 text-center">
                <h3 className="font-semibold text-slate-950">
                  No environments yet
                </h3>

                <p className="mt-2 text-sm text-slate-500">
                  Create your first environment using the
                  form on this page.
                </p>
              </div>
            ) : null}

            {environments.length > 0 ? (
              <div className="divide-y divide-slate-200">
                {environments.map((environment) => (
                  <article
                    key={environment.id}
                    className="px-6 py-5"
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-3">
                          <h3 className="font-semibold text-slate-950">
                            {environment.name}
                          </h3>

                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusStyles[environment.status]}`}
                          >
                            {environment.status}
                          </span>
                        </div>

                        <p className="mt-2 text-sm text-slate-600">
                          {environment.description ||
                            "No description provided."}
                        </p>
                      </div>

                      <div className="text-left text-sm sm:text-right">
                        <p className="font-medium capitalize text-slate-700">
                          {environment.environment_type}
                        </p>

                        <p className="mt-1 text-slate-500">
                          Version{" "}
                          {environment.application_version}
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-xs text-slate-500">
                      <span>
                        Created{" "}
                        {formatDate(
                          environment.created_at,
                        )}
                      </span>

                      {environment.external_url ? (
                        <a
                          href={environment.external_url}
                          target="_blank"
                          rel="noreferrer"
                          className="font-medium text-blue-600 hover:text-blue-700"
                        >
                          Open environment
                        </a>
                      ) : (
                        <span>No external URL yet</span>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            ) : null}
          </section>
        </div>
      </section>
    </main>
  );
}
