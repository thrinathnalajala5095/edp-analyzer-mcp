# edp-analyzer-mcp

# AI-Driven DisplayPort/eDP Protocol Analyzer

An AI-integrated automation framework for hardware-based DisplayPort/eDP protocol debugging.

This project demonstrates how a Model Context Protocol (MCP) server can connect an AI assistant to an external analyzer, automate captures, parse protocol-level diagnostics, and generate structured health reports for DisplayPort/eDP links.

It is designed to reduce manual debugging time and make low-level display diagnostics easier to access, understand, and reuse.

---

## Overview

Traditional DisplayPort/eDP debugging often requires:

- manually connecting to analyzer hardware
- configuring captures
- exporting raw logs
- reviewing AUX and main-link traffic by hand
- correlating failures across link training, DSC, and FEC

This project automates that workflow by exposing analyzer operations as MCP tools that an AI assistant can call directly.

With this setup, an engineer can request:

- connect to the analyzer
- run a capture
- generate a protocol report
- check link health
- reload a previous capture
- retrieve the last report for follow-up analysis

---

## Key Features

- Analyzer connection management
- Automated capture orchestration
- Structured protocol report generation
- Link health analysis
- Offline capture loading
- Cached report retrieval
- Async-compatible client workflow
- Strongly typed Pydantic report models

---

## Architecture

```text
+---------------------+        +-----------------------+        +----------------------+
|   Engineer / User   | -----> |   AI Assistant        | -----> |   MCP Server         |
|  "Check link health"|        |   (Claude / Devmate)  |        |   (Python)           |
+---------------------+        +-----------------------+        +----------+-----------+
                                                                          |
                                                                          |
                                                                          v
                                                           +---------------------------+
                                                           |   Analyzer Client         |
                                                           |   + State Manager         |
                                                           +-------------+-------------+
                                                                         |
                                                                         |
                                                                         v
                                                           +---------------------------+
                                                           |  Introspect eDP Analyzer  |
                                                           |  Hardware Capture Device   |
                                                           +-------------+-------------+
                                                                         |
                                                                         |
                                                                         v
                                                           +---------------------------+
                                                           | DisplayPort / eDP Link    |
                                                           | Under Test                |
                                                           +---------------------------+
````

---

## Data Flow

```text
1. User asks AI assistant to analyze display link
2. AI calls MCP tool
3. MCP server connects to analyzer
4. Analyzer runs capture
5. Capture data is parsed into structured models
6. Health engine evaluates protocol status
7. AI returns human-readable diagnostic report
```

---

## Example Workflow

```text
User:
"Connect to the analyzer and check if the eDP link is healthy."

AI Assistant:
1. connect_analyzer(host="192.168.1.100", port=5000)
2. capture_and_report(duration_ms=2000, trigger_mode="link_training")
3. analyze health
4. return structured summary
```

Example response:

```text
Link Training: SUCCESS
Link Rate: HBR3
Lane Count: 4

AUX Channel: OK
EDID Read: SUCCESS
Symbol Errors: 0
FEC Errors: 0

Overall Status: HEALTHY
Recommendation: Link is operating normally.
```

---

## Code Structure

```text
introspect_edp/
├── README.md
├── __init__.py
├── BUCK
│
├── analyzer_client.py
├── analyzer_state.py
├── tool_models.py
├── report_types.py
│
├── IntrospectConnectTool.py
├── IntrospectDisconnectTool.py
├── IntrospectCaptureAndReportTool.py
├── IntrospectLoadCaptureTool.py
├── IntrospectGetLastReportTool.py
├── IntrospectGetStatusTool.py
│
├── test_report_types.py
└── test_tools.py
```

---

## Module Responsibilities

### `analyzer_client.py`

Implements the analyzer interface and report-generation logic.

Responsibilities:

* connect/disconnect from analyzer
* start and stop capture
* wait for capture completion
* export raw capture data
* parse analyzer output
* generate structured report
* evaluate overall link health

---

### `analyzer_state.py`

Maintains singleton session state across MCP tool calls.

Responsibilities:

* active connection info
* current capture state
* cached report data
* last export path
* validation helpers for tool preconditions

---

### `tool_models.py`

Defines input and config models for MCP tools using Pydantic.

Examples:

* connect input
* capture input
* load-capture input
* analyzer config

---

### `report_types.py`

Defines the structured report schema.

Includes models for:

* link training status
* AUX transaction details
* AUX channel diagnostics
* main-link diagnostics
* DSC status
* FEC status
* top-level eDP report

---

### MCP Tool Files

#### `IntrospectConnectTool.py`

Connect to analyzer by hostname/IP and port.

#### `IntrospectDisconnectTool.py`

Disconnect analyzer and clear active state.

#### `IntrospectCaptureAndReportTool.py`

Primary workflow tool. Runs capture and returns a structured protocol report.

#### `IntrospectLoadCaptureTool.py`

Loads a previously saved capture and regenerates the report offline.

#### `IntrospectGetLastReportTool.py`

Returns the cached report from the last analysis session.

#### `IntrospectGetStatusTool.py`

Provides current analyzer/session state.

---

## MCP Tools

| Tool                                 | Purpose                           |
| ------------------------------------ | --------------------------------- |
| `introspect_connect_tool`            | Connect to analyzer               |
| `introspect_disconnect_tool`         | Disconnect from analyzer          |
| `introspect_capture_and_report_tool` | Run capture and generate report   |
| `introspect_load_capture_tool`       | Load saved capture                |
| `introspect_get_last_report_tool`    | Retrieve cached report            |
| `introspect_get_status_tool`         | Get connection and capture status |

---

## Report Model

The generated report includes five major diagnostic areas:

### 1. Link Training

* success/failure
* link rate
* lane count
* clock recovery
* channel equalization
* symbol lock
* interlane alignment

### 2. AUX Channel

* EDID read status
* DPCD reads/writes
* I2C-over-AUX activity
* NACK / DEFER / timeout counts
* notable transactions

### 3. Main Link

* frame count
* per-lane symbol errors
* disparity errors
* lane alignment errors
* blanking and active timing
* refresh rate
* bandwidth utilization

### 4. DSC Status

* enabled/disabled
* PPS detection
* slice dimensions
* bits per pixel
* compression ratio
* slice errors

### 5. FEC Status

* enabled/disabled
* readiness
* corrected errors
* decode errors
* parity errors per lane

---

## Health Analysis Engine

The project includes a rules-based health engine that classifies captures as:

* `HEALTHY`
* `WARNING`
* `ERROR`

### Example checks

* link training failed
* multiple training retries
* AUX timeouts
* EDID read failure
* symbol errors on main link
* lane alignment errors
* DSC slice errors
* FEC decode errors

### Example decision logic

```text
If any critical protocol failure is present:
    overall_health = ERROR

Else if non-critical warnings are present:
    overall_health = WARNING

Else:
    overall_health = HEALTHY
```

---

## Sequence Diagram

```text
User            AI Assistant         MCP Server         Analyzer Client        Hardware Analyzer
 |                    |                  |                    |                      |
 | ask for report     |                  |                    |                      |
 |------------------->|                  |                    |                      |
 |                    | tool call        |                    |                      |
 |                    |----------------->|                    |                      |
 |                    |                  | connect            |                      |
 |                    |                  |------------------->|                      |
 |                    |                  |                    | connect              |
 |                    |                  |                    |--------------------->|
 |                    |                  |                    |<---------------------|
 |                    |                  | capture request    |                      |
 |                    |                  |------------------->|                      |
 |                    |                  |                    | run capture          |
 |                    |                  |                    |--------------------->|
 |                    |                  |                    | parse results        |
 |                    |                  |<-------------------|                      |
 |                    | structured report|                    |                      |
 |                    |<-----------------|                    |                      |
 | human summary      |                  |                    |                      |
 |<-------------------|                  |                    |                      |
```

---

## Build

```bash
buck2 build fbcode//model_context_protocol/python_servers/introspect_edp:introspect_edp_mcp_server
```

---

## Tests

```bash
buck2 test fbcode//model_context_protocol/python_servers/introspect_edp:test_report_types
buck2 test fbcode//model_context_protocol/python_servers/introspect_edp:test_tools
```

---

## Current Status

* MCP architecture implemented
* report models implemented
* health analysis implemented
* tool interfaces implemented
* unit/integration tests added
* production SDK integration pending
* end-to-end hardware validation pending

---

## Future Improvements

* integrate actual analyzer SDK
* add HDCP, PSR, MST diagnostics
* support richer trigger modes
* enable regression comparison across captures
* add dashboards for repeated validation runs
* improve recommendation engine with historical pattern matching

---

## Use Cases

* DisplayPort/eDP link bring-up
* link training failure analysis
* AUX channel debugging
* DSC/FEC validation
* offline capture re-analysis
* AI-assisted protocol debugging workflows

---

## Impact

This project transforms display protocol validation from a manual analyzer-driven workflow into an AI-assisted diagnostic system.

Benefits include:

* faster debug turnaround
* standardized analyzer reporting
* better visibility beyond SoC logs
* easier reuse of protocol knowledge
* foundation for scalable hardware-validation automation

---


