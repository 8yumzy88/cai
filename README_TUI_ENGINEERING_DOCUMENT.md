# Engineering Document: Multi-Agent Terminal User Interface (TUI)

## Document Metadata

- **Version**: 1.0
- **Date**: 2025-01-11
- **Purpose**: Technical specification for implementing a multi-agent terminal-based UI similar to CAI TUI
- **Target Audience**: Software engineers implementing similar systems
- **Framework**: Textual (Python TUI framework)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Core Components](#2-core-components)
3. [UI Layout Structure](#3-ui-layout-structure)
4. [State Management](#4-state-management)
5. [Event System](#5-event-system)
6. [Terminal Management](#6-terminal-management)
7. [Team Configuration System](#7-team-configuration-system)
8. [Parallel Execution Engine](#8-parallel-execution-engine)
9. [Sidebar Components](#9-sidebar-components)
10. [Input Handling](#10-input-handling)
11. [Output Rendering](#11-output-rendering)
12. [Session Management](#12-session-management)
13. [Implementation Patterns](#13-implementation-patterns)
14. [Data Structures](#14-data-structures)
15. [API Specifications](#15-api-specifications)
16. [Appendix: Agent Details](#appendix-agent-details)

---

## 1. Architecture Overview

### 1.1 High-Level Design

The TUI follows a component-based architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Top Bar    │  │   Sidebar    │  │  Terminals    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                  State Management Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ SessionMgr   │  │ TerminalMgr  │  │  AgentMgr    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                  Execution Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ AgentRunner  │  │ QueueMgr     │  │  StatsMgr    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

- **Framework**: Textual (Python TUI framework)
- **Language**: Python 3.9+
- **Dependencies**:
  - `textual` - TUI framework
  - `rich` - Terminal formatting
  - `asyncio` - Async execution
  - `prompt_toolkit` - Input handling (for CLI mode)

### 1.3 Design Principles

1. **Separation of Concerns**: UI, state, and execution are separate
2. **Event-Driven**: Components communicate via events
3. **Isolation**: Each terminal has isolated state
4. **Responsive**: UI adapts to terminal size
5. **Extensible**: Easy to add agents/teams

---

## 2. Core Components

### 2.1 Application Root (`App`)

**Responsibility**: Main application container, coordinates all components

**Key Features**:
- Manages application lifecycle
- Handles global keyboard shortcuts
- Coordinates component communication
- Manages focus between terminals

**Structure**:
```python
class MultiAgentTUI(App):
    """Main application class."""
    
    # Component references
    top_bar: TopBar
    sidebar: Sidebar
    terminal_grid: TerminalGrid
    status_bar: StatusBar
    
    # State managers
    session_manager: SessionManager
    terminal_manager: TerminalManager
    agent_manager: AgentManager
    
    # Event handlers
    def on_key(self, event: Key) -> None
    def on_mount(self) -> None
    def action_toggle_sidebar(self) -> None
```

### 2.2 Terminal Grid (`TerminalGrid`)

**Responsibility**: Manages layout and rendering of multiple terminals

**Key Features**:
- Responsive layout (1-4 terminals)
- Dynamic resizing
- Focus management
- Terminal addition/removal

**Layout Patterns**:
- **1 terminal**: Full-screen
- **2 terminals**: Horizontal split (50/50)
- **3 terminals**: 2+1 grid (top 2, bottom 1)
- **4 terminals**: 2x2 grid

**Implementation**:
```python
class TerminalGrid(Container):
    """Grid container for terminals."""
    
    terminals: Dict[int, TerminalWidget]
    active_terminal_id: int = 1
    max_terminals: int = 4
    
    def add_terminal(self) -> bool
    def remove_terminal(self, terminal_id: int) -> bool
    def focus_terminal(self, terminal_id: int) -> None
    def get_layout(self) -> Layout
```

### 2.3 Terminal Widget (`TerminalWidget`)

**Responsibility**: Individual terminal display and interaction

**Key Features**:
- Header with agent/model selectors
- Output area with scrolling
- Input area
- Status indicators

**Structure**:
```python
class TerminalWidget(Widget):
    """Individual terminal widget."""
    
    terminal_id: int
    agent_name: str
    model_name: str
    conversation_history: List[Message]
    is_executing: bool = False
    
    # UI Components
    header: TerminalHeader
    output_area: ScrollableContainer
    input_area: Input
    
    def set_agent(self, agent_name: str) -> None
    def set_model(self, model_name: str) -> None
    def add_output(self, content: str, role: str) -> None
    def clear_output(self) -> None
```

### 2.4 Sidebar (`Sidebar`)

**Responsibility**: Side panel with tabs for teams, queue, stats, keys

**Key Features**:
- Collapsible (toggle with Ctrl+S)
- Tab navigation
- Scrollable content
- Responsive width (32 chars when open)

**Structure**:
```python
class Sidebar(Container):
    """Sidebar with tabs."""
    
    is_visible: bool = True
    active_tab: str = "teams"
    
    # Tab widgets
    teams_tab: TeamsTab
    queue_tab: QueueTab
    stats_tab: StatsTab
    keys_tab: KeysTab
    
    def toggle_visibility(self) -> None
    def switch_tab(self, tab_name: str) -> None
```

---

## 3. UI Layout Structure

### 3.1 Layout Hierarchy

```
App
├── TopBar (fixed height: 1 line)
├── HSplit
│   ├── TerminalGrid (flex: 1)
│   │   ├── TerminalWidget (T1)
│   │   ├── TerminalWidget (T2)
│   │   ├── TerminalWidget (T3)
│   │   └── TerminalWidget (T4)
│   └── Sidebar (width: 32, collapsible)
│       ├── TeamsTab
│       ├── QueueTab
│       ├── StatsTab
│       └── KeysTab
└── StatusBar (fixed height: 1 line)
```

### 3.2 Responsive Behavior

**Terminal Width < 120 chars**:
- Hide sidebar by default
- Compact terminal headers
- Single-column layout

**Terminal Width 120-160 chars**:
- Sidebar visible, compact
- Medium terminal headers
- 2-column terminal grid max

**Terminal Width > 160 chars**:
- Full sidebar
- Full terminal headers
- 2x2 terminal grid

### 3.3 Color Scheme

Use a consistent palette:
- **Primary**: Cyan/Blue for active elements
- **Success**: Green for completed operations
- **Warning**: Yellow for pending/queued
- **Error**: Red for errors/failures
- **Muted**: Gray for inactive/secondary

---

## 4. State Management

### 4.1 Session Manager

**Responsibility**: Manages application-wide state

**State Data**:
```python
@dataclass
class SessionState:
    session_id: str
    start_time: datetime
    total_cost: float
    total_tokens: int
    active_terminals: Set[int]
    current_team: Optional[TeamConfig]
```

**Key Methods**:
- `start_session() -> SessionState`
- `end_session() -> SessionSummary`
- `save_session(path: str) -> None`
- `load_session(path: str) -> SessionState`

### 4.2 Terminal Manager

**Responsibility**: Manages terminal instances and their state

**State Data**:
```python
@dataclass
class TerminalState:
    terminal_id: int
    agent_name: str
    model_name: str
    conversation_history: List[Message]
    is_executing: bool
    queue: List[str]
    cost: float
    tokens_used: int
```

**Key Methods**:
- `create_terminal() -> TerminalState`
- `remove_terminal(terminal_id: int) -> None`
- `update_terminal(terminal_id: int, updates: Dict) -> None`
- `get_terminal_state(terminal_id: int) -> TerminalState`

### 4.3 Agent Manager

**Responsibility**: Manages agent instances and configurations

**State Data**:
```python
@dataclass
class AgentConfig:
    name: str
    display_name: str
    description: str
    default_model: str
    capabilities: List[str]
```

**Key Methods**:
- `get_available_agents() -> Dict[str, AgentConfig]`
- `create_agent(agent_name: str, terminal_id: int) -> Agent`
- `switch_agent(terminal_id: int, agent_name: str) -> None`

---

## 5. Event System

### 5.1 Event Types

**Terminal Events**:
- `TerminalCreated(terminal_id: int)`
- `TerminalRemoved(terminal_id: int)`
- `TerminalFocused(terminal_id: int)`
- `AgentChanged(terminal_id: int, agent_name: str)`
- `ModelChanged(terminal_id: int, model_name: str)`
- `ExecutionStarted(terminal_id: int, prompt: str)`
- `ExecutionCompleted(terminal_id: int, result: Any)`
- `OutputReceived(terminal_id: int, content: str)`

**Team Events**:
- `TeamSelected(team_config: TeamConfig)`
- `TeamApplied(team_config: TeamConfig)`

**Session Events**:
- `SessionStarted(session_id: str)`
- `SessionEnded(session_id: str)`
- `SessionSaved(path: str)`
- `SessionLoaded(path: str)`

### 5.2 Event Handling Pattern

```python
class TerminalWidget(Widget):
    def on_terminal_created(self, event: TerminalCreated) -> None:
        """Handle terminal creation."""
        if event.terminal_id == self.terminal_id:
            self.initialize()
    
    def on_agent_changed(self, event: AgentChanged) -> None:
        """Handle agent change."""
        if event.terminal_id == self.terminal_id:
            self.agent_name = event.agent_name
            self.update_header()
```

---

## 6. Terminal Management

### 6.1 Terminal Lifecycle

**Creation**:
1. User clicks "Add+" button or presses shortcut
2. `TerminalManager.create_terminal()` called
3. Default agent/model assigned
4. `TerminalWidget` created and added to grid
5. `TerminalCreated` event emitted
6. Terminal focused automatically

**Removal**:
1. User closes terminal (Ctrl+E) or clicks close button
2. Check if terminal is main terminal (T1 cannot be closed)
3. Check if terminal is executing (warn if so)
4. Save conversation history if needed
5. Remove from grid
6. Re-layout remaining terminals
7. `TerminalRemoved` event emitted

### 6.2 Terminal Focus Management

**Focus Rules**:
- Only one terminal focused at a time
- Focused terminal shows visual indicator (border highlight)
- Input goes to focused terminal
- Keyboard shortcuts apply to focused terminal

**Focus Navigation**:
- `Ctrl+N`: Next terminal (wrap around)
- `Ctrl+B`: Previous terminal (wrap around)
- Mouse click: Direct focus
- Tab key: Cycle through terminals

### 6.3 Terminal State Isolation

Each terminal maintains:
- **Independent conversation history**
- **Separate agent instance**
- **Isolated execution context**
- **Individual cost tracking**
- **Separate token counting**

---

## 7. Team Configuration System

### 7.1 Team Data Structure

```python
@dataclass
class TeamConfig:
    team_id: int
    name: str
    description: str
    terminal_assignments: Dict[int, str]  # terminal_id -> agent_name
    use_case: str
    
    def get_compact_label(self) -> str:
        """Generate compact label like '2 red + 2 bug'."""
        agent_counts = {}
        for agent_name in self.terminal_assignments.values():
            agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
        
        parts = []
        for agent_name, count in agent_counts.items():
            short_name = agent_name.replace('_agent', '')
            parts.append(f"{count} {short_name}")
        
        return " + ".join(parts)
```

### 7.2 Team Application Flow

**When team is selected**:
1. User clicks team button in sidebar
2. `TeamConfig` retrieved
3. For each terminal assignment:
   - Get terminal widget
   - Update agent name
   - Update header display
   - Preserve conversation history
4. Emit `TeamApplied` event
5. Update sidebar to show active team

**Preservation Rules**:
- Conversation history preserved
- Model selection preserved (unless team specifies)
- Terminal focus preserved
- Execution state preserved

### 7.3 Team Button Rendering

**Display Logic**:
```python
def render_team_button(team: TeamConfig, width: int) -> str:
    """Render team button with adaptive width."""
    if width >= 30:
        # Full width: show complete names
        label = team.get_compact_label()
    else:
        # Narrow width: abbreviate
        label = team.get_compact_label_short()
    
    return f"#{team.team_id}: {label}"
```

**Tooltip**:
- Show on hover
- Display full team composition
- Terminal-by-terminal breakdown
- Use case description

---

## 8. Parallel Execution Engine

### 8.1 Execution Model

**Single Terminal Execution**:
```python
async def execute_terminal(
    terminal_id: int,
    prompt: str,
    agent: Agent,
    model: Model
) -> ExecutionResult:
    """Execute prompt in single terminal."""
    terminal_state = terminal_manager.get_terminal_state(terminal_id)
    
    # Mark as executing
    terminal_state.is_executing = True
    emit(ExecutionStarted(terminal_id, prompt))
    
    try:
        # Run agent
        result = await agent.run(prompt, model)
        
        # Update state
        terminal_state.conversation_history.append({
            'role': 'user',
            'content': prompt
        })
        terminal_state.conversation_history.append({
            'role': 'assistant',
            'content': result.output
        })
        terminal_state.cost += result.cost
        terminal_state.tokens_used += result.tokens
        
        emit(ExecutionCompleted(terminal_id, result))
        return result
        
    finally:
        terminal_state.is_executing = False
```

**Parallel Execution**:
```python
async def execute_parallel(
    terminals: List[int],
    prompt: str
) -> List[ExecutionResult]:
    """Execute same prompt in multiple terminals."""
    tasks = []
    
    for terminal_id in terminals:
        terminal_state = terminal_manager.get_terminal_state(terminal_id)
        agent = agent_manager.get_agent(terminal_state.agent_name)
        model = model_manager.get_model(terminal_state.model_name)
        
        task = execute_terminal(terminal_id, prompt, agent, model)
        tasks.append(task)
    
    # Execute all in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

### 8.2 Queue Management

**Queue Structure**:
```python
@dataclass
class QueuedCommand:
    terminal_id: int
    prompt: str
    timestamp: datetime
    status: str  # 'pending', 'executing', 'completed'
```

**Queue Behavior**:
- Commands auto-queue when terminal is busy
- FIFO execution order
- Per-terminal queues
- Visual queue display in sidebar

**Queue Processing**:
```python
async def process_queue(terminal_id: int) -> None:
    """Process queued commands for terminal."""
    queue = queue_manager.get_queue(terminal_id)
    terminal_state = terminal_manager.get_terminal_state(terminal_id)
    
    while queue and not terminal_state.is_executing:
        command = queue.pop(0)
        command.status = 'executing'
        emit(QueueUpdated(terminal_id, queue))
        
        await execute_terminal(terminal_id, command.prompt, ...)
        
        command.status = 'completed'
        emit(QueueUpdated(terminal_id, queue))
```

---

## 9. Sidebar Components

### 9.1 Teams Tab

**Structure**:
```python
class TeamsTab(Widget):
    """Teams selection tab."""
    
    teams: List[TeamConfig]
    active_team_id: Optional[int]
    
    def render_team_button(self, team: TeamConfig) -> str:
        """Render clickable team button."""
        label = team.get_compact_label()
        if team.team_id == self.active_team_id:
            return f"[bold cyan]#{team.team_id}: {label}[/bold cyan]"
        return f"#{team.team_id}: {label}"
    
    def on_click(self, event: Click) -> None:
        """Handle team button click."""
        team_id = self.get_team_id_from_position(event.x, event.y)
        if team_id:
            self.select_team(team_id)
```

**Features**:
- Scrollable list of team buttons
- Active team highlighting
- Tooltip on hover
- Click to apply

### 9.2 Queue Tab

**Structure**:
```python
class QueueTab(Widget):
    """Command queue display."""
    
    queues: Dict[int, List[QueuedCommand]]
    
    def render_queue(self, terminal_id: int) -> str:
        """Render queue for terminal."""
        queue = self.queues.get(terminal_id, [])
        if not queue:
            return f"T{terminal_id}: [dim]No queued commands[/dim]"
        
        lines = [f"T{terminal_id}:"]
        for i, cmd in enumerate(queue, 1):
            status_icon = "▶" if cmd.status == 'executing' else "⏸"
            lines.append(f"  [{i}] {status_icon} {cmd.prompt[:50]}...")
        
        return "\n".join(lines)
```

### 9.3 Stats Tab

**Structure**:
```python
class StatsTab(Widget):
    """Statistics display."""
    
    session_stats: SessionStats
    terminal_stats: Dict[int, TerminalStats]
    
    def render_stats(self) -> str:
        """Render statistics."""
        lines = [
            f"Session Total: ${self.session_stats.total_cost:.2f}",
            f"Total Tokens: {self.session_stats.total_tokens:,}",
            "",
            "Per Terminal:"
        ]
        
        for terminal_id, stats in self.terminal_stats.items():
            lines.append(
                f"T{terminal_id}: ${stats.cost:.2f} "
                f"({stats.tokens:,} tokens)"
            )
        
        return "\n".join(lines)
```

**Update Frequency**:
- Real-time updates during execution
- Refresh every 1 second when active
- Lazy update when tab not visible

### 9.4 Keys Tab

**Structure**:
```python
class KeysTab(Widget):
    """API key management."""
    
    keys: Dict[str, str]  # provider -> masked_key
    
    def render_keys(self) -> str:
        """Render API keys."""
        lines = []
        for provider, masked_key in self.keys.items():
            lines.append(f"{provider}: {masked_key}")
        return "\n".join(lines)
    
    def add_key(self, provider: str, key: str) -> None:
        """Add or update API key."""
        self.keys[provider] = self.mask_key(key)
        # Save to .env file
        self.save_to_env(provider, key)
```

---

## 10. Input Handling

### 10.1 Input Flow

**Input Processing**:
1. User types in input area
2. Input validated (command vs prompt)
3. If command (starts with `/`): route to command handler
4. If prompt: check for broadcast flag (`all`)
5. Route to appropriate terminal(s)
6. Queue if terminal busy, execute if idle

**Command Parsing**:
```python
def parse_input(input_text: str) -> InputCommand:
    """Parse user input."""
    input_text = input_text.strip()
    
    # Check for terminal-specific command (T1:prompt)
    if match := re.match(r'^T(\d+):(.+)$', input_text):
        terminal_id = int(match.group(1))
        prompt = match.group(2)
        return InputCommand(
            type='terminal_specific',
            terminal_id=terminal_id,
            content=prompt
        )
    
    # Check for broadcast (prompt all)
    if input_text.endswith(' all'):
        prompt = input_text[:-4].strip()
        return InputCommand(
            type='broadcast',
            terminals='all',
            content=prompt
        )
    
    # Check for command (starts with /)
    if input_text.startswith('/'):
        return InputCommand(
            type='command',
            command=input_text.split()[0],
            args=input_text.split()[1:]
        )
    
    # Default: prompt to focused terminal
    return InputCommand(
        type='prompt',
        terminal_id=app.focused_terminal_id,
        content=input_text
    )
```

### 10.2 Command System

**Command Registry**:
```python
class CommandRegistry:
    """Registry for commands."""
    
    commands: Dict[str, CommandHandler]
    
    def register(self, name: str, handler: CommandHandler) -> None:
        """Register command."""
        self.commands[name] = handler
    
    def execute(self, command: str, args: List[str]) -> bool:
        """Execute command."""
        handler = self.commands.get(command)
        if handler:
            return handler(args)
        return False
```

**Built-in Commands**:
- `/agent [name]` - Switch agent
- `/model [name]` - Switch model
- `/clear` - Clear terminal output
- `/save [path]` - Save session
- `/load [path]` - Load session
- `/help` - Show help

---

## 11. Output Rendering

### 11.1 Output Formatting

**Message Types**:
- **User messages**: Plain text, left-aligned
- **Agent messages**: Formatted with syntax highlighting
- **Tool calls**: Collapsible sections with status
- **Errors**: Red-highlighted with error icon

**Rendering**:
```python
def render_message(message: Message) -> str:
    """Render message for display."""
    if message.role == 'user':
        return f"[dim]You:[/dim] {message.content}"
    
    elif message.role == 'assistant':
        # Check for code blocks
        if '```' in message.content:
            return render_code_blocks(message.content)
        return message.content
    
    elif message.role == 'tool':
        return render_tool_output(message)
```

### 11.2 Streaming Output

**Streaming Pattern**:
```python
async def stream_output(terminal_id: int, stream: AsyncIterator) -> None:
    """Stream output to terminal."""
    terminal_widget = get_terminal_widget(terminal_id)
    
    async for chunk in stream:
        terminal_widget.append_output(chunk)
        terminal_widget.refresh()
```

**Visual Indicators**:
- Cursor animation during streaming
- Progress indicator for long operations
- Status badges for tool execution

---

## 12. Session Management

### 12.1 Session Data Structure

```python
@dataclass
class SessionData:
    """Complete session data."""
    session_id: str
    timestamp: datetime
    terminals: List[TerminalState]
    team_config: Optional[TeamConfig]
    total_cost: float
    total_tokens: int
    metadata: Dict[str, Any]
```

### 12.2 Save/Load Flow

**Save**:
```python
def save_session(path: str) -> None:
    """Save session to file."""
    session_data = SessionData(
        session_id=session_manager.session_id,
        timestamp=datetime.now(),
        terminals=[
            terminal_manager.get_terminal_state(tid)
            for tid in terminal_manager.get_active_terminals()
        ],
        team_config=session_manager.current_team,
        total_cost=session_manager.total_cost,
        total_tokens=session_manager.total_tokens,
        metadata={}
    )
    
    with open(path, 'w') as f:
        json.dump(session_data.to_dict(), f, indent=2)
```

**Load**:
```python
def load_session(path: str) -> None:
    """Load session from file."""
    with open(path, 'r') as f:
        data = json.load(f)
    
    session_data = SessionData.from_dict(data)
    
    # Restore terminals
    for terminal_state in session_data.terminals:
        terminal_manager.restore_terminal(terminal_state)
    
    # Restore team if applicable
    if session_data.team_config:
        team_manager.apply_team(session_data.team_config)
```

---

## 13. Implementation Patterns

### 13.1 Component Pattern

**Base Component**:
```python
class BaseComponent(Widget):
    """Base component with common functionality."""
    
    def on_mount(self) -> None:
        """Initialize component."""
        self.setup_event_handlers()
    
    def setup_event_handlers(self) -> None:
        """Register event handlers."""
        self.app.on(SomeEvent, self.handle_event)
    
    def handle_event(self, event: SomeEvent) -> None:
        """Handle event."""
        pass
```

### 13.2 Manager Pattern

**State Manager**:
```python
class StateManager:
    """Manages application state."""
    
    _state: Dict[str, Any]
    _listeners: List[Callable]
    
    def get_state(self, key: str) -> Any:
        """Get state value."""
        return self._state.get(key)
    
    def set_state(self, key: str, value: Any) -> None:
        """Set state value and notify listeners."""
        self._state[key] = value
        self.notify_listeners(key, value)
    
    def notify_listeners(self, key: str, value: Any) -> None:
        """Notify all listeners of state change."""
        for listener in self._listeners:
            listener(key, value)
```

### 13.3 Observer Pattern

**Event Observer**:
```python
class EventObserver:
    """Observes and reacts to events."""
    
    def __init__(self):
        self.handlers: Dict[Type, List[Callable]] = {}
    
    def subscribe(self, event_type: Type, handler: Callable) -> None:
        """Subscribe to event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def emit(self, event: Event) -> None:
        """Emit event to subscribers."""
        event_type = type(event)
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(event)
```

---

## 14. Data Structures

### 14.1 Core Data Models

```python
@dataclass
class Message:
    """Conversation message."""
    role: str  # 'user', 'assistant', 'tool', 'system'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Agent:
    """Agent instance."""
    name: str
    display_name: str
    model: Model
    conversation_history: List[Message]
    tools: List[Tool]
    
@dataclass
class ExecutionResult:
    """Execution result."""
    output: str
    cost: float
    tokens: int
    duration: float
    tool_calls: List[ToolCall]
```

### 14.2 Configuration Models

```python
@dataclass
class AppConfig:
    """Application configuration."""
    max_terminals: int = 4
    default_agent: str = "default_agent"
    default_model: str = "default_model"
    sidebar_width: int = 32
    auto_save: bool = False
    save_interval: int = 300  # seconds
```

---

## 15. API Specifications

### 15.1 Terminal API

```python
class TerminalAPI:
    """API for terminal operations."""
    
    def create_terminal() -> int:
        """Create new terminal. Returns terminal_id."""
        pass
    
    def remove_terminal(terminal_id: int) -> bool:
        """Remove terminal. Returns success."""
        pass
    
    def set_agent(terminal_id: int, agent_name: str) -> None:
        """Set agent for terminal."""
        pass
    
    def set_model(terminal_id: int, model_name: str) -> None:
        """Set model for terminal."""
        pass
    
    def execute(terminal_id: int, prompt: str) -> ExecutionResult:
        """Execute prompt in terminal."""
        pass
    
    def get_history(terminal_id: int) -> List[Message]:
        """Get conversation history."""
        pass
```

### 15.2 Team API

```python
class TeamAPI:
    """API for team operations."""
    
    def get_teams() -> List[TeamConfig]:
        """Get all available teams."""
        pass
    
    def apply_team(team_id: int) -> None:
        """Apply team configuration."""
        pass
    
    def create_team(config: TeamConfig) -> int:
        """Create custom team. Returns team_id."""
        pass
```

---

## Appendix: Agent Details

### Agent Types

The system supports multiple agent types. Each agent has:

- **Name**: Internal identifier (e.g., `redteam_agent`)
- **Display Name**: Human-readable name (e.g., "Red Team Agent")
- **Description**: Purpose and capabilities
- **Default Model**: Recommended model
- **Tools**: Available tools/capabilities

### Example Agent Configuration

```python
AGENTS = {
    "redteam_agent": AgentConfig(
        name="redteam_agent",
        display_name="Red Team Agent",
        description="Offensive security specialist for penetration testing",
        default_model="alias1",
        capabilities=["exploitation", "vulnerability_discovery", "reconnaissance"],
        tools=["generic_linux_command", "execute_code", "web_search"]
    ),
    "blueteam_agent": AgentConfig(
        name="blueteam_agent",
        display_name="Blue Team Agent",
        description="Defensive security expert for threat mitigation",
        default_model="alias1",
        capabilities=["hardening", "incident_response", "threat_analysis"],
        tools=["generic_linux_command", "ssh_command", "execute_code"]
    ),
    # ... additional agents
}
```

### Preconfigured Teams

The system includes 11 preconfigured teams optimized for different security workflows:

#### Team 1: 2 Red + 2 Bug
- **Terminal 1**: `redteam_agent`
- **Terminal 2**: `redteam_agent`
- **Terminal 3**: `bug_bounter_agent`
- **Terminal 4**: `bug_bounter_agent`
- **Use Case**: Comprehensive vulnerability discovery combining offensive testing with bug bounty methodology

#### Team 2: 1 Red (T1) + 3 Bug
- **Terminal 1**: `redteam_agent`
- **Terminal 2**: `bug_bounter_agent`
- **Terminal 3**: `bug_bounter_agent`
- **Terminal 4**: `bug_bounter_agent`
- **Use Case**: Bug bounty programs with red team leadership and multiple hunters focusing on different attack surfaces

#### Team 3: 2 Red + 2 Blue
- **Terminal 1**: `redteam_agent`
- **Terminal 2**: `redteam_agent`
- **Terminal 3**: `blueteam_agent`
- **Terminal 4**: `blueteam_agent`
- **Use Case**: Adversarial testing with simultaneous offensive and defensive perspectives

#### Team 4: 2 Blue + 2 Bug
- **Terminal 1**: `blueteam_agent`
- **Terminal 2**: `blueteam_agent`
- **Terminal 3**: `bug_bounter_agent`
- **Terminal 4**: `bug_bounter_agent`
- **Use Case**: Defense-focused assessments with vulnerability validation from bug bounty perspective

#### Team 5: Red + Blue + Retester + Bug
- **Terminal 1**: `redteam_agent`
- **Terminal 2**: `blueteam_agent`
- **Terminal 3**: `retester_agent`
- **Terminal 4**: `bug_bounter_agent`
- **Use Case**: Complete security lifecycle from discovery to validation with mixed specialties

#### Team 6: 2 Red + 2 Retester
- **Terminal 1**: `redteam_agent`
- **Terminal 2**: `redteam_agent`
- **Terminal 3**: `retester_agent`
- **Terminal 4**: `retester_agent`
- **Use Case**: Aggressive offensive testing with immediate vulnerability retesting and validation

#### Team 7: 2 Blue + 2 Retester
- **Terminal 1**: `blueteam_agent`
- **Terminal 2**: `blueteam_agent`
- **Terminal 3**: `retester_agent`
- **Terminal 4**: `retester_agent`
- **Use Case**: Defensive security validation with continuous retesting of hardening measures

#### Team 8: 4 Red
- **Terminal 1**: `redteam_agent`
- **Terminal 2**: `redteam_agent`
- **Terminal 3**: `redteam_agent`
- **Terminal 4**: `redteam_agent`
- **Use Case**: Maximum offensive power, CTF competitions, intensive penetration testing campaigns

#### Team 9: 4 Blue
- **Terminal 1**: `blueteam_agent`
- **Terminal 2**: `blueteam_agent`
- **Terminal 3**: `blueteam_agent`
- **Terminal 4**: `blueteam_agent`
- **Use Case**: Comprehensive defensive analysis, security architecture review, hardening validation

#### Team 10: 4 Bug
- **Terminal 1**: `bug_bounter_agent`
- **Terminal 2**: `bug_bounter_agent`
- **Terminal 3**: `bug_bounter_agent`
- **Terminal 4**: `bug_bounter_agent`
- **Use Case**: Bug bounty hunts, vulnerability research, OWASP Top 10 testing across multiple surfaces

#### Team 11: 4 Retester
- **Terminal 1**: `retester_agent`
- **Terminal 2**: `retester_agent`
- **Terminal 3**: `retester_agent`
- **Terminal 4**: `retester_agent`
- **Use Case**: Large-scale retesting campaigns, verification of fixes, regression testing

### Team Configuration Format

```python
TEAMS = [
    TeamConfig(
        team_id=1,
        name="2 Red + 2 Bug",
        description="Comprehensive vulnerability discovery",
        terminal_assignments={
            1: "redteam_agent",
            2: "redteam_agent",
            3: "bug_bounter_agent",
            4: "bug_bounter_agent"
        },
        use_case="Penetration testing and vulnerability discovery"
    ),
    # ... additional teams
]
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Set up Textual application structure
- [ ] Implement basic layout (top bar, grid, sidebar, status bar)
- [ ] Create state management system
- [ ] Implement event system
- [ ] Add keyboard shortcut handling

### Phase 2: Terminal Management
- [ ] Implement terminal widget
- [ ] Add terminal creation/removal
- [ ] Implement focus management
- [ ] Add terminal state isolation
- [ ] Implement responsive layouts

### Phase 3: Sidebar Components
- [ ] Implement sidebar with tabs
- [ ] Create teams tab with team buttons
- [ ] Create queue tab
- [ ] Create stats tab
- [ ] Create keys tab

### Phase 4: Execution Engine
- [ ] Implement single terminal execution
- [ ] Implement parallel execution
- [ ] Add queue management
- [ ] Implement streaming output
- [ ] Add error handling

### Phase 5: Advanced Features
- [ ] Team configuration system
- [ ] Session save/load
- [ ] Command system
- [ ] Input parsing and routing
- [ ] Output formatting and rendering

### Phase 6: Polish
- [ ] Add tooltips and help
- [ ] Implement responsive behavior
- [ ] Add visual indicators
- [ ] Performance optimization
- [ ] Error recovery

---

## References

- **Textual Documentation**: https://textual.textualize.io/
- **Rich Documentation**: https://rich.readthedocs.io/
- **Asyncio Documentation**: https://docs.python.org/3/library/asyncio.html

---

**End of Document**

