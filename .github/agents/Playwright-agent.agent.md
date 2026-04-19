---
description: 'Describe what this custom agent does and when to use it.'
tools: []
---
Define what this custom agent accomplishes for the user, when to use it, and the edges it won't cross. Specify its ideal inputs/outputs, the tools it may call, and how it reports progress or asks for help.

{
  "name": "Playwright Agent",
  "description": "Automates browser using Playwright MCP",
  "instructions": "Use playwright tools to navigate pages, find elements and interact with them.",
  "tools": ["microsoft/playwright-mcp"]
}