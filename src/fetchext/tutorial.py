from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, Markdown
from textual.screen import Screen
from textual.binding import Binding

TUTORIAL_STEPS = [
    {
        "title": "Welcome to fetchext",
        "content": """
# Welcome to fetchext!

`fetchext` (fext) is a powerful CLI tool for downloading, analyzing, and managing browser extensions.

This tutorial will guide you through the main features of the tool.

**Navigation:**
- Press **Next** to proceed.
- Press **Previous** to go back.
- Press **Quit** or `q` to exit.
"""
    },
    {
        "title": "Downloading Extensions",
        "content": """
# Downloading Extensions

The core feature of `fext` is downloading extensions from Chrome, Edge, and Firefox Web Stores.

**Command:**
```bash
fext download <browser> <url_or_id>
```

**Examples:**
- Chrome: `fext download chrome <url>`
- Firefox: `fext download firefox <url>`
- Edge: `fext download edge <url>`

**Flags:**
- `-x` / `--extract`: Automatically unzip the extension.
- `-m` / `--save-metadata`: Save details to a JSON file.
"""
    },
    {
        "title": "Searching",
        "content": """
# Searching for Extensions

You can search for extensions directly from the command line (currently Firefox only).

**Command:**
```bash
fext search firefox "adblock"
```

**Output:**
- Displays a table of results with IDs, names, and users.
- Use `--json` for machine-readable output.
"""
    },
    {
        "title": "Inspecting & Analyzing",
        "content": """
# Inspecting & Analyzing

`fext` provides powerful tools to analyze extension files (`.crx`, `.xpi`).

**Commands:**
- `fext inspect <file>`: View manifest details.
- `fext preview <file>`: List file contents without extracting.
- `fext risk <file>`: Analyze permission risks.
- `fext audit <file>`: Check for Manifest V3 compatibility.
- `fext scan <file>`: Scan for vulnerable dependencies.
"""
    },
    {
        "title": "Advanced Features",
        "content": """
# Advanced Features

- **Timeline**: `fext timeline <file>` - Visualize file modification dates.
- **Graph**: `fext graph <file>` - Generate dependency graphs.
- **Serve**: `fext serve` - Host a local update server.
- **Optimize**: `fext optimize <dir>` - Compress images.
- **Mirror**: `fext mirror <list>` - Sync a local repository.
"""
    },
    {
        "title": "Configuration",
        "content": """
# Configuration

You can customize `fext` behavior using the config file.

**Command:**
```bash
fext config list
fext config set general.download_dir /path/to/downloads
```

**Setup Wizard:**
Run `fext setup` to interactively configure the tool.
"""
    },
    {
        "title": "Conclusion",
        "content": """
# You're Ready!

You now know the basics of `fext`.

Explore the help menu for more details:
```bash
fext --help
```

Happy hacking!
"""
    }
]

class TutorialStep(Container):
    def __init__(self, step_index: int):
        super().__init__()
        self.step_index = step_index
        self.step_data = TUTORIAL_STEPS[step_index]

    def compose(self) -> ComposeResult:
        yield Markdown(self.step_data["content"])

class TutorialApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #main-container {
        width: 80%;
        height: 80%;
        border: solid green;
        padding: 1 2;
        background: $surface;
    }

    #content {
        height: 1fr;
        overflow-y: auto;
    }

    #buttons {
        height: 3;
        dock: bottom;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "next_step", "Next"),
        ("p", "prev_step", "Previous"),
    ]

    def __init__(self):
        super().__init__()
        self.current_step = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Container(id="content"),
            Horizontal(
                Button("Previous", id="btn-prev", variant="primary"),
                Button("Next", id="btn-next", variant="success"),
                Button("Quit", id="btn-quit", variant="error"),
                id="buttons"
            ),
            id="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.update_step()

    def update_step(self) -> None:
        content_container = self.query_one("#content")
        content_container.remove_children()
        content_container.mount(TutorialStep(self.current_step))
        
        self.title = f"fext Tutorial - {self.current_step + 1}/{len(TUTORIAL_STEPS)}"
        
        # Update button states
        self.query_one("#btn-prev").disabled = self.current_step == 0
        
        next_btn = self.query_one("#btn-next")
        if self.current_step == len(TUTORIAL_STEPS) - 1:
            next_btn.label = "Finish"
            next_btn.variant = "success"
        else:
            next_btn.label = "Next"
            next_btn.variant = "primary"

    def action_next_step(self) -> None:
        if self.current_step < len(TUTORIAL_STEPS) - 1:
            self.current_step += 1
            self.update_step()
        else:
            self.exit()

    def action_prev_step(self) -> None:
        if self.current_step > 0:
            self.current_step -= 1
            self.update_step()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-next":
            self.action_next_step()
        elif event.button.id == "btn-prev":
            self.action_prev_step()
        elif event.button.id == "btn-quit":
            self.exit()

def run_tutorial():
    app = TutorialApp()
    app.run()
