---
description: Start backend infrastructure and seed data
---

# Start Infrastructure and Seed Data

This workflow starts the backend services (Infrahub, Temporal, Neo4j, Redis, RabbitMQ) and seeds the initial schemas and device topology data.

// turbo-all

1. Start the infrastructure dependencies using the invoke task.

```bash
uv run invoke dev.deps
```

2. Wait a moment for Infrahub and Temporal to fully initialize (Infrahub needs to run migrations).

```bash
sleep 15
```

3. Load the OpsMill schemas into Infrahub.

```bash
uv run invoke backend.load-schemas
```

4. Seed the defined network topology data into Infrahub.

```bash
uv run invoke backend.seed-data
```
