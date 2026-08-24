export type EnvironmentType =
  | "development"
  | "staging"
  | "demo";

export type EnvironmentStatus =
  | "pending"
  | "provisioning"
  | "active"
  | "failed"
  | "destroying"
  | "destroyed";

export type DeploymentOperation =
  | "provision"
  | "destroy"
  | "retry"
  | "upgrade";

export type DeploymentRequestStatus =
  | "queued"
  | "processing"
  | "succeeded"
  | "failed"
  | "cancelled";

export interface PaginationMetadata {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface EnvironmentResponse {
  id: string;
  owner_id: string;
  name: string;
  environment_type: EnvironmentType;
  application_version: string;
  description: string | null;
  status: EnvironmentStatus;
  external_url: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  destroyed_at: string | null;
}

export interface EnvironmentListResponse {
  items: EnvironmentResponse[];
  pagination: PaginationMetadata;
}

export interface EnvironmentCreateRequest {
  name: string;
  environment_type: EnvironmentType;
  application_version: string;
  description?: string | null;
}

export interface DeploymentRequestResponse {
  id: string;
  environment_id: string;
  requested_by_id: string;
  operation: DeploymentOperation;
  status: DeploymentRequestStatus;
  attempt_count: number;
  error_message: string | null;
  request_payload: Record<string, unknown>;
  requested_at: string;
  started_at: string | null;
  completed_at: string | null;
  updated_at: string;
}

export interface DeploymentRequestListResponse {
  items: DeploymentRequestResponse[];
  pagination: PaginationMetadata;
}

export type DeploymentRequestCreateRequest = {
  operation: DeploymentOperation;
  request_payload?: Record<string, unknown>;
};

export type EnvironmentOperationResponse = {
  environment: EnvironmentResponse;
  deployment_request: DeploymentRequestResponse;
};