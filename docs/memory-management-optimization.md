# Memory Management Optimization Spec

## Status

Draft for implementation planning.

## Context

The bot currently manages conversational memory by storing recent dialog turns in MongoDB and injecting them into every model prompt.

Relevant current flow:

- `MessageHandler.stream_get_response()` decides whether to save a message or engage.
- `AIAgent.astream()` transcribes the current message, calls `PromptManager.compose_prompt()`, and sends the composed prompt to `models_toolkit.text_model`.
- `PromptManager.compose_prompt()` builds one large user prompt from:
  - current date,
  - recent chat history from `Dialogs.get_messages()`,
  - current user input,
  - chat-wide facts,
  - facts for the initiating user,
  - introduction for the initiating user.
- `Dialogs` stores messages keyed by `chat_id` and prunes by `last_n_messages_to_store`.
- Facts and introductions are keyed by `chat_id` plus `user_handle`.

Current config:

- `last_n_messages_to_remember: 25`
- `last_n_messages_to_store: 50`

This means every engaged response pays prompt cost for the same recent history repeatedly. It also mixes all group-chat participants into one plain-text history block, which gives the model weak identity boundaries in multi-user chats.

OpenAI's current conversation-state documentation recommends the Responses API for stateful interactions, and describes two relevant mechanisms:

- `previous_response_id` for chaining a new response to a prior response without resending all previous inputs.
- Conversations API objects for durable, reusable conversation state that can be used with Responses API across sessions, devices, or jobs.

Sources:

- OpenAI conversation state guide: https://developers.openai.com/api/docs/guides/conversation-state
- Responses API reference: https://developers.openai.com/api/docs/api-reference/responses
- OpenAI Agents SDK guide: https://developers.openai.com/api/docs/guides/agents

## Problem

The current prompt-as-memory approach has four problems:

1. Cost grows with `last_n_messages_to_remember`, because the same message history is re-sent on every engaged turn.
2. Latency grows with prompt size and repeated preamble construction.
3. Multi-user identity is represented only as text labels like `@handle`, so the model can conflate participants, especially when users mention one another or reply in threads.
4. Durable facts, ephemeral chat history, and current request context are all merged into one prompt, making it hard to reason about retention, deletion, privacy, and provider migration.

## Goals

- Reduce repeated prompt tokens for recent conversation history.
- Preserve correct behavior in group chats with multiple human participants.
- Keep durable memory under project control where possible.
- Keep `/reset`, `/clearfacts`, `/introduce`, `/fact`, `/autofact`, `/conversationtracker`, and `/autoengage` semantics clear.
- Support a gradual rollout behind configuration.
- Avoid coupling the whole bot directly to one OpenAI state mechanism without an abstraction.
- Allow removing `omnimodkit` if a direct SDK or agent implementation is cleaner.
- Keep memory storage vendor-independent while allowing provider metadata for optimization.
- Implement the migration additively: expand existing models, keep the current prompt path as the default, and gate every new behavior behind config.

## Non-Goals

- Replace MongoDB as the durable source for facts, introductions, usage, chat modes, or audit history.
- Implement vector search in the first iteration.
- Change Telegram command behavior unless explicitly called out in this spec.
- Store sensitive user data in provider state when the same result can be achieved with short-lived state plus project-owned durable memory.
- Add a separate top-level memory model collection when existing dialog/fact/chat records can be extended cleanly.
- Remove the current `PromptManager`, `AIAgent`, or `omnimodkit` path in the first implementation phase.

## Additive Migration Policy

The first implementation should be additive and reversible.

Rules:

1. Existing runtime remains the default when no new config is present.
2. Existing collections are expanded with optional fields only.
3. Existing documents must remain readable without migration.
4. New memory behavior is selected by config, not by deleting current code paths.
5. New provider metadata is advisory. If it is missing, expired, or invalid, the bot falls back to local prompt memory.
6. New agent tools initially read from existing `user_facts`, `dialogs`, and `chats`; writes must preserve current command semantics.
7. No existing command should require provider state to work.
8. Cleanup and deletion commands should clear new metadata in addition to existing data, not change their user-facing meaning.

Initial feature flags:

```yaml
memory:
  enabled: false
  strategy: "legacy_prompt"
  runtime: "omnimodkit"
  facts_access: "prompt"
  provider_state: "disabled"
```

Additive rollout states:

| State | Runtime | Facts | Provider state | Purpose |
| --- | --- | --- | --- | --- |
| `legacy_prompt` | Existing `omnimodkit` path | Prompt-injected | Disabled | Current behavior |
| `expanded_prompt` | Existing path | Targeted prompt subset | Disabled | Validate identity/schema changes |
| `agent_tools_shadow` | Existing reply path plus shadow tools | Tool read simulation | Disabled | Compare tool retrieval without affecting replies |
| `agent_tools` | Agents SDK | Tool retrieval | Disabled | Move facts out of prompts |
| `hybrid_provider_state` | Agents SDK | Tool retrieval | Previous response/conversation metadata | Optimize repeated dialog tokens |

`agent_tools_shadow` should log which facts/tools would have been used, but should not alter the model request or generated response.

## Memory Types

The implementation should explicitly separate memory into these categories:

| Type | Examples | Scope | Retention | Storage |
| --- | --- | --- | --- | --- |
| Turn context | Current Telegram message, image/audio descriptions, reply target | One response | Ephemeral | Request payload |
| Short-term dialog | Recent conversational turns | Chat/thread/session | Short TTL or resettable | OpenAI state plus Mongo audit |
| Durable user facts | User preferences, RP facts, introductions | `chat_id + user_id` | Until cleared | Mongo, retrieved by tool |
| Chat configuration | Mode, language, feature flags | `chat_id` | Until changed | Mongo |
| Audit/debug history | Original Telegram/user/bot message records | `chat_id/thread_id` | Configurable | Mongo |

## Identity Model

The current implementation keys user memory by `user_handle`. This is convenient for prompts but weak as a database identity because handles can change and some Telegram users may not have public handles.

Add a canonical participant identity:

```text
participant_key = telegram:<telegram_id>
display_handle = @handle if available else first/last name fallback
```

For group chats, conversation state must not be keyed only by `chat_id`. It should account for:

- `chat_id`
- `thread_id` when present
- active chat mode
- state strategy
- optionally the initiating `participant_key` for per-user private branches

Recommended key:

```text
conversation_scope_key = chat:<chat_id>:thread:<thread_id-or-main>:mode:<mode_id>
```

Every message item sent to the model should include structured participant metadata in addition to human-readable text:

```json
{
  "participant_key": "telegram:123456",
  "display_handle": "@alice",
  "is_bot": false,
  "timestamp": "2026-06-27T12:00:00Z",
  "text": "..."
}
```

If the model wrapper cannot pass metadata directly, serialize a compact line format:

```text
[participant=telegram:123456 handle=@alice at=2026-06-27T12:00:00Z] message text
```

Durable facts should be keyed and retrieved by canonical participant identity. They should not be injected into every prompt by default. The preferred agent path is to expose facts through explicit memory tools so the model retrieves them only when needed. `user_handle` can remain as display data and a backwards-compatible lookup field.

## Agent Direction

Recommended agent choice: OpenAI Agents SDK for the main bot runtime once this project switches from simple model calls to tool-using agents.

Rationale:

- The bot owns application state, authorization, usage accounting, Telegram delivery, and memory retention.
- Facts should become application tools such as `get_user_facts`, `get_chat_participants`, `add_user_fact`, and `search_recent_dialog`, not unconditional prompt text.
- The workflow already needs orchestration: engage classification, media transcription, response type selection, fact extraction, image/audio generation, and persistence.
- The Agents SDK is a better fit than raw Responses calls when the application owns orchestration, tool execution, state, approvals, and observability.

Keep a direct Responses API adapter as a lower-level escape hatch for:

- cheap yes/no classifiers,
- simple structured extraction,
- provider-state experiments,
- fallback when the Agents SDK does not expose a needed API surface yet.

Do not build around Assistant API. Treat it as legacy for this project unless a future requirement specifically needs it.

Proposed initial agents:

- `ReplyAgent`: owns the user-visible response and can call memory/media tools.
- `EngagementAgent` or direct Responses classifier: decides whether to autoengage.
- `MemoryExtractionAgent`: extracts candidate facts after a successful response, with strict write-tool constraints.

Start with one `ReplyAgent` plus tools. Add specialist handoffs only after the single-agent version becomes hard to reason about.

## Options

### Option A: Keep Local Prompt Memory, Improve Compaction

Keep MongoDB dialog history as the source of short-term memory, but replace raw `last_n_messages_to_remember` prompt injection with a compact rolling summary plus the last few raw turns.

Implementation:

- Store a compact summary under the existing chat memory scope.
- Maintain the summary after each bot response or when token threshold is exceeded.
- Send:
  - system prompt,
  - current input,
  - compact summary,
  - last 3-6 raw messages.

Pros:

- Provider-portable.
- Full project control over data retention and deletion.
- Does not require immediate OpenAI Agents SDK adoption.

Cons:

- Still sends summary/history on every request.
- Summaries can drift.
- Does not use provider-side conversation state.

Best use:

- Immediate fallback strategy.
- Non-OpenAI providers.
- Chats where provider-side state is disabled.

### Option B: Responses API `previous_response_id`

Store the last OpenAI response ID for a conversation scope and pass it as `previous_response_id` on the next model call.

Implementation:

- Store `previous_response_id` under `chats.memory.scopes[scope].provider_metadata.openai`.
- On each engaged text response:
  - build only current message plus role/config,
  - pass `previous_response_id` if state is valid,
  - expose durable facts through tools,
  - store returned response ID as provider metadata.
- On `/reset`, clear both Mongo dialog history and provider state pointer.

Pros:

- Reduces repeated short-term history tokens.
- Smaller application change than durable Conversations API.
- Natural fit for linear chat replies.

Cons:

- A group chat is not strictly linear if multiple users interleave topics.
- Branching is tricky: a response ID chain can attach unrelated users/topics.
- Provider state retention/deletion semantics must be understood and documented.
- Requires either direct OpenAI SDK usage or an adapter that exposes response IDs and `previous_response_id`.

Best use:

- A single chat/thread timeline where all participants share context.
- Autoengage and mention responses that should continue the room conversation.

### Option C: OpenAI Conversations API

Create one provider-side conversation object per `conversation_scope_key` and pass that conversation object into Responses API calls.

Implementation:

- Store `conversation_id` under `chats.memory.scopes[scope].provider_metadata.openai`.
- Create a provider conversation when a chat/thread first engages.
- Append or rely on Responses API to persist items in that conversation.
- Store only the provider conversation ID locally, plus vendor-neutral scope metadata and retention info.

Pros:

- Designed for long-running durable state across sessions.
- Cleaner than manually chaining response IDs when many calls share one state object.
- More natural reset target than a response chain.

Cons:

- Stronger provider lock-in.
- Requires clear deletion/retention design.
- Still needs local facts and identity controls.

Best use:

- Long-lived roleplay chat sessions where provider-side persistence is acceptable.

### Option D: Hybrid Memory Manager

Introduce a project-level `MemoryManager` abstraction that supports multiple strategies:

- `local_prompt`: current behavior with compaction improvements.
- `responses_previous_id`: OpenAI state via previous response ID.
- `openai_conversation`: OpenAI Conversations API.
- `agent_tools`: agent retrieves durable memory through application tools.
- `hybrid`: provider short-term state plus local durable memory tools and local audit history.

Recommended path: implement the abstraction first, then ship `hybrid` with an OpenAI Agents SDK `ReplyAgent`, memory tools, and `responses_previous_id` or provider conversation metadata as an optimization. Keep `local_prompt` as fallback.

Pros:

- Keeps durable user memory in Mongo.
- Reduces repeated short-term prompt tokens.
- Allows controlled rollout and rollback.
- Avoids spreading provider-specific fields through handlers and prompt code.
- Makes fact access demand-driven through tools instead of prompt injection.

Cons:

- Requires more design than directly adding `previous_response_id`.
- Requires replacing or bypassing `omnimodkit` for the agent path.

## Recommended Design

Use a hybrid design:

1. Keep facts, introductions, chat modes, language, usage, permissions, and audit message storage in MongoDB.
2. Add a `MemoryManager` that prepares model context and records model outputs.
3. Add an agent/runtime adapter. The preferred implementation is OpenAI Agents SDK; a direct Responses API adapter is acceptable for small calls and fallback.
4. Fall back to local compacted memory when provider state is unavailable, expired, reset, or disabled.
5. Always inject current user identity explicitly; retrieve durable facts through tools unless a specific small fact set is required for correctness.
6. Store vendor-independent memory records locally, with optional provider metadata fields for response IDs, conversation IDs, trace IDs, token accounting, and cache hints.

High-level flow:

```text
Telegram message
  -> MessageHandler
  -> AIAgent transcribes media
  -> MemoryManager.prepare_context()
       returns instructions, current input, provider_state, fallback_history, tool context
  -> ReplyAgent or direct Responses adapter
  -> MemoryManager.record_response()
       stores provider metadata on existing dialog/scope records, audit message, summary if needed
  -> MessageHandler persists usage/facts as today
```

## Data Model Changes

Principle: prefer extending existing memory-related models over introducing parallel models. Vendor-independent fields should be first-class. Vendor-specific optimization data should live under a generic `provider_metadata` object.

### `dialogs`

Keep as audit/history storage, but add fields:

- `telegram_user_id`
- `participant_key`
- `thread_id`
- `telegram_message_id` if available from Telegram integration
- `reply_to_message_id` if available
- `scope_key`
- `memory_role`: `user`, `assistant`, `tool`, or `system_event`
- `provider_metadata`, optional object:
  - `provider`
  - `model`
  - `response_id`
  - `conversation_id`
  - `trace_id`
  - `usage`
  - `cache`

Indexes:

- `{ "scope_key": 1, "_id": -1 }`
- `{ "participant_key": 1 }`
- `{ "chat_id": 1, "thread_id": 1 }`

### `user_facts`

Add canonical identity fields while retaining handle:

- `participant_key`
- `telegram_user_id`
- `user_handle`
- `display_name`

Unique key should become:

```text
chat_id + participant_key
```

Migration should backfill `participant_key` from known `telegram_id` where possible. Existing handle-only facts can remain handle-keyed until the user appears again and can be reconciled.

Facts should also support agent-tool retrieval:

- `fact_id`
- `visibility`: initially `chat`
- `confidence`
- `source_dialog_id`
- `created_by`: `manual`, `autofact`, or `tool`
- `status`: `active`, `superseded`, or `deleted`

The agent should call tools to fetch facts instead of receiving all facts in the prompt.

### `chats`

Extend existing chat records with memory scope state instead of adding a separate top-level state collection:

```json
{
  "memory": {
    "version": 1,
    "strategy": "hybrid",
    "scopes": {
      "thread:main:mode:default": {
        "scope_key": "chat:-100:thread:main:mode:default",
        "participants": ["telegram:123", "telegram:456"],
        "last_dialog_id": "...",
        "expires_at": "2026-06-28T12:00:00Z",
        "provider_metadata": {
          "openai": {
            "strategy": "responses_previous_id",
            "model": "gpt-4o",
            "previous_response_id": "resp_...",
            "conversation_id": null,
            "trace_id": "trace_..."
          }
        },
        "summary": {
          "text": "...",
          "covered_until_dialog_id": "...",
          "updated_at": "..."
        }
      }
    }
  }
}
```

This keeps memory state vendor-neutral while allowing OpenAI-specific optimization metadata.

If embedded scope documents become too large for active group chats, split only the scope state into a collection such as `chat_memory_scopes`. That should be a scalability decision, not the default design.

### Rejected Separate Collection: `ai_conversation_states`

The first draft proposed a separate `ai_conversation_states` collection:

```json
{
  "scope_key": "chat:-100:thread:main:mode:default",
  "chat_id": -100,
  "thread_id": null,
  "mode_id": "default",
  "provider": "openai",
  "strategy": "responses_previous_id",
  "model": "gpt-4o",
  "previous_response_id": "resp_...",
  "provider_conversation_id": null,
  "participants": ["telegram:123", "telegram:456"],
  "last_dialog_id": "...",
  "expires_at": "2026-06-28T12:00:00Z",
  "created_at": "2026-06-27T12:00:00Z",
  "updated_at": "2026-06-27T12:30:00Z"
}
```

This is no longer the recommended default. It is acceptable only if chat documents become too large or update contention becomes a measurable problem.

### Rejected Separate Collection: `chat_memory_summaries`

The first draft also proposed `chat_memory_summaries`:

```json
{
  "scope_key": "chat:-100:thread:main:mode:default",
  "summary": "...",
  "covered_until_dialog_id": "...",
  "participants": ["telegram:123", "telegram:456"],
  "created_at": "...",
  "updated_at": "..."
}
```

Prefer storing summaries under the chat memory scope. Split to a separate collection only if summary size or update frequency requires it.

## Configuration

Add config under `BotConfig`:

```yaml
memory:
  enabled: false
  strategy: "hybrid"
  runtime: "openai_agents_sdk"
  provider_state: "responses_previous_id"
  provider_state_ttl_hours: 24
  fallback_last_n_messages: 6
  summary_enabled: true
  summary_token_target: 800
  facts_access: "tools"
  shadow_mode: false
```

Backward-compatible defaults:

- If `memory` is absent, use current local prompt behavior.
- If `memory.enabled` is `false`, use current local prompt behavior.
- Keep `last_n_messages_to_remember` and `last_n_messages_to_store` during migration.

## Prompt Contract

System prompt should contain stable role/config only:

- assistant role,
- chat name,
- chat mode,
- language,
- response style constraints,
- identity handling rule.

Current input should contain:

- canonical participant identity,
- display handle,
- timestamp,
- text,
- media descriptions,
- reply target if available.

Durable memory should normally be available through tools rather than a prompt block:

- `get_user_facts(participant_key | handle)`
- `get_replied_user_facts()`
- `search_chat_facts(query, participant_key?)`
- `add_user_fact(participant_key, fact, source_dialog_id)`
- `search_recent_dialog(query?, participant_key?, limit?)`

Small fact snippets may be injected only when required for correctness, for example the initiating user's own introduction in a non-agent fallback path.

Short-term dialog block should be supplied by exactly one strategy:

- provider state through `previous_response_id` or conversation ID, or
- local summary plus last raw turns.

Do not send both full local history and provider-state continuation unless recovering from a missing provider state.

## Multi-User Group Chat Behavior

The bot should distinguish:

- who sent the current message,
- who is being replied to,
- who authored each recent message,
- which durable facts belong to which participant.

Rules:

1. A room-level provider state can represent the shared chat timeline.
2. The current initiating user identity must be explicit every turn.
3. Facts must be retrieved by canonical participant identity, not by display name.
4. If two unrelated topics interleave quickly, local fallback history should prefer messages in the same Telegram thread or reply chain.
5. `/reset` resets the room/thread state, not global user facts.
6. `/clearfacts @user` clears durable facts only for that participant in the current chat.

Optional later enhancement:

- topic-aware branch keys derived from Telegram thread, reply chain, or an embedding-based topic classifier.

## API/Adapter Work

The current code uses `omnimodkit`, but this spec does not require keeping it. Prefer a direct runtime abstraction with two implementations:

- `OpenAIAgentsRuntime` for the main agent path.
- `OpenAIResponsesRuntime` for classifiers, structured extraction, and fallback simple calls.

The runtime abstraction should support:

- streaming text responses,
- structured outputs,
- tool registration and execution,
- provider response IDs,
- `previous_response_id`,
- provider conversation IDs if Conversations API is used,
- usage/cost accounting,
- tracing metadata,
- model/provider selection.

Example interface:

```python
class AgentRuntime:
    async def stream(
        self,
        instructions: str,
        input: AgentInput,
        tools: list[AgentTool],
        memory_state: MemoryState | None,
    ) -> AgentStreamResult:
        ...
```

Keep `AIAgent` or its replacement dependent on this interface rather than direct OpenAI details. Removing `omnimodkit` is acceptable if it simplifies provider-state and tool support.

## Implementation Plan

### Phase 1: Preparation

- Add `participant_key` helper from `Person.telegram_id`.
- Add `scope_key` helper from `Context`, active mode, and strategy.
- Extend `dialogs` writes with optional `participant_key`, `thread_id`, and `scope_key`.
- Extend `chats` with optional `memory.scopes`.
- Extend `user_facts` with optional canonical participant identity and tool-friendly metadata.
- Add memory config with current behavior as default.

Acceptance criteria:

- Existing tests/behavior still pass.
- Existing `/reset` still clears local dialog history.
- New fields are optional for existing documents.
- With default config, generated prompts and model calls are unchanged except for optional extra DB fields.

### Phase 2: MemoryManager with Local Fallback

- Introduce `MemoryManager.prepare_context()`.
- Wrap existing `PromptManager` behavior instead of removing it.
- Implement `legacy_prompt` strategy equivalent to current behavior.
- Add `expanded_prompt` strategy for targeted identity/history formatting.
- Add compact identity format for history lines.
- Do not introduce separate memory collections unless chat document size or update contention requires it.

Acceptance criteria:

- Generated prompt remains behaviorally equivalent in `legacy_prompt` mode.
- `expanded_prompt` current input includes canonical participant identity.
- `expanded_prompt` can be enabled independently per config.

### Phase 3: Agent Runtime and Memory Tools in Shadow Mode

- Add `AgentRuntime` interface.
- Implement `OpenAIAgentsRuntime` for the main reply path.
- Implement memory tools:
  - `get_user_facts`
  - `search_chat_facts`
  - `search_recent_dialog`
  - `add_user_fact`
- Add `agent_tools_shadow` mode that evaluates memory tool retrieval but does not alter the live reply.
- Keep direct Responses calls for engagement classification or structured extraction if simpler.

Acceptance criteria:

- Shadow mode logs which tools/facts would have been used without changing user-visible responses.
- The runtime can retrieve facts for the initiating user and replied-to user through tools.
- Tool calls enforce chat/user permissions server-side.

### Phase 4: Agent Tools Live Mode

- Enable `agent_tools` mode for selected chats/configs.
- Convert `ReplyAgent` to retrieve facts through tools.
- Keep `legacy_prompt` fallback available.

Acceptance criteria:

- Normal agent replies no longer inject all chat facts.
- Falling back to `legacy_prompt` restores current behavior.
- Fact tool failures degrade gracefully without losing the user message.

### Phase 5: Responses `previous_response_id`

- Extend model adapter to pass `previous_response_id` and capture response ID.
- Implement `responses_previous_id` strategy.
- Store/update provider metadata under `chats.memory.scopes`.
- On provider-state error, clear stale state and retry once with local fallback.

Acceptance criteria:

- Second engaged turn in the same scope sends no full local history when provider state exists.
- `/reset` clears provider state pointer.
- Failed provider continuation does not lose the user message.

### Phase 6: Fact Tool Retrieval Policy

- Remove all-chat fact injection from the normal reply path.
- Make fact tools support targeted retrieval for:
  - initiating user,
  - replied-to user,
  - explicitly mentioned handles,
  - recently active participants up to a small limit.
- Update autofact generation to use canonical participant identity.

Acceptance criteria:

- Group chats with many facts do not send unrelated fact lists.
- Facts generated for one user are not attributed to another similarly named user.

### Phase 7: Optional Conversations API

- Add `openai_conversation` strategy if product behavior and retention are acceptable.
- Implement provider conversation creation/deletion through provider metadata under `chats.memory.scopes`.
- Add explicit cleanup on `/reset` if the provider exposes deletion for the chosen object.

Acceptance criteria:

- Strategy can be switched per config.
- Local fallback remains available.

## Edge Cases

- Provider state expired: retry with local summary/history and store the new response ID.
- Bot output failed after model response: do not advance provider pointer until Telegram send succeeds, or store pending state and reconcile.
- User has no handle: use `participant_key` and display fallback.
- Handle changed: preserve identity by Telegram ID and update display handle.
- Chat mode changed: new `scope_key` so old roleplay context does not leak into new mode.
- Threaded group chat: include `thread_id` in state key.
- Autoengage classification: can use cheaper local compact context; it does not need full provider state unless quality demands it.
- Image/audio: store transcribed descriptions locally; provider state should not be the only copy.

## Privacy and Retention

- Durable facts remain local and user-clearable.
- Provider state should have a TTL and be resettable.
- Document that using provider conversation state sends short-term chat context to OpenAI for stateful continuation.
- `/reset` should clear local dialog history and provider-state references for the current scope.
- `DB.clear_user_data()` should remove canonical user facts and local dialog records; provider-side deletion must be handled if provider APIs allow targeted deletion.

## Observability

Log without message bodies:

- strategy selected,
- scope key,
- whether provider state was used,
- whether fallback was used,
- number of local fallback messages,
- provider state update success/failure,
- token/price metrics if available.

Add counters:

- `memory.provider_state.hit`
- `memory.provider_state.miss`
- `memory.provider_state.retry_fallback`
- `memory.local_prompt.messages_sent`
- `memory.tools.fact_lookup_count`
- `memory.tools.fact_write_count`
- `memory.facts.fallback_injected_count`

## Known Current-Code Issues Found During Research

- `AIAgent.astream()` sets `communication_history = None`, so the existing model wrapper history channel is intentionally unused.
- `PromptManager._compose_chat_history_prompt()` ignores its `user_input` argument and reads from DB.
- `inject_autofact()` currently calls async prompt methods without `await`:
  - `self.prompt_manager.compose_chat_facts_prompt(self.context)`
  - `self.prompt_manager.compose_user_facts_prompt(self.person, self.context)`
  This causes coroutine objects to be interpolated into the autofact prompt instead of the intended fact text.
- `Dialogs` stores only `user_handle`, not stable Telegram user IDs.
- `Dialogs.reset()` clears the whole chat by `chat_id`, not a specific thread/scope.

## Recommendation

Implement Option D in phases, starting with vendor-independent memory extensions, `MemoryManager`, and an OpenAI Agents SDK `ReplyAgent` that can retrieve facts through tools. Add `previous_response_id` or Conversations API state after the agent/tool boundary is in place.

Do not remove local dialog storage. It is still needed for audit, fallback, reset behavior, media transcription retention, provider migration, and future summarization.

Do not rely on provider state for durable user facts. Continue storing those locally, migrate identity from `user_handle` to `participant_key`, and let the agent retrieve facts on demand through server-side tools.
