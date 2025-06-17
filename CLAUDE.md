# CLAUDE.md - Kairos BCP

<meta>
role: FastAPI+Next.js+PostgreSQL specialist | Docker orchestration expert
context: PKM system | successful rewrite | production-ready
constraints: Python 3.11+ | TypeScript strict | async-first | type-safe
</meta>

## 🚨 CRITICAL: Context7 Usage Required

<context7_mandate>
**NEVER write code using cached knowledge. ALWAYS use context7 for:**
- Framework APIs (FastAPI, Next.js, Shadcn/ui, React)
- Library methods (SQLAlchemy, Pydantic, Zod, React Hook Form)
- Database patterns (PostgreSQL, pgvector, Alembic)
- Any third-party dependency

**Usage**: Append `use context7` to ANY coding request:
```
"Create a FastAPI endpoint with pagination use context7"
"Build Shadcn/ui data table component use context7"
"Write SQLAlchemy query with joins use context7"
```

**Setup** (if not configured):
```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
```

**Why**: Prevents deprecated APIs, ensures latest patterns, reduces debugging time by 80%
</context7_mandate>

## Core Commands
```bash
# Single source of truth - no repetition
env:    docker-compose up -d && docker-compose logs -f [service]
be:     docker-compose exec backend [cmd]  # alembic/pytest/black
fe:     docker-compose exec frontend [cmd] # npm run build/lint/test
db:     docker-compose exec postgres psql -U kairos -d kairos
urls:   3000:frontend | 8000:api/docs | 8080:pgadmin
```

## Architecture DNA
```yaml
backend:  api/v1/* → models/* → schemas/* → core/*
frontend: app/* → components/* → hooks/* → lib/*
patterns: async-sqlalchemy-2.0 | pydantic-v2 | shadcn-ui | jwt-auth
quality:  type-hints | error-handling | test-coverage>90%
```

## Parallel Execution Matrix

<subagent_orchestration>
```
ALWAYS_PARALLEL:
├── Multi-Stack Research: BE + FE + DB + DevOps (all with context7)
├── Feature Implementation: API + UI + Tests + Docs (context7 required)
├── Architecture Analysis: Security + Performance + Scale (use context7)
└── Problem Debugging: Layer1 + Layer2 + Layer3 + Root (context7 for each)

ORCHESTRATION_PATTERNS:
├── Boomerang: spawn(specialist + context7) → collect(results) → synthesize
├── Pipeline: task1|context7 → task2|context7 → task3|context7 > integrate
├── Fork-Join: parallel(independent + context7) → barrier → merge
└── Cascade: trigger(event) → spawn(reactive_agents with context7)

CONTEXT_ISOLATION:
├── Fresh Context: /clear between different domains
├── Worktree Isolation: git worktree add -b feature-x
├── Test Constraints: TDD to prevent hardcoding
├── Documentation First: Always context7 before implementation
└── Result Validation: cross-check between agents using current docs
```
</subagent_orchestration>

## Execution Pipelines

<pipeline name="feature_implementation">
```bash
# Parallel Phase (spawn 4 agents) - ALL WITH context7
agent1: "Research FastAPI patterns for {feature} with pagination, filtering, auth use context7"
agent2: "Design Next.js components for {feature} with Shadcn/ui, forms, state use context7"  
agent3: "Create PostgreSQL schema for {feature} with indexes, constraints use context7"
agent4: "Write comprehensive tests for {feature} - unit, integration, e2e use context7"

# Synthesis Phase
integrate: "Merge all agent outputs ensuring consistency and type safety"
validate: "Run full test suite and type checking"
document: "Update API docs and component stories"
```
</pipeline>

<pipeline name="code_development">
```bash
# ALWAYS start with documentation lookup
context_gather: "Fetch latest docs for {frameworks} use context7"
implement: "Write code following retrieved patterns use context7"
review: "Verify against official docs use context7"
```
</pipeline>

<pipeline name="performance_optimization">
```bash
# Analysis Phase (parallel)
profile: "Identify bottlenecks using profiler output"
query: "Analyze SQL performance with EXPLAIN ANALYZE use context7"
bundle: "Check frontend bundle size and optimization techniques use context7"
cache: "Review caching strategy best practices use context7"

# Optimization Phase (sequential)
implement: "Apply optimizations based on analysis"
measure: "Compare before/after metrics"
rollback: "Revert if regression detected"
```
</pipeline>

## Code Templates (Ultra-Concise)

<templates>
```python
# API Pattern - ALWAYS check latest FastAPI docs first with context7
# "Show me current FastAPI dependency injection patterns use context7"
@router.post("/", response_model=Response)
async def create(data: Create, db: AsyncSession = Depends(get_async_session)):
    async with db.begin():
        entity = Model(**data.dict())
        db.add(entity)
        await db.flush()
        return entity

# Query Pattern - Verify SQLAlchemy 2.0 loading strategies with context7
# "What are the latest SQLAlchemy relationship loading options use context7"
stmt = select(Model).options(
    selectinload(Model.collection),  # 1-to-many
    joinedload(Model.single)         # many-to-1
).where(Model.active == True)
```

```typescript
// Component Pattern - Get latest Shadcn/ui patterns with context7
// "Show current Shadcn/ui form component patterns use context7"
const schema = z.object({ field: z.string().min(1) });
type FormData = z.infer<typeof schema>;

export function Component() {
  const form = useForm<FormData>({ resolver: zodResolver(schema) });
  const onSubmit = async (data: FormData) => {
    try {
      await api.post('/endpoint', data);
      toast.success('Created');
    } catch { toast.error('Failed'); }
  };
}
```
</templates>

## Workflow Acceleration

<task_delegation>
```yaml
complex_feature:
  trigger: "Implement {feature} with full CRUD, search, and real-time updates"
  decompose:
    - research: "Find best practices for real-time in FastAPI + Next.js use context7"
    - design: "Create API schema and component architecture use context7"
    - implement: "Build backend endpoints with WebSocket support use context7"
    - frontend: "Create responsive UI with optimistic updates use context7"
    - test: "Write comprehensive test suite with latest testing patterns use context7"
  coordinate: "Ensure WebSocket protocol consistency across stack"

architecture_decision:
  trigger: "Evaluate replacing {current_tech} with {new_tech}"
  parallel:
    - technical: "Compare performance, features, compatibility use context7"
    - migration: "Design migration path with latest patterns use context7"
    - risk: "Identify breaking changes using current docs use context7"
    - team: "Assess learning curve with official documentation"
  synthesize: "Create decision matrix with recommendations"

quick_implementation:
  before_coding: "Fetch latest {library} documentation use context7"
  during_coding: "Verify API usage against docs use context7"
  after_coding: "Validate patterns match current best practices use context7"
```
</task_delegation>

## Context Management

<context_preservation>
```bash
# Prevent Pollution
/clear          # Every 5-10 interactions
/compact        # When context >70%
/thinking basic # For simple tasks (save tokens)
/thinking ultra # For architecture decisions

# Session Continuity
--continue      # Auto-resume last conversation
--resume        # Select specific thread
--save          # Checkpoint important state

# Subagent Patterns
spawn: cc --thinking none "focused task with clear constraints"
merge: cc "synthesize results from agents A, B, C"
validate: cc "cross-check implementation against requirements"
```
</context_preservation>

## Quality Gates

<validation_matrix>
```yaml
pre_commit:
  - black --check
  - ruff check
  - mypy --strict
  - pytest --cov=app --cov-report=term-missing
  - npm run typecheck

code_review:
  - architecture: "Follows established patterns?"
  - performance: "Optimized queries and bundle size?"
  - security: "Input validation and auth checks?"
  - tests: "Coverage >90% with edge cases?"
```
</validation_matrix>

## Troubleshooting (One-Liners)

<quick_fixes>
```bash
svc_down:  docker-compose ps && docker-compose restart {service}
db_conn:   docker-compose exec postgres pg_isready -U kairos
api_auth:  echo $JWT_SECRET_KEY && curl -X POST localhost:8000/auth/token
fe_build:  rm -rf .next node_modules && npm i && npm run build
reset_all: docker-compose down -v && docker-compose up -d  # ⚠️ DATA LOSS
```
</quick_fixes>

## Performance Patterns

<optimization>
```python
# Query Optimization - Verify with latest SQLAlchemy docs
# "Current SQLAlchemy bulk operation patterns use context7"
.options(selectinload(Model.collection))      # Prevent N+1
.execution_options(synchronize_session=False) # Bulk operations
.limit(per_page + 1)                         # Cursor pagination

# Caching Strategy - Check Redis best practices
# "Latest Redis caching patterns for FastAPI use context7"
@cache_result(ttl=300, key=lambda x: f"user:{x.id}")
async def get_user_with_projects(user_id: int): ...

# Background Tasks - Verify Celery/BackgroundTasks usage
# "FastAPI background task patterns 2024 use context7"
background_tasks.add_task(process_heavy_operation, data)
```
</optimization>

## Context7 Usage Patterns

<context7_patterns>
```bash
# Framework Updates
"Show me Next.js 15 App Router patterns use context7"
"Latest FastAPI async dependency injection use context7"
"Current Shadcn/ui Dialog component API use context7"

# Library Research
"PostgreSQL 17 jsonb query optimization use context7"
"SQLAlchemy 2.0 hybrid properties syntax use context7"
"Pydantic v2 computed fields examples use context7"

# Problem Solving
"Debug TypeScript strict mode errors in Next.js use context7"
"Fix SQLAlchemy async session warnings use context7"
"Optimize Docker multi-stage builds for Python use context7"

# ANTI-PATTERNS (Never do this)
❌ "Create a FastAPI endpoint" (missing context7)
❌ Using memorized syntax without verification
❌ Assuming API hasn't changed since training
```
</context7_patterns>

## Success Metrics

<kpi>
- Development Speed: 2-3x faster with parallel agents
- Context Efficiency: less than 30% usage with /compact strategy
- Code Quality: 90%+ test coverage, zero type errors
- API Accuracy: 100% current patterns via context7 (vs 60% from memory)
- Debug Time: 80% reduction using up-to-date documentation
- Performance: less than 100ms API response, less than 3s page load
</kpi>
