Instructions:
As a solution architect, consider source testcases listed in the data/source_testcase.xlsx

Context:
The agent should generate the playwright python based POM oriented automation framework with exception handling.


Example:
Test Case ID	Test Scenario Description	Pre-condition	Test Steps	Test Data	Expected Result (ER)
TC_01	Verify that the user is able to login successfully with valid credentials	User is on the login page	"1. Launch browser and navigate to Sauce Demo URL
2. Enter valid username
3. Enter valid password
4. Click on Login button"	"Username: standard_user
Password: secret_sauce"	User is redirected to Products page and inventory items are displayed
TC_02	Verify that login is denied for locked out user	User is on the login page	"1. Enter Username: locked_out_user
2. Enter Password: secret_sauce
3. Click Login button"	"Username: locked_out_user
Password: secret_sauce"	Error message displayed: "Sorry, this user has been locked out."
TC_03	Verify that login fails with invalid username	User is on the login page	"1. Enter invalid username
2. Enter valid password
3. Click Login"	"Username: invalid_user
Password: secret_sauce"	Error message: "Epic sadface: Username and password do not match any user in this service"
TC_04	Verify that login fails with invalid password	User is on the login page	"1. Enter valid username
2. Enter invalid password
3. Click Login"	"Username: standard_user
Password: wrong_pass"	Error message: "Epic sadface: Username and password do not match any user in this service"

persona:

Output format:
playwright python based POM oriented automation framework with exception handling
The automation framework should consist of object folder for object repository, pages folder for pages from various pages, tests folder for test scripts

tone:
Highly professional and technical and covering all aspects of a agent development considering optimal token utilization, fast, security, clear comments, well structured, modular, extendable and simple

# 🤖 AI Test Compiler (Playwright Automation Agent)

## 📌 Overview

AI Test Compiler is a **phase-wise, agent-inspired system** that converts structured test cases into executable **Playwright Python automation scripts**.

It is designed to:

* Reduce manual test script creation
* Maintain reusable locator repositories
* Evolve into a self-improving automation agent

---

## 🎯 Key Features

* ✅ Convert test cases → Playwright scripts
* ✅ Modular pipeline architecture
* ✅ Object repository for locator reuse
* ✅ Template-based code generation
* ✅ Phase-wise evolution into AI agent

---

## 🧠 How It Works

```text
Test Case (CSV / JSON / Text)
        ↓
Parser
        ↓
Planner (Rules / LLM)
        ↓
Structured Steps (JSON)
        ↓
Locator Engine (Repo + Heuristics)
        ↓
Code Generator (Templates)
        ↓
Validator
        ↓
Playwright Runner
```

---

## 🏗️ Project Structure

```bash
project/
│
├── parser/            # Test case parsing
├── planner/           # Step → action conversion
├── locator/           # Locator engine + repository
├── generator/         # Playwright script generation
├── validator/         # Code validation
├── runner/            # Test execution
│
├── pages/             # (Phase 3+) Page Object Models
├── tests/             # Generated test scripts
│
├── config/            # Configurations
├── data/              # Input test cases
│
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-test-compiler.git
cd ai-test-compiler
```

---

### 2. Setup Environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install Playwright Browsers

```bash
python -m playwright install
```

---

### 5. Add Test Cases

Example (`data/testcases.csv`):

```csv
id,title,steps
AUTH_001,Login Test,"Enter email; Enter password; Click login"
```

---

### 6. Generate Scripts

```bash
python main.py
```

---

### 7. Run Tests

```bash
pytest tests/
```

---

## 🧩 Example Output

Generated Playwright script:

```python
def test_auth_001(page):
    page.goto("https://example.com")

    page.get_by_placeholder("Email").fill("test@example.com")
    page.get_by_placeholder("Password").fill("password123")
    page.get_by_role("button", name="Login").click()
```

---

## 🪜 Development Roadmap

### 🚀 Phase 1 — Core Pipeline

* Parser
* Rule-based planner
* Hardcoded locators
* Template generator
* Script execution

---

### 🚀 Phase 2 — Structured System

* Object repository (JSON)
* Multi-test support
* Validation layer
* Config system

---

### 🚀 Phase 3 — Intelligent System

* LLM-based planner (via OpenAI API)
* Dynamic locator generation
* Page Object Model (POM)
* Logging

---

### 🚀 Phase 4 — Agent Behavior

* Execution feedback loop
* Basic self-healing
* Retry mechanisms

---

### 🚀 Phase 5 — API Layer (Optional)

* FastAPI backend
* Script generation endpoints

---

## 🧠 Design Principles

* **Pipeline First** → Build working flow before intelligence
* **Deterministic → AI** → Start simple, then evolve
* **Modular Architecture** → Easy to extend
* **Incremental Complexity** → Avoid overengineering

---

## ⚠️ Limitations (Current Phase)

* Limited locator intelligence
* No self-healing (yet)
* Requires structured test cases
* Basic validation only

---

## 🔮 Future Enhancements

* AI-powered locator healing
* Memory-based learning
* CI/CD integration
* Dashboard UI
* Test analytics

---

## 🛠️ Tech Stack

* Python
* Playwright (Python)
* Pytest
* Jinja2
* (Phase 3+) OpenAI API

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Open a PR

---

## 📄 License

MIT License

---

## 💡 Inspiration

This project is inspired by the idea of building **agentic systems for test automation**, where AI assists in reducing manual effort while improving scalability.

---

## ⭐ Final Note

This project focuses on:

> **"Start simple → build working system → evolve into intelligence"**

---
