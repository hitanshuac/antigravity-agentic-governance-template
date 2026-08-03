# ADR-0003: Adopt Groq as primary LLM provider

## Status
Accepted

## Context
Running rapid, continuous evaluation loops requires high tokens-per-second throughput and low cost, especially when scaling a template factory.

## Decision
We adopted Groq as the primary LLM provider in `SecureLLMClient` with free-tier quota management and fallback chains.

## Consequences
- High-speed inference enables near real-time PRAR cycles.
- Quota management is required to avoid rate limits on free tiers.
