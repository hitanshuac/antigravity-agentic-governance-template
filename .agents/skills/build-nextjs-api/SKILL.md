---
name: Build Next.js API Routes
description: "Scaffold production-grade Next.js API routes for Vercel deployment. Zero-config serverless with edge runtime, middleware, and type-safe validation. TRIGGERS: 'build api', 'next.js api', 'api routes', 'serverless api', 'edge api', 'build backend'."
---

# Build Next.js API Routes

Scaffold production-grade API routes optimized for Vercel serverless/edge deployment with TypeScript and Zod validation.

## Pre-Conditions
1. The Product Templates in `.agents/product/templates/` MUST be populated. Specifically:
   - `02_TAD.md` (component architecture and data flow)
   - `03_SECURITY.md` (authentication strategy, RBAC)
   - `04_FRONTEND.md` (API contracts)
2. The agent must reference `.agents/rules/20-phase-execute.md` for security constraints.

## Phase 1: Route Design
1. Read `04_FRONTEND.md` § API Contracts to understand the expected endpoints.
2. Read `03_SECURITY.md` to understand the authentication strategy.
3. Design the route structure following Next.js App Router conventions:
   - `app/api/<resource>/route.ts` for REST endpoints
   - `app/api/<resource>/[id]/route.ts` for parameterized routes

## Phase 2: Route Construction
1. Build route handlers in `app/api/`:
   ```typescript
   import { NextRequest, NextResponse } from 'next/server';
   import { z } from 'zod';

   const RequestSchema = z.object({ /* ... */ });

   export async function POST(request: NextRequest) {
     const body = RequestSchema.parse(await request.json());
     // Implementation
     return NextResponse.json({ data });
   }
   ```
2. Use Zod schemas for all request/response validation (TypeScript equivalent of Pydantic).
3. Use Edge Runtime for latency-sensitive endpoints:
   ```typescript
   export const runtime = 'edge';
   ```

## Phase 3: Middleware & Security
1. Create `middleware.ts` at project root for auth and rate limiting.
2. Ensure all secrets are loaded via `process.env` per 12-Factor Factor III.
3. Apply CORS headers, rate limiting, and input sanitization.

## Phase 4: Testing
1. Execute `@.agents/skills/test-engineering/SKILL.md` to generate tests.
2. Use `vitest` or `jest` for unit/integration testing.
3. All tests must pass before handing back to the user.

## When to Use FastAPI Instead
If the project is Python-heavy (data engineering, ML, DuckDB), use
`@.agents/skills/build-fastapi/SKILL.md` instead. This skill is for
JavaScript/TypeScript full-stack projects deploying to Vercel.
