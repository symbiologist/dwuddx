# Project Tasks 
As outlined in `PLANNING.md`, implement the following:

## Project Tasks
- Create a working app.py script

## Discovered During Work
(None yet)

## Completed Tasks
- Create a working app2.py script using Streamlit (Completed on 5/16/2025)
- Investigate auto-selection of chatbar input on page load in app2.py (Completed on 5/16/2025)
  - Note: After multiple approaches, it was determined that auto-focus is not supported in Streamlit. Added clear instructions for users to click in the input field instead.
- Create a working app3.py script using FastAPI (Completed on 5/16/2025)
  - Implemented a chat interface with streaming responses using Server-Sent Events (SSE)
  - Added dropdown menus for model and prompt selection
  - Ensured auto-focus on the input field works correctly
- Fix input chatbar covering LLM output (Completed on 5/16/2025)
  - Completely restructured the layout using flexbox to ensure proper content flow
  - Added significant bottom margin to the last message to prevent it from being hidden
  - Enhanced scrollToBottom function to detect and adjust for input area overlap
  - Improved the overall layout structure for better content visibility
- Fix duplicate icons in chat messages (Completed on 5/17/2025)
  - Identified two sources of icons: CSS ::before pseudo-elements and JavaScript-created avatar elements
  - Modified the CSS file to remove the ::before pseudo-elements
  - Updated the JavaScript addMessageToChat function to remove avatar creation entirely
  - Disabled template auto-generation in app3.py to prevent overwriting our changes
  - Each message now displays without any icons for a cleaner interface
