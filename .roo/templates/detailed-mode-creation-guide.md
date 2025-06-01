# Detailed Guide: Creating Custom Modes in Roo

This guide provides comprehensive instructions on how to create and configure custom modes in Roo, ensuring consistency and eliminating contradictions in setup and usage.

## Understanding Mode Configuration in Roo

Roo offers two ways to configure modes:

1. **Global Modes**: Apply to all projects (stored in `AppData/Roaming/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json`)
2. **Project-Specific Modes**: Apply only to the current project (stored in `.roomodes` file in the project root)

When modes with the same slug exist in both locations, the project-specific version takes precedence.

## Using the Native Roo Tool for Mode Creation

Roo has a built-in tool that provides detailed instructions for creating custom modes:

```javascript
<fetch_instructions>
<task>create_mode</task>
</fetch_instructions>
```

This tool returns comprehensive guidance on mode configuration structure and requirements.

## Mode Configuration Structure

A mode configuration in the `.roomodes` file follows this structure:

```json
{
  "customModes": [
    {
      "slug": "your-mode-slug",
      "name": "🔍 Your Mode Name",
      "roleDefinition": "Detailed description of the mode's role and capabilities...",
      "groups": [
        "read",
        ["edit", { "fileRegex": "\\.md$", "description": "Markdown files only" }],
        "browser",
        "command",
        "mcp"
      ],
      "customInstructions": "Additional mode-specific instructions..."
    }
  ]
}
```

### Required Fields

- **slug**: A unique identifier using lowercase letters, numbers, and hyphens (shorter is better)
- **name**: The display name for the mode (can include emoji)
- **roleDefinition**: A detailed description of the mode's role and capabilities
- **groups**: Array of allowed tool groups (can be empty)

### Optional Fields

- **customInstructions**: Additional instructions specific to the mode

## Tool Groups and Permissions

Roo modes can be granted access to different tool groups:

- **read**: Access to read files, search files, list files, etc.
- **edit**: Permission to modify files (can be restricted to specific file types)
- **browser**: Ability to use browser actions
- **command**: Permission to execute commands
- **mcp**: Access to MCP tools and resources

### File Restrictions

You can limit which files a mode can edit using regex patterns:

```json
["edit", { "fileRegex": "\\.md$", "description": "Markdown files only" }]
```

This example restricts the mode to only edit markdown files.

## Step-by-Step: Creating a Custom Mode

### Method 1: Using the Roo GUI

1. Click the "Modes" button in the Roo sidebar
2. Select "Edit Global Modes" or "Edit Project Modes (.roomodes)"
3. Add a new mode entry following the structure above
4. Click "Save"

### Method 2: Directly Editing Configuration Files

1. For global modes, edit: `AppData/Roaming/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json`
2. For project modes, edit: `.roomodes` in your project root
3. Add your mode configuration following the structure above
4. Save the file

### Method 3: Using an AI Assistant

You can use the prompt provided in the README under "Option C: Direct Setup with AI Assistant" to have an AI create the mode configurations for you.

## Example: Creating a Custom "Researcher" Mode

Here's a complete example of creating a custom "Researcher" mode:

```json
{
  "customModes": [
    {
      "slug": "researcher",
      "name": "🔬 Researcher",
      "roleDefinition": "Roo Role Definition: Scientific Research Specialist\nIdentity & Expertise\nYou are Roo, an advanced Scientific Research Agent optimized for conducting rigorous academic research. Your core capabilities include:\n\nLiterature Review: Comprehensive analysis of existing research across multiple disciplines.\nMethodology Design: Creating robust experimental frameworks and research protocols.\nData Analysis: Statistical evaluation and interpretation of complex datasets.\nScientific Writing: Producing clear, concise research papers and reports following academic standards.",
      "groups": [
        "read",
        ["edit", { "fileRegex": "\\.md$|\\.csv$|\\.txt$", "description": "Documentation and data files only" }],
        "browser",
        "command",
        "mcp"
      ],
      "customInstructions": "# Mode-specific Custom Instructions: Researcher Mode\n\n## Research Process Guidelines\n\n### 1. Literature Review Phase\n- Conduct comprehensive search of relevant academic databases\n- Analyze existing research for gaps and opportunities\n- Synthesize findings into structured literature review\n\n### 2. Methodology Development\n- Design rigorous research protocols\n- Establish clear hypotheses and testing frameworks\n- Define appropriate statistical methods for analysis\n\n### 3. Data Collection & Analysis\n- Implement systematic data collection procedures\n- Apply appropriate statistical tests\n- Interpret results in context of existing literature\n- Document limitations and potential biases"
    }
  ]
}
```

## System Consistency Audit

To ensure consistency in your mode configurations:

1. **Use correct directory references**: Use `.roomodes` for mode assignments and `.roo` for notes and documentation
2. **Standardize file paths**: Use consistent file path patterns across all modes
3. **Align permissions**: Ensure tool groups are appropriate for each mode's function
4. **Maintain consistent formatting**: Follow the same JSON structure for all modes
5. **Use clear descriptions**: Provide descriptive text for file restrictions

## Troubleshooting

If your custom mode isn't working as expected:

1. **Validate JSON syntax**: Ensure your JSON is properly formatted with no syntax errors
2. **Check for duplicates**: Make sure you don't have duplicate slugs in global and project modes
3. **Verify file paths**: Confirm that file regex patterns are correct
4. **Restart Roo**: Sometimes changes require a restart to take effect
5. **Check logs**: Look for error messages in the Roo logs

## Best Practices

1. **Start simple**: Begin with basic permissions and expand as needed
2. **Test thoroughly**: Verify that each mode can access only what it needs
3. **Document clearly**: Include detailed descriptions in customInstructions
4. **Use consistent naming**: Follow a consistent pattern for mode slugs and names
5. **Prefer project-specific modes**: Use `.roomodes` for project-specific configurations
6. **Focus on outcomes**: For Orchestrator mode, emphasize project completion over task decomposition

## Orchestrator Mode Best Practices

When configuring the Orchestrator mode, ensure it focuses on project completion rather than just task decomposition:

1. **Emphasize end-to-end completion**: Make it clear that the primary goal is completing the entire project
2. **Include integration steps**: Add instructions for integrating completed subtasks into cohesive deliverables
3. **Add verification procedures**: Include steps to verify that integrated results meet project requirements
4. **Maintain project vision**: Ensure the mode maintains focus on the final deliverables at all times
5. **Track completion progress**: Include instructions for tracking progress toward project completion