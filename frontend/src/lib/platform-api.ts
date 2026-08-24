import { apiRequest } from "@/lib/api";

import type {
  DeploymentOperation,
  DeploymentRequestListResponse,
  DeploymentRequestStatus,
  EnvironmentCreateRequest,
  EnvironmentListResponse,
  EnvironmentOperationResponse,
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

export async function createDeploymentRequest(
  token: string,
  environmentId: string,
  operation: DeploymentOperation,
): Promise<EnvironmentOperationResponse> {
  return apiRequest<EnvironmentOperationResponse>(
    `/api/v1/environments/${environmentId}/deployment-requests`,
    {
      method: "POST",
      token,
      body: JSON.stringify({
        operation,
        request_payload: {},
      }),
    },
  );
}

export async function listDeploymentRequests(
  token: string,
  options: {
    page?: number;
    pageSize?: number;
    status?: DeploymentRequestStatus;
    operation?: DeploymentOperation;
  } = {},
): Promise<DeploymentRequestListResponse> {
  const {
    page = 1,
    pageSize = 100,
    status,
    operation,
  } = options;

  const searchParams = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

  if (status) {
    searchParams.set("status", status);
  }

  if (operation) {
    searchParams.set("operation", operation);
  }

  return apiRequest<DeploymentRequestListResponse>(
    `/api/v1/deployment-requests?${searchParams.toString()}`,
    {
      method: "GET",
      token,
    },
  );
}