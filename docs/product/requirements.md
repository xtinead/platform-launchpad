# Platform Launchpad - Product Requirements Document

## 1. Overview

Platform Launchpad is a self-service internal developer platform demo application. It allows developers to request and manage application environments through a controlled web interface.

The goal of this project is to demonstrate full-stack application development and platform engineering practices, including authentication, role-based access control, CI/CD, infrastructure as code, GitOps, observability, and cloud deployment.

## 2. Problem Statement

Platform teams often need to provide developers with a safe and repeatable way to request environments without giving direct access to cloud infrastructure or Kubernetes clusters.

Platform Launchpad solves this by creating a simple self-service interface where users can request environments while platform automation handles provisioning, deployment, status tracking, and audit logging.

## 3. Goals

- Provide a simple developer portal experience.
- Support multi-user authentication.
- Support role-based access for users and admins.
- Track environment requests and lifecycle status.
- Demonstrate backend, frontend, database, worker, CI/CD, and infrastructure automation.
- Provide a portfolio-ready application that can be deployed locally, cheaply hosted, and optionally deployed to AWS.

## 4. Non-Goals

- This MVP will not provision real cloud infrastructure from the UI initially.
- This MVP will not include enterprise SSO in the first release.
- This MVP will not support billing, quotas, or advanced policy enforcement initially.
- This MVP will not replace a real enterprise internal developer platform.

## 5. User Roles

### Regular User

A regular user can:

- Register an account.
- Log in.
- Create environment requests.
- View their own environments.
- Delete or destroy their own environments.

### Admin User

An admin can:

- View all users.
- View all environments.
- Update environment status.
- Review audit logs.
- Manage environment requests.

## 6. Core Features

### Authentication

Users can sign up and log in using email and password. The backend issues JWT tokens for authenticated API access.

### Environment Requests

Users can submit a request for a new environment by providing:

- Environment name
- Environment type
- Application version
- Description

### Environment Lifecycle

Each environment moves through one of the following statuses:

- pending
- provisioning
- active
- failed
- destroyed

### Audit Logging

Important actions are recorded in audit logs, including:

- user signup
- login
- environment creation
- environment deletion
- status changes

## 7. MVP Screens

- Login
- Signup
- Dashboard
- Create Environment
- Environment Details
- Admin Dashboard
- Audit Logs

## 8. Success Criteria

The MVP is complete when:

- Users can register and log in.
- Users can create environment requests.
- Users can view only their own environments.
- Admins can view all environments.
- Environment lifecycle status is stored in PostgreSQL.
- API routes are protected by JWT authentication.
- The app runs locally with Docker Compose.
- The app has clear documentation and architecture diagrams.