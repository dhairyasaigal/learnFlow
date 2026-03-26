import llm
import os
print("API KEY PRESENT:", bool(os.getenv("OPENROUTER_API_KEY")))
try:
    res = llm.generate_questions("Quadratic Equations")
    print("OUTPUT:", res)
except Exception as e:
    print("FATAL ERROR:", e)
