import importlib.util, pathlib

p = pathlib.Path("agents/core/planner_agent.py").resolve()
spec = importlib.util.spec_from_file_location("planner_agent", str(p))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

tests = [
    "what is in sandeep_internship_work.pdf file",
    "this is a test",
    "find email containing abc",
    "hi there",
    "when is the meeting",
    "show reminders",
    "summarize my emails",
    "what topics are covered",
    "which is better, python or java",
    "Which is better: 'Node.js' or 'Deno'?",
    "Compare C# and C++",
    "Show emails from Bharath",
]
for t in tests:
    print(t, "->", mod.decide_intent(t))
