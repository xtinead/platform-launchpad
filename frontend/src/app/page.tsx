import Link from "next/link";

const capabilities = [
  {
    title: "Environment Management",
    description:
      "Create and manage application environments through standardized platform workflows.",
  },
  {
    title: "Deployment Automation",
    description:
      "Submit deployment requests and track their progress through the worker execution engine.",
  },
  {
    title: "Platform Visibility",
    description:
      "View environment state and deployment activity from one operational dashboard.",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-lg font-semibold text-slate-950">
              Platform Launchpad
            </p>
            <p className="text-sm text-slate-500">
              Self-Service Platform Engineering
            </p>
          </div>

          <Link
            href="/login"
            className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
          >
            Sign in
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-6 py-24">
        <div className="max-w-3xl">
          <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-blue-600">
            Internal Developer Platform
          </p>

          <h1 className="text-5xl font-bold tracking-tight text-slate-950 sm:text-6xl">
            Ship infrastructure through a standardized platform workflow.
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            Platform Launchpad provides developers with a self-service interface
            for managing environments and deployment workflows while the
            platform controls the underlying infrastructure and automation.
          </p>

          <div className="mt-10 flex gap-4">
            <Link
              href="/login"
              className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
            >
              Open Launchpad
            </Link>

            <span className="rounded-lg border border-slate-300 bg-white px-6 py-3 font-medium text-slate-600">
              AWS · Kubernetes · Terraform
            </span>
          </div>
        </div>

        <div className="mt-24 grid gap-6 md:grid-cols-3">
          {capabilities.map((capability) => (
            <article
              key={capability.title}
              className="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm"
            >
              <h2 className="text-lg font-semibold text-slate-950">
                {capability.title}
              </h2>

              <p className="mt-3 leading-7 text-slate-600">
                {capability.description}
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
