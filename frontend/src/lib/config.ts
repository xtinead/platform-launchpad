const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export const appConfig = {
  name: "Platform Launchpad",
  description:
    "A self-service platform for managing environments and deployment workflows.",
  apiBaseUrl,
} as const;
