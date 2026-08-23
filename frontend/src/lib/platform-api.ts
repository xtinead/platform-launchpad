import { apiRequest } from "@/lib/api";
import type {
  DeploymentRequestListResponse,
  EnvironmentCreateRequest,
  EnvironmentListResponse,
  EnvironmentResponse,
} from "@/lib/platform-types";

export async function listEnvironments(
  token: string,
): Promise<EnvironmentListResponse> {
  return apiRequest<EnvironmentListResponse>(
    "/api/v1/environments?page=1&page_size=100",
    {
      method: "GET",
      token,
    },
  );
}

export async function createEnvironment(
  token: string,
  request: EnvironmentCreateRequest,
): Promise<EnvironmentResponse> {
  return apiRequest<EnvironmentResponse>(
    "/api/v1/environments",
    {
      method: "POST",
      token,
      body: JSON.stringify(request),
    },
  );
}

export async function listDeploymentRequests(
  token: string,
): Promise<DeploymentRequestListResponse> {
  return apiRequest<DeploymentRequestListResponse>(
    "/api/v1/deployment-requests?page=1&page_size=100",
    {
      method: "GET",
      token,
    },
  );
}
