import type { Metadata } from "next";
import { Suspense } from "react";

import LoginForm from "@/app/login/login-form";

export const metadata: Metadata = {
  title: "Sign In",
};

function LoginFallback() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <p className="text-sm text-slate-500">
        Loading Platform Launchpad...
      </p>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginFallback />}>
      <LoginForm />
    </Suspense>
  );
}
