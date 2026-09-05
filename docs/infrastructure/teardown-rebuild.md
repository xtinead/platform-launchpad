# Platform Launchpad — Teardown and Rebuild Runbook

## 1. Purpose

This runbook defines the controlled teardown and rebuild procedure for the
Platform Launchpad AWS development environment.

The development environment is intentionally temporary.

It exists to support:

- platform validation;
- integration testing;
- portfolio demonstrations;
- architecture evidence capture;
- recovery testing;
- interview preparation.

It is not intended to remain online continuously when no active testing or
demonstration is taking place.

The primary goals of this runbook are to:

- avoid unnecessary AWS cost;
- preserve source-controlled platform state;
- prevent accidental loss of shared or external resources;
- destroy Terraform-owned infrastructure cleanly;
- detect orphaned cost-generating resources;
- document the dependency order required for rebuild;
- validate that the platform can be reconstructed from authoritative state.

---

## 2. Environment Scope

Current environment:

```text
development
```

Primary AWS runtime account:

```text
201854077833
```

Primary region:

```text
us-east-1
```

EKS cluster:

```text
platform-launchpad-development-eks
```

Application namespace:

```text
platform-launchpad
```

Argo CD namespace:

```text
argocd
```

Public application endpoint:

```text
https://launchpad.christineadelusi.com
```

---

## 3. External Ownership Boundaries

Not every resource used by Platform Launchpad is owned by the development
Terraform state.

This distinction is critical during teardown.

### Route 53

The hosted zone for:

```text
christineadelusi.com
```

exists in a separate AWS development account.

That hosted zone must **not** be destroyed as part of the Platform Launchpad
runtime teardown.

The application DNS record:

```text
launchpad.christineadelusi.com
```

may need to be removed or updated separately after the ALB is destroyed.

### ACM

The TLS certificate used by Platform Launchpad is not currently represented as
a Terraform-owned development resource.

It must therefore be reviewed separately before teardown.

Do not assume:

```text
terraform destroy
```

will or should remove it.

### Terraform Backend

Remote Terraform state infrastructure must survive application-environment
teardown unless the explicit goal is to destroy the state backend itself.

The backend is required for future reconstruction and state inspection.

---

# Part I — Pre-Teardown

## 4. Pre-Teardown Principle

Do not begin infrastructure destruction until the development environment has
been fully documented and the current source-controlled state has been pushed.

The preferred lifecycle is:

```text
Build
    |
    v
Validate
    |
    v
Document
    |
    v
Capture Evidence
    |
    v
Tag Release
    |
    v
Destroy
```

---

## 5. Verify Main Repository Status

From:

```bash
cd /c/apps/platform-launchpad
```

run:

```bash
git status --short
```

Before final teardown, all intended changes should be:

- reviewed;
- committed;
- pushed.

Confirm:

```bash
git status
```

eventually reports a clean working tree.

---

## 6. Verify GitOps Repository Status

Run:

```bash
cd /c/apps/platform-launchpad-gitops
git status --short
```

The GitOps repository should also be clean and pushed before teardown.

Confirm:

```bash
git log -3 --oneline
```

and verify the expected release state exists on:

```text
origin/main
```

---

## 7. Verify Terraform Drift

Return to:

```bash
cd /c/apps/platform-launchpad/terraform/environments/development
```

run:

```bash
terraform plan
```

The preferred pre-destroy state is:

```text
No changes. Your infrastructure matches the configuration.
```

This establishes that Terraform understands the environment before
destruction begins.

Unexpected drift should be resolved before proceeding.

---

## 8. Record Terraform Outputs

Capture current outputs for troubleshooting and portfolio evidence:

```bash
terraform output
```

Optionally save them locally:

```bash
terraform output \
  > /tmp/platform-launchpad-development-outputs.txt
```

Do not commit output files containing sensitive values.

---

## 9. Verify AWS Identity

Before any destructive AWS operation:

```bash
aws sts get-caller-identity \
  --query '{Account:Account,Arn:Arn}' \
  --output table
```

Expected runtime account:

```text
201854077833
```

If the account does not match, stop.

Do not perform a destroy from an unintended AWS account.

---

## 10. Verify Kubernetes Context

Run:

```bash
kubectl config current-context
```

Then:

```bash
kubectl get nodes
```

Confirm the active cluster is the Platform Launchpad development cluster.

---

## 11. Capture Argo CD Evidence

Run:

```bash
kubectl get applications \
  -n argocd
```

Expected:

```text
aws-load-balancer-controller-development   Synced   Healthy
platform-launchpad-development             Synced   Healthy
```

Capture screenshots of the Argo CD UI before teardown.

Recommended screenshots:

- Applications overview;
- Platform Launchpad resource graph;
- application `Synced`;
- application `Healthy`;
- database migration Sync hook if visible.

---

## 12. Capture Kubernetes Evidence

Run:

```bash
kubectl get pods \
  -n platform-launchpad \
  -o wide
```

Then:

```bash
kubectl get deployments \
  -n platform-launchpad
```

Capture evidence showing:

```text
backend
frontend
worker
```

healthy and available.

---

## 13. Capture Public HTTPS Evidence

Run:

```bash
curl -I \
  http://launchpad.christineadelusi.com/
```

Expected:

```text
301 Moved Permanently
```

Then:

```bash
curl -I \
  https://launchpad.christineadelusi.com/
```

Expected:

```text
HTTP/2 200
```

---

## 14. Capture Backend Health Evidence

Run:

```bash
curl -sS \
  https://launchpad.christineadelusi.com/health/live
```

Then:

```bash
curl -sS \
  https://launchpad.christineadelusi.com/health/ready
```

Expected readiness:

```json
{
  "status": "ready",
  "checks": {
    "database": "ok"
  }
}
```

---

## 15. Capture Worker Evidence

Run:

```bash
kubectl logs \
  -n platform-launchpad \
  deployment/worker \
  --tail=100
```

Preserve evidence showing successful deployment-request processing.

Example:

```text
Processed deployment request <id> with status succeeded.
```

---

## 16. Capture Backend Workflow Evidence

Run:

```bash
kubectl logs \
  -n platform-launchpad \
  deployment/backend \
  --tail=100
```

Useful evidence includes:

```text
POST .../deployment-requests ... 202 Accepted
```

and successful API requests.

---

## 17. Verify Database Migration Version

Run:

```bash
kubectl exec \
  -n platform-launchpad \
  deployment/backend \
  -- alembic current
```

Confirm the expected migration head is applied.

---

## 18. Verify Argo CD Migration Hook

Run:

```bash
kubectl get application \
  platform-launchpad-development \
  -n argocd \
  -o json \
| python -c "
import json, sys

app = json.load(sys.stdin)

resources = (
    app.get('status', {})
       .get('operationState', {})
       .get('syncResult', {})
       .get('resources', [])
)

for resource in resources:
    if resource.get('kind') == 'Job':
        print(json.dumps(resource, indent=2))
"
```

Expected migration hook status should include:

```text
hookPhase: Succeeded
hookType: Sync
```

---

# Part II — Data Preservation

## 19. Decide Whether Database Data Must Be Preserved

Before destroy, decide whether the development RDS data is:

```text
Disposable
```

or:

```text
Required for future reconstruction
```

For a portfolio development environment, application data may be disposable.

However, this decision must be explicit.

---

## 20. Optional RDS Snapshot

If the data should survive teardown, create an RDS snapshot before destroying
the instance.

First identify the DB instance:

```bash
terraform output
```

or:

```bash
aws rds describe-db-instances \
  --region us-east-1 \
  --query 'DBInstances[].DBInstanceIdentifier' \
  --output table
```

Then create a manual snapshot using an intentionally named snapshot identifier.

Example pattern:

```text
platform-launchpad-development-pre-teardown-YYYYMMDD
```

Verify completion before continuing.

Do not create snapshots unnecessarily if the goal is to minimize long-term
storage cost and the data has no recovery value.

---

## 21. ECR Artifact Retention Decision

Review application images before destroy.

List repositories:

```bash
aws ecr describe-repositories \
  --region us-east-1 \
  --query 'repositories[].repositoryName' \
  --output table
```

Important repositories include:

```text
platform-launchpad-development-application
platform-launchpad-development-aws-load-balancer-controller
platform-launchpad-development-argocd
platform-launchpad-development-argocd-dex
platform-launchpad-development-argocd-redis
```

If Terraform destroys these repositories, mirrored bootstrap and application
images may also disappear depending on repository deletion configuration.

Before destroy, decide whether:

- rebuilding images is acceptable;
- bootstrap images should be mirrored again;
- a release artifact should be retained elsewhere.

The bootstrap process is designed to repopulate missing Argo CD images.

---

# Part III — Destroy Planning

## 22. Do Not Run Destroy Blindly

Before executing:

```bash
terraform destroy
```

generate and inspect a destroy plan.

Preferred:

```bash
terraform plan \
  -destroy \
  -out=platform-launchpad-development-destroy.tfplan
```

Then inspect:

```bash
terraform show \
  platform-launchpad-development-destroy.tfplan
```

---

## 23. Review Destroy Scope

Confirm the plan targets Platform Launchpad development resources.

Expected categories may include:

- EKS;
- managed node group;
- VPC;
- subnets;
- NAT Gateway;
- Elastic IP;
- route tables;
- RDS;
- Redis;
- security groups;
- VPC endpoints;
- IAM resources;
- Pod Identity associations;
- ECR repositories;
- Secrets Manager resources.

Stop if the plan includes an unrelated shared resource.

---

## 24. Confirm External Resources Are Not Included

The destroy plan should not unexpectedly destroy:

- shared Route 53 hosted zone;
- unrelated DNS records;
- shared ACM certificates;
- Terraform backend infrastructure;
- unrelated AWS resources.

If any appear, stop and resolve ownership first.

---

# Part IV — GitOps and Load Balancer Considerations

## 25. Why Kubernetes Resources Matter During Destroy

The AWS Load Balancer Controller creates AWS resources from Kubernetes
Ingress objects.

If EKS disappears before controller-managed AWS resources are cleaned up,
orphaned ALB resources may remain.

Therefore, controller-managed resources should be reviewed before cluster
destruction.

---

## 26. Inspect Current Ingress

Run:

```bash
kubectl get ingress \
  -A
```

For Platform Launchpad:

```bash
kubectl get ingress \
  platform-launchpad \
  -n platform-launchpad
```

Record the ALB hostname if needed.

---

## 27. Inspect ALBs

Run:

```bash
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[].{
    Name:LoadBalancerName,
    DNS:DNSName,
    State:State.Code
  }' \
  --output table
```

Identify the Platform Launchpad load balancer.

---

## 28. Application Removal Strategy

The safest teardown strategy should account for GitOps-managed AWS
load-balancer resources.

Before destroying EKS, it may be appropriate to remove or delete the
application Ingress so the AWS Load Balancer Controller can cleanly delete its
ALB resources.

This step should be performed deliberately and validated before continuing.

Do not remove GitOps state from Git merely to destroy the temporary runtime.

Git remains authoritative for future rebuild.

Runtime resources can be deleted from the cluster while keeping their desired
state in Git for reconstruction.

---

## 29. Validate ALB Cleanup

After the Ingress is removed from the runtime, verify the Platform Launchpad
ALB has been deleted before destroying the cluster.

Use:

```bash
aws elbv2 describe-load-balancers \
  --region us-east-1
```

Do not assume Kubernetes object deletion immediately means the AWS ALB has
finished deleting.

---

# Part V — Terraform Destroy

## 30. Execute the Saved Destroy Plan

Once the destroy plan has been reviewed:

```bash
terraform apply \
  platform-launchpad-development-destroy.tfplan
```

Using the saved plan ensures the executed actions match the reviewed plan.

---

## 31. Monitor Destroy

Terraform may take time to remove:

- EKS node groups;
- EKS control plane;
- RDS;
- Redis;
- NAT Gateway;
- VPC endpoints;
- networking resources.

Do not interrupt the process unless necessary.

---

## 32. Destroy Failure Handling

If Terraform fails during destroy:

1. read the exact resource failure;
2. do not randomly delete dependencies;
3. inspect AWS state;
4. inspect Terraform state;
5. resolve the dependency;
6. rerun `terraform plan -destroy`;
7. continue through Terraform.

Manual deletion should be a controlled recovery action, not the default.

---

# Part VI — Post-Destroy Validation

## 33. Terraform State Check

After successful destruction:

```bash
terraform state list
```

Review what remains.

Environment resources expected to be destroyed should no longer appear.

Some intentionally persistent resources may remain if they are designed to
survive environment destruction.

---

## 34. Terraform Plan Check

Run:

```bash
terraform plan
```

After a full environment destroy, Terraform should propose recreation of the
environment.

That is expected.

This validates that the configuration still describes the complete platform.

---

## 35. Check EKS

Run:

```bash
aws eks list-clusters \
  --region us-east-1
```

Confirm:

```text
platform-launchpad-development-eks
```

is gone.

---

## 36. Check EC2 Worker Instances

Run:

```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --filters \
    Name=instance-state-name,Values=pending,running,stopping,stopped \
  --query 'Reservations[].Instances[].{
    InstanceId:InstanceId,
    State:State.Name,
    Name:Tags[?Key==`Name`]|[0].Value
  }' \
  --output table
```

Confirm Platform Launchpad worker nodes are not left running.

---

## 37. Check Load Balancers

Run:

```bash
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[].{
    Name:LoadBalancerName,
    DNS:DNSName,
    State:State.Code
  }' \
  --output table
```

Confirm the Platform Launchpad ALB is gone.

---

## 38. Check NAT Gateways

Run:

```bash
aws ec2 describe-nat-gateways \
  --region us-east-1 \
  --filter Name=state,Values=available,pending,deleting \
  --query 'NatGateways[].{
    Id:NatGatewayId,
    State:State,
    VpcId:VpcId
  }' \
  --output table
```

Confirm no Platform Launchpad NAT Gateway remains.

NAT is an important cost check.

---

## 39. Check Elastic IPs

Run:

```bash
aws ec2 describe-addresses \
  --region us-east-1 \
  --query 'Addresses[].{
    AllocationId:AllocationId,
    PublicIp:PublicIp,
    AssociationId:AssociationId
  }' \
  --output table
```

Confirm there is no unused Platform Launchpad Elastic IP left unintentionally.

---

## 40. Check RDS

Run:

```bash
aws rds describe-db-instances \
  --region us-east-1 \
  --query 'DBInstances[].{
    Identifier:DBInstanceIdentifier,
    Status:DBInstanceStatus
  }' \
  --output table
```

Confirm the development database is removed unless intentionally retained.

---

## 41. Check Redis

Run:

```bash
aws elasticache describe-replication-groups \
  --region us-east-1 \
  --query 'ReplicationGroups[].{
    Id:ReplicationGroupId,
    Status:Status
  }' \
  --output table
```

Confirm the development Redis resource is removed unless intentionally
retained.

---

## 42. Check VPC Endpoints

Run:

```bash
aws ec2 describe-vpc-endpoints \
  --region us-east-1 \
  --query 'VpcEndpoints[].{
    Id:VpcEndpointId,
    Service:ServiceName,
    State:State,
    VpcId:VpcId
  }' \
  --output table
```

Confirm Platform Launchpad interface endpoints are gone.

Interface endpoints can generate ongoing hourly cost.

---

## 43. Check ECR

Run:

```bash
aws ecr describe-repositories \
  --region us-east-1 \
  --query 'repositories[].repositoryName' \
  --output table
```

Confirm repository retention matches the teardown decision.

Do not assume ECR repositories should always survive.

---

## 44. Check Secrets Manager

Run:

```bash
aws secretsmanager list-secrets \
  --region us-east-1 \
  --query 'SecretList[].{
    Name:Name,
    ARN:ARN
  }' \
  --output table
```

Confirm temporary Platform Launchpad runtime secrets are removed or
intentionally retained.

Remember that Secrets Manager deletion may use a recovery window.

---

# Part VII — DNS After Destroy

## 45. Application DNS Record

After the ALB is destroyed, the record:

```text
launchpad.christineadelusi.com
```

should not remain indefinitely pointing to a nonexistent ALB.

Because DNS is in a separate account, this may require:

```text
--profile development
```

or whichever profile owns the hosted zone.

The hosted zone itself must remain.

---

## 46. ACM Certificate After Destroy

The ACM certificate may remain intentionally.

Reasons to retain it include:

- future rebuild;
- no meaningful ongoing certificate charge;
- avoiding unnecessary revalidation.

Do not delete it automatically merely because the application environment is
offline.

Ownership should remain documented.

---

# Part VIII — Rebuild

## 47. Rebuild Preconditions

Before rebuilding, confirm:

- main repository is available;
- GitOps repository is available;
- Terraform remote state/backend is available;
- AWS credentials are valid;
- Docker is available;
- Terraform is available;
- AWS CLI is available;
- kubectl is available;
- Python is available;
- GitHub access is available.

---

## 48. Verify AWS Identity Before Rebuild

Run:

```bash
aws sts get-caller-identity \
  --query '{Account:Account,Arn:Arn}' \
  --output table
```

Confirm the intended runtime AWS account.

---

## 49. Initialize Terraform

From:

```bash
cd /c/apps/platform-launchpad/terraform/environments/development
```

run:

```bash
terraform init
```

Then:

```bash
terraform validate
```

---

## 50. Generate Rebuild Plan

Run:

```bash
terraform plan \
  -out=platform-launchpad-development-rebuild.tfplan
```

Review:

```bash
terraform show \
  platform-launchpad-development-rebuild.tfplan
```

Confirm resources match the intended development architecture.

---

## 51. Apply AWS Foundation

Run:

```bash
terraform apply \
  platform-launchpad-development-rebuild.tfplan
```

Terraform recreates the AWS foundation, including appropriate:

- networking;
- EKS;
- IAM;
- Pod Identity;
- ECR;
- RDS;
- Redis;
- Secrets Manager;
- VPC endpoints;
- NAT;
- security groups.

---

## 52. Validate Terraform After Rebuild

Run:

```bash
terraform plan
```

Expected:

```text
No changes. Your infrastructure matches the configuration.
```

---

## 53. Update Kubernetes Access

The Argo CD bootstrap performs kubeconfig setup, but manual verification may
also be useful.

Run:

```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name platform-launchpad-development-eks
```

Then:

```bash
kubectl get nodes
```

---

## 54. Bootstrap Argo CD

From:

```bash
cd /c/apps/platform-launchpad
```

run:

```bash
./bootstrap/argocd/install.sh
```

The bootstrap will:

- read Terraform outputs;
- validate prerequisites;
- authenticate to private ECR;
- mirror missing pinned images;
- download the pinned Argo CD manifest;
- rewrite image references;
- install Argo CD;
- wait for readiness;
- validate runtime image sources.

---

## 55. Apply GitOps Applications

Run:

```bash
./bootstrap/argocd/apply-applications.sh
```

Expected Applications:

```text
aws-load-balancer-controller-development
platform-launchpad-development
```

---

## 56. Verify Argo CD

Run:

```bash
kubectl get applications \
  -n argocd
```

Target:

```text
Synced
Healthy
```

If manual sync is required by the configured sync policy, initiate the
approved synchronization and wait for completion.

---

## 57. Verify Migration Hook

Confirm the database migration Job succeeds during the application sync.

Inspect:

```bash
kubectl get application \
  platform-launchpad-development \
  -n argocd \
  -o json
```

The migration hook should report:

```text
Succeeded
```

---

## 58. Verify Application Pods

Run:

```bash
kubectl get pods \
  -n platform-launchpad
```

Target:

```text
backend     1/1 Running
frontend    1/1 Running
worker      1/1 Running
```

---

## 59. Restore or Create DNS Record

A newly rebuilt ALB may receive a different AWS DNS hostname.

Retrieve:

```bash
kubectl get ingress \
  platform-launchpad \
  -n platform-launchpad
```

Update the external Route 53 record in the DNS-owning account if required.

Do not assume the previous ALB hostname survives rebuild.

---

## 60. Verify HTTPS

Once DNS resolves:

```bash
curl -I \
  http://launchpad.christineadelusi.com/
```

Expected:

```text
301
```

Then:

```bash
curl -I \
  https://launchpad.christineadelusi.com/
```

Expected:

```text
HTTP/2 200
```

---

## 61. Verify Backend Readiness

Run:

```bash
curl -sS \
  https://launchpad.christineadelusi.com/health/ready
```

Expected:

```json
{
  "status": "ready",
  "checks": {
    "database": "ok"
  }
}
```

---

## 62. Verify Worker

Run:

```bash
kubectl logs \
  -n platform-launchpad \
  deployment/worker \
  --tail=50
```

Confirm normal worker startup.

---

## 63. Rebuild Acceptance Test

After infrastructure recovery, perform an application-level test.

Recommended:

1. access Platform Launchpad;
2. authenticate;
3. create or select an environment;
4. submit a deployment request;
5. confirm API acceptance;
6. confirm worker processing;
7. confirm status reaches `succeeded`;
8. verify Argo CD remains healthy.

This proves the rebuild restored application behavior rather than merely
recreating infrastructure.

---

# Part IX — Recovery Failure Scenarios

## 64. Argo CD Image Missing

If an Argo CD bootstrap image is missing from ECR, the bootstrap should mirror
it again from the pinned upstream version.

Do not manually modify the installed Argo CD manifest to use an arbitrary
newer version.

---

## 65. GitOps Application OutOfSync

If an Application reports:

```text
OutOfSync
```

inspect the difference.

Do not immediately force changes without determining whether:

- Git is wrong;
- cluster state is stale;
- a manual runtime modification occurred;
- a sync hook failed.

---

## 66. Migration Failure After Rebuild

If the migration hook fails:

1. inspect Argo CD operation state;
2. inspect migration logs;
3. validate database connectivity;
4. validate secrets;
5. validate migration chain;
6. correct the cause;
7. rerun controlled synchronization.

Do not bypass the migration hook simply to make application pods start.

---

## 67. Secret Mount Failure

If workloads fail to mount secrets:

Check:

```bash
kubectl describe pod \
  <pod> \
  -n platform-launchpad
```

Then verify:

- SecretProviderClass;
- Secrets Store CSI components;
- EKS Pod Identity;
- IAM policy;
- Secrets Manager secret;
- AWS region.

---

## 68. ALB Not Created

If the Ingress exists but no ALB appears, inspect:

```bash
kubectl describe ingress \
  platform-launchpad \
  -n platform-launchpad
```

Then:

```bash
kubectl logs \
  -n kube-system \
  deployment/aws-load-balancer-controller \
  --tail=100
```

Verify the controller Application is:

```text
Synced
Healthy
```

---

# Part X — Cost Validation

## 69. Highest-Priority Post-Destroy Cost Checks

After teardown, verify these first:

1. EKS control plane
2. EC2 worker nodes
3. NAT Gateway
4. RDS
5. ElastiCache Redis
6. ALB
7. interface VPC endpoints

These are among the most important ongoing development cost sources.

---

## 70. Resources That May Intentionally Remain

Depending on the teardown strategy, the following may remain:

- Terraform state backend;
- Git repositories;
- ACM certificate;
- Route 53 hosted zone;
- selected DNS records;
- selected ECR artifacts;
- manual RDS snapshot;
- documentation.

Their retention must be intentional.

---

# Part XI — Portfolio Evidence

## 71. Recommended Evidence Before Destroy

Capture at minimum:

### Application

```text
Platform Launchpad dashboard
Successful deployment request
```

### Argo CD

```text
Applications overview
Synced / Healthy
Resource graph
Migration hook
```

### Kubernetes

```text
backend/frontend/worker Running
```

### Terraform

```text
No changes. Your infrastructure matches the configuration.
```

### HTTPS

```text
HTTP -> 301
HTTPS -> 200
```

### Worker

```text
Processed deployment request ... succeeded
```

---

## 72. Evidence Storage

Portfolio screenshots should be stored in an appropriate documentation
directory rather than scattered in the repository root.

Recommended structure:

```text
docs/
└── screenshots/
    ├── application/
    ├── argocd/
    ├── kubernetes/
    └── infrastructure/
```

Do not include screenshots containing:

- passwords;
- JWTs;
- access keys;
- secret values;
- connection strings;
- sensitive account details.

---

# Part XII — Release and Teardown Gate

## 73. Release Gate

Do not tear down until all of the following are complete:

```text
[ ] README updated
[ ] architecture documentation updated
[ ] Terraform documentation updated
[ ] security documentation updated
[ ] CI/CD documentation updated
[ ] observability documentation updated
[ ] case study completed
[ ] teardown/rebuild runbook completed
[ ] screenshots captured
[ ] main repository clean
[ ] GitOps repository clean
[ ] changes pushed
[ ] release tag created
[ ] Terraform zero drift captured
[ ] Argo CD health captured
[ ] end-to-end workflow captured
```

---

## 74. Destroy Approval Gate

Immediately before destruction, answer:

```text
Are all portfolio artifacts captured?
Are all commits pushed?
Is the GitOps repository pushed?
Is Terraform state safe?
Is database data disposable or preserved?
Are external DNS resources identified?
Are external ACM resources identified?
Has the destroy plan been reviewed?
```

Only then proceed.

---

# Part XIII — Rebuild Success Criteria

## 75. Infrastructure Criteria

A successful rebuild requires:

```text
Terraform zero drift
EKS available
worker nodes Ready
RDS available
Redis available
required ECR repositories available
Pod Identity associations available
Secrets available
VPC endpoints available
```

---

## 76. Platform Criteria

A successful rebuild requires:

```text
Argo CD Running
AWS Load Balancer Controller Running
Argo CD Applications Synced
Argo CD Applications Healthy
migration hook Succeeded
```

---

## 77. Application Criteria

A successful rebuild requires:

```text
frontend Running
backend Running
worker Running
HTTPS 200
database readiness ok
deployment request succeeds
worker processes request
```

---

## 78. Final Principle

The success of Platform Launchpad is not defined by keeping the development
environment running forever.

The stronger platform-engineering outcome is:

```text
The environment can be destroyed safely
and recreated predictably.
```

The authoritative state is distributed intentionally across:

```text
Terraform
Git
GitOps
Private Artifacts
Secrets Manager
Documented External Dependencies
```

rather than undocumented manual AWS configuration.

---

## 79. Summary

The Platform Launchpad teardown/rebuild lifecycle is:

```text
Validate
    |
    v
Capture Evidence
    |
    v
Commit and Tag
    |
    v
Review Destroy Plan
    |
    v
Clean Controller-Managed Resources
    |
    v
Terraform Destroy
    |
    v
Post-Destroy Cost Audit
    |
    v
Environment Offline
```

When the environment is needed again:

```text
Terraform Apply
    |
    v
Argo CD Bootstrap
    |
    v
GitOps Application Bootstrap
    |
    v
Argo CD Reconciliation
    |
    v
Database Migration
    |
    v
DNS Validation
    |
    v
HTTPS Validation
    |
    v
End-to-End Acceptance Test
```

This process makes cost control, disaster recovery, and platform
reproducibility part of the same operational design.