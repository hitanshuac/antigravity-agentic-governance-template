---
name: Deploy to Vercel
description: "Production deployment skill for Vercel. Supports Next.js, Vite, SvelteKit, and Python serverless. Includes Vercel Postgres, KV, Blob storage, edge functions, and preview deployments. Replaces Streamlit Community Cloud for full-stack deployments. TRIGGERS: 'deploy to vercel', 'vercel deployment', 'deploy production', 'deploy app', 'deploy website', 'preview deployment', 'serverless deployment'."
---

# Deploy to Vercel

## Why Vercel Over Streamlit Cloud
- **Persistent Storage:** Vercel Postgres (256MB free), Vercel KV (Redis), Vercel Blob (file storage)
- **Any Framework:** Next.js, Vite, SvelteKit, Flask, FastAPI, static sites
- **Edge Functions:** Sub-10ms response globally
- **Preview Deployments:** Every PR gets a unique preview URL
- **Custom Domains:** Free tier supports custom domains
- **CI/CD:** Auto-deploy on push to GitHub

## Prerequisites
1. Vercel CLI must be installed: `npm i -g vercel`
2. User must be authenticated: `vercel login`
3. Project must have a `package.json` (Node.js) or `requirements.txt` (Python)

## Phase 1: Pre-Flight Checks
1. Verify Vercel CLI is installed and authenticated:
   // turbo
   `vercel whoami`
2. Verify the project has a valid entrypoint:
   - **Next.js:** `next.config.js` or `next.config.ts`
   - **Vite:** `vite.config.ts`
   - **Python:** `api/` directory with serverless functions
3. Verify environment variables are configured:
   `vercel env ls`

## Phase 2: Environment Variable Configuration
1. If the project uses API keys or secrets:
   - Ask the user for each required value
   - Inject via CLI: `vercel env add <VAR_NAME> production`
2. For local development: `vercel env pull .env.local`

## Phase 3: Deploy
1. **Preview deployment** (for testing):
   // turbo
   `vercel`
2. **Production deployment** (for release):
   // turbo
   `vercel --prod`
3. Capture the deployment URL from CLI output.

## Phase 4: Storage Setup (If Needed)
1. **Vercel Postgres:** `vercel storage create postgres <db-name>`
2. **Vercel KV (Redis):** `vercel storage create kv <store-name>`
3. **Vercel Blob:** `vercel storage create blob <store-name>`
4. Link storage to project: `vercel link`

## Phase 5: Smoke Test
1. After deployment completes, ask the user to verify the live URL.
2. Confirm that:
   - The home page loads correctly
   - API routes respond (if applicable)
   - Storage connections work (if applicable)
   - Images and assets load properly

## Phase 6: Custom Domain (Optional)
1. If the user wants a custom domain:
   `vercel domains add <domain-name>`
2. Configure DNS records as instructed by Vercel CLI output.

## Failure Handling
- If `vercel` CLI is not installed: `npm i -g vercel`
- If not authenticated: prompt user to run `vercel login`
- If build fails: check `vercel logs <deployment-url>` for error details
