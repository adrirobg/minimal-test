# Pre-Commit Errors Report

## Ruff Errors

### F821: Undefined name
- `src\pkm_app\core\application\use_cases\project\update_project_use_case.py:20:44`
  - Undefined name `IProjectRepository`

## Mypy Errors

### attr-defined: Undefined attributes
- `src\pkm_app\core\application\use_cases\project\update_project_use_case.py:91`
  - `IUnitOfWork` has no attribute `begin`
- `src\pkm_app\core\application\use_cases\project\list_projects_use_case.py:91`
  - `IUnitOfWork` has no attribute `begin`
- `src\pkm_app\core\application\use_cases\project\get_project_use_case.py:90`
  - `IUnitOfWork` has no attribute `begin`
- `src\pkm_app\core\application\use_cases\project\delete_project_use_case.py:84`
  - `IUnitOfWork` has no attribute `begin`

### no-untyped-def: Missing type annotations
- `src\pkm_app\core\application\use_cases\project\list_projects_use_case.py:18`
- `src\pkm_app\core\application\use_cases\project\get_project_use_case.py:24`
- `src\pkm_app\core\application\use_cases\project\delete_project_use_case.py:18`
- `src\pkm_app\core\application\use_cases\project\create_project_use_case.py:20`

### no-any-return: Returning Any instead of declared type
- `src\pkm_app\core\application\use_cases\project\update_project_use_case.py:107`
  - Returning Any from function declared to return `ProjectSchema`
- `src\pkm_app\core\application\use_cases\project\list_projects_use_case.py:102`
  - Returning Any from function declared to return `list[ProjectSchema]`
- `src\pkm_app\core\application\use_cases\project\get_project_use_case.py:105`
  - Returning Any from function declared to return `ProjectSchema`

### return: Missing return statement
- `src\pkm_app\core\application\use_cases\project\create_project_use_case.py:36`

### call-arg: Missing positional arguments
- `src\pkm_app\core\application\use_cases\note_link\list_note_links_use_case.py:106`
  - Missing `user_id` in `get_by_id` call
- `src\pkm_app\core\application\use_cases\note_link\list_note_links_use_case.py:120`
  - Missing `user_id` in `get_by_id` call
- `src\pkm_app\core\application\use_cases\note_link\create_note_link_use_case.py:77`
  - Missing `user_id` in `get_by_id` call
- `src\pkm_app\core\application\use_cases\note_link\create_note_link_use_case.py:84`
  - Missing `user_id` in `get_by_id` call

### attr-defined: Undefined repository methods
- `src\pkm_app\core\application\use_cases\note_link\list_note_links_use_case.py:112`
  - `INoteLinkRepository` has no attribute `list_by_source_note`
- `src\pkm_app\core\application\use_cases\note_link\list_note_links_use_case.py:126`
  - `INoteLinkRepository` has no attribute `list_by_target_note`

### call-arg: Unexpected keyword arguments
- `src\pkm_app\core\application\use_cases\keyword\update_keyword_use_case.py:103`
  - Unexpected `entity_id` in `get_by_id` call
- `src\pkm_app\core\application\use_cases\keyword\update_keyword_use_case.py:116`
  - Unexpected `entity_id` and `entity_in` in `update` call
- `src\pkm_app\core\application\use_cases\keyword\get_keyword_use_case.py:85`
  - Unexpected `entity_id` in `get_by_id` call
- `src\pkm_app\core\application\use_cases\keyword\delete_keyword_use_case.py:88`
  - Unexpected `entity_id` in `get_by_id` call
- `src\pkm_app\core\application\use_cases\keyword\delete_keyword_use_case.py:115`
  - Unexpected `entity_id` in `delete` call
