# DockerMe test task

## Containers
- API Service (FastAPI)
- Outbox Consumer (Background Worker)

## Task Execution Strategy
- To prevent blocking the API:
Task execution is triggered via a domain event (TaskRan)
Events are persisted in an outbox table
A background consumer processes events asynchronously
Blocking business logic is offloaded using asyncio.to_thread

- This ensures:
The API remains responsive
Multiple tasks can be processed concurrently
Failures do not corrupt system state

## Event Handling (Outbox Pattern)
Domain events are stored in the database
Events are processed at-least-once
An event is marked as processed only after successful handling
Failed events remain unprocessed and can be retried

## Error Handling
Structured and consistent API error responses
No internal stack traces exposed to clients
Explicit domain-level exceptions
Failed task execution transitions the task to FAILED

## Running the Project
- Prerequisites:
Docker
Docker Compose

- Run with Docker:
docker compose up --build
docker compose exec -it app sh -c "alembic upgrade head"
