"use client";

import Link from "next/link";
import {
  useCallback,
  useEffect,
  useMemo,
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
  listDeploymentRequests,
  listEnvironments,
} from "@/lib/platform-api";
import type {
  DeploymentOperation,
  DeploymentRequestListResponse,
  DeploymentRequestStatus,
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

const statusStyles: Record<
  DeploymentRequestStatus,
  string
> = {
  queued: "bg-amber-100 text-amber-700",
  processing: "bg-blue-100 text-blue-700",
  succeeded: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
  cancelled: "bg-slate-200 text-slate-700",
};

const operationLabels: Record<
  DeploymentOperation,
  string
> = {
  provision: "Provision",
  destroy: "Destroy",
  retry: "Retry",
  upgrade: "Upgrade",
};

function formatDate(
  value: string | null,
): string {
  if (!value) {
    return "—";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function DeploymentsPage() {
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

  const [deploymentList, setDeploymentList] =
    useState<DeploymentRequestListResponse | null>(
      null,
    );

  const [environmentList, setEnvironmentList] =
    useState<EnvironmentListResponse | null>(null);

  const [statusFilter, setStatusFilter] =
    useState<DeploymentRequestStatus | "">("");

  const [operationFilter, setOperationFilter] =
    useState<DeploymentOperation | "">("");

  const [isLoading, setIsLoading] =
    useState(false);

  const [error, setError] =
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

  const loadDeployments = useCallback(
    async () => {
      if (!session.token) {
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const [
          deployments,
          environments,
        ] = await Promise.all([
          listDeploymentRequests(
            session.token,
            {
              page: 1,
              pageSize: 100,
              status:
                statusFilter || undefined,
              operation:
                operationFilter || undefined,
            },
          ),
          listEnvironments(session.token),
        ]);

        setDeploymentList(deployments);
        setEnvironmentList(environments);
      } catch (error) {
        if (error instanceof ApiError) {
          if (
            error.code === "invalid_token" ||
            error.code === "token_expired" ||
            error.code ===
              "authentication_required"
          ) {
            clearSession();
            router.replace("/login");
            return;
          }

          setError(error.message);
        } else {
          setError(
            "Unable to load deployment requests.",
          );
        }
      } finally {
        setIsLoading(false);
      }
    },
    [
      operationFilter,
      router,
      session.token,
      statusFilter,
    ],
  );

  useEffect(() => {
    if (!isHydrated || !session.token) {
      return;
    }

    const timeoutId = window.setTimeout(
      () => {
        void loadDeployments();
      },
      0,
    );

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [
    isHydrated,
    loadDeployments,
    session.token,
  ]);

  const environmentNames = useMemo(() => {
    const names = new Map<string, string>();

    environmentList?.items.forEach(
      (environment) => {
        names.set(
          environment.id,
          environment.name,
        );
      },
    );

    return names;
  }, [environmentList]);

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

  const deploymentRequests =
    deploymentList?.items ?? [];

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-lg font-semibold text-slate-950">
              Platform Launchpad
            </p>

            <p className="text-sm text-slate-500">
              Deployment Activity
            </p>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="text-sm font-medium text-slate-600 hover:text-slate-950"
            >
              Dashboard
            </Link>

            <Link
              href="/environments"
              className="text-sm font-medium text-slate-600 hover:text-slate-950"
            >
              Environments
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
            Deployment Requests
          </p>

          <h1 className="mt-2 text-3xl font-bold text-slate-950">
            Deployment activity
          </h1>

          <p className="mt-2 max-w-2xl text-slate-600">
            Track asynchronous environment
            lifecycle operations executed by the
            Platform Launchpad worker.
          </p>
        </div>

        <section className="mt-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="status-filter"
                  className="block text-sm font-medium text-slate-700"
                >
                  Status
                </label>

                <select
                  id="status-filter"
                  value={statusFilter}
                  onChange={(event) =>
                    setStatusFilter(
                      event.target.value as
                        | DeploymentRequestStatus
                        | "",
                    )
                  }
                  className="mt-2 w-full min-w-48 rounded-lg border border-slate-300 bg-white px-3 py-2.5"
                >
                  <option value="">
                    All statuses
                  </option>
                  <option value="queued">
                    Queued
                  </option>
                  <option value="processing">
                    Processing
                  </option>
                  <option value="succeeded">
                    Succeeded
                  </option>
                  <option value="failed">
                    Failed
                  </option>
                  <option value="cancelled">
                    Cancelled
                  </option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="operation-filter"
                  className="block text-sm font-medium text-slate-700"
                >
                  Operation
                </label>

                <select
                  id="operation-filter"
                  value={operationFilter}
                  onChange={(event) =>
                    setOperationFilter(
                      event.target.value as
                        | DeploymentOperation
                        | "",
                    )
                  }
                  className="mt-2 w-full min-w-48 rounded-lg border border-slate-300 bg-white px-3 py-2.5"
                >
                  <option value="">
                    All operations
                  </option>
                  <option value="provision">
                    Provision
                  </option>
                  <option value="upgrade">
                    Upgrade
                  </option>
                  <option value="retry">
                    Retry
                  </option>
                  <option value="destroy">
                    Destroy
                  </option>
                </select>
              </div>
            </div>

            <button
              type="button"
              onClick={() =>
                void loadDeployments()
              }
              disabled={isLoading}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading
                ? "Refreshing..."
                : "Refresh"}
            </button>
          </div>
        </section>

        {error ? (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <section className="mt-8 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-6 py-5">
            <h2 className="text-lg font-semibold text-slate-950">
              Request history
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              {deploymentList
                ? `${deploymentList.pagination.total_items} request${
                    deploymentList.pagination
                      .total_items === 1
                      ? ""
                      : "s"
                  }`
                : "Loading deployment requests..."}
            </p>
          </div>

          {!error &&
          !isLoading &&
          deploymentRequests.length === 0 ? (
            <div className="px-6 py-16 text-center">
              <h3 className="font-semibold text-slate-950">
                No deployment requests found
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                Queue an environment lifecycle
                operation or change the active
                filters.
              </p>
            </div>
          ) : null}

          {deploymentRequests.length > 0 ? (
            <div className="divide-y divide-slate-200">
              {deploymentRequests.map(
                (request) => {
                  const environmentName =
                    environmentNames.get(
                      request.environment_id,
                    ) ?? request.environment_id;

                  return (
                    <article
                      key={request.id}
                      className="px-6 py-6"
                    >
                      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
                        <div>
                          <div className="flex flex-wrap items-center gap-3">
                            <h3 className="font-semibold text-slate-950">
                              {environmentName}
                            </h3>

                            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-slate-700">
                              {
                                operationLabels[
                                  request.operation
                                ]
                              }
                            </span>

                            <span
                              className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${
                                statusStyles[
                                  request.status
                                ]
                              }`}
                            >
                              {request.status}
                            </span>
                          </div>

                          <p className="mt-3 text-xs text-slate-500">
                            Request ID:{" "}
                            <span className="font-mono">
                              {request.id}
                            </span>
                          </p>
                        </div>

                        <div className="text-sm lg:text-right">
                          <p className="font-medium text-slate-700">
                            Attempt{" "}
                            {request.attempt_count}
                          </p>

                          <p className="mt-1 text-slate-500">
                            Requested{" "}
                            {formatDate(
                              request.requested_at,
                            )}
                          </p>
                        </div>
                      </div>

                      <dl className="mt-5 grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-3">
                        <div>
                          <dt className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Started
                          </dt>

                          <dd className="mt-1 text-sm text-slate-700">
                            {formatDate(
                              request.started_at,
                            )}
                          </dd>
                        </div>

                        <div>
                          <dt className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Completed
                          </dt>

                          <dd className="mt-1 text-sm text-slate-700">
                            {formatDate(
                              request.completed_at,
                            )}
                          </dd>
                        </div>

                        <div>
                          <dt className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Environment ID
                          </dt>

                          <dd className="mt-1 break-all font-mono text-xs text-slate-700">
                            {request.environment_id}
                          </dd>
                        </div>
                      </dl>

                      {request.error_message ? (
                        <div className="mt-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
                          <p className="text-xs font-semibold uppercase tracking-wider text-red-700">
                            Failure
                          </p>

                          <p className="mt-1 text-sm text-red-700">
                            {
                              request.error_message
                            }
                          </p>
                        </div>
                      ) : null}
                    </article>
                  );
                },
              )}
            </div>
          ) : null}
        </section>
      </section>
    </main>
  );
}
