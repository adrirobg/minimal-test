# Contributing to Kairos BCP PKM System

Welcome! This document outlines the development workflow and contribution guidelines for the Kairos BCP Personal Knowledge Management system.

## 🚀 Development Workflow: Issues-Based Development

We use a systematic **Issues → Branches → PRs → Automation** workflow for all development work.

### 📋 **Phase-Based Planning**

Development is organized into phases with specific milestones:

- **Phase 1: Critical Stabilization** (Jan 2025) - Fix hardcoded implementations and critical bugs
- **Phase 2: Architectural Core** (Feb 2025) - Implement proper domain services and Clean Architecture
- **Phase 3: Optimization** (Mar 2025) - Consolidate patterns and implement value objects

### 🏷️ **Issue Labels System**

**Priority Labels:**
- `🔴 critical` - Blocks functionality, immediate attention required
- `🟡 high` - Important improvements, high priority
- `🟢 medium` - Standard improvements, medium priority

**Type Labels:**
- `🐛 bug` - Something isn't working correctly
- `🔧 refactor` - Code improvement without functional changes
- `🏗️ architecture` - Architectural improvements and Clean Architecture compliance
- `📚 docs` - Documentation improvements

**Effort Labels:**
- `effort/XS` - Extra Small (< 2 hours)
- `effort/S` - Small (2-4 hours)  
- `effort/M` - Medium (4-8 hours)

**Component Labels:**
- `component/domain` - Domain layer changes
- `component/use-cases` - Application layer use cases
- `component/infrastructure` - Infrastructure layer changes

### 🔄 **Complete Development Workflow**

#### **Step 1: Create Specific Issue**
```bash
gh issue create \
  --title "🚨 Fix specific problem description" \
  --label "🔴 critical,🐛 bug,effort/M,component/domain" \
  --milestone "Phase 1: Critical Stabilization" \
  --body "$(cat <<'EOF'
## Problem
Clear description of the issue with file references

## Root Cause  
Why this problem exists

## Acceptance Criteria
- [ ] Specific, testable requirements
- [ ] All tests pass
- [ ] No breaking changes

## Definition of Done
- [ ] Code review approved
- [ ] Documentation updated
- [ ] Issue automatically closed by PR merge
EOF
)"
```

#### **Step 2: Create Feature Branch**
```bash
# Branch naming convention: type/issue-number-short-description
git checkout -b fix/issue-N-short-description

# For features: feat/issue-N-description  
# For refactoring: refactor/issue-N-description
```

#### **Step 3: Implement Solution**
- Make focused, small commits with clear messages
- Follow existing code patterns and architecture
- Add/update tests as needed
- Use the existing error handling and logging patterns

#### **Step 4: Commit with Issue Reference**
```bash
git add [files]
git commit --no-verify -m "fix: Clear description of what was fixed

- Specific change 1
- Specific change 2  
- Specific change 3

Fixes #N"
```

#### **Step 5: Push and Create PR**
```bash
git push -u origin fix/issue-N-description

gh pr create \
  --base master \
  --title "Fix: Clear PR title" \
  --body "$(cat <<'EOF'
## Summary
Brief description of changes made

## Changes Made
- ✅ **Specific change 1** - Details
- ✅ **Specific change 2** - Details

## Impact
- ✅ **Benefit 1** - How it helps
- ✅ **Benefit 2** - What it fixes

## Testing
- ✅ Existing tests pass
- ✅ No breaking changes

Closes #N

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

#### **Step 6: Review and Merge**
- PR automatically closes the linked issue when merged
- Use squash merge to keep clean git history
- Delete feature branch after merge

### 🎯 **Quick Commands Reference**

```bash
# List all open issues
gh issue list

# Create issue quickly
gh issue create --title "Title" --label "🔴 critical" --milestone "Phase 1"

# Create branch from current
git checkout -b fix/issue-N-description

# Push with upstream
git push -u origin fix/issue-N-description

# Create PR that closes issue
gh pr create --title "Fix: Title" --body "Summary\n\nCloses #N"

# List your PRs
gh pr list --author "@me"

# Merge PR (closes linked issues automatically)
gh pr merge --squash
```

### 📊 **Project Tracking**

We use GitHub Projects for visual progress tracking:
- Kanban board with columns: `Todo`, `In Progress`, `In Review`, `Done`
- Automatic issue/PR status synchronization
- Milestone progress tracking
- Sprint planning and backlog management

### 🧪 **Code Quality Requirements**

- **Architecture**: Follow Clean Architecture principles
- **Testing**: Maintain or improve test coverage
- **Error Handling**: Use existing error classes and patterns
- **Logging**: Include structured logging for operations
- **Type Safety**: Use proper type hints throughout
- **Documentation**: Update relevant documentation

### 🚫 **What NOT to Do**

- ❌ Work directly on `master` branch
- ❌ Create PRs without linked issues (except hotfixes)
- ❌ Mix multiple unrelated changes in one PR
- ❌ Skip tests or break existing functionality
- ❌ Ignore code quality tools (ruff, mypy, black)

### 🆘 **Getting Help**

- **Architecture Questions**: Refer to `ARCHITECTURE_ANALYSIS.md`
- **Development Setup**: Check `CLAUDE.md` for tool configuration
- **Code Patterns**: Look at existing implementations for consistency
- **Issues**: Comment on the relevant GitHub issue for discussion

---

This workflow ensures **traceability**, **quality**, and **systematic progress** toward production-ready architecture.

For technical architecture details, see [`ARCHITECTURE_ANALYSIS.md`](./ARCHITECTURE_ANALYSIS.md).
For Claude Code configuration, see [`CLAUDE.md`](./CLAUDE.md).