
# Codeit-AI

Built as a hands-on project to explore AI-assisted developer tools.
AI-assisted code runner that can execute Python, explain logic, and debug errors using LLM reasoning.

---

## ✨ Features

✔ Run Python code  
✔ Explain code using LLM reasoning  
✔ Debug runtime errors (with suggested fixes)  
✔ Supports Python `input()`  
✔ Clean UI (React + Monaco Editor)  
✔ AI backend powered by Groq  

---

## 🧰 Tech Stack

**Frontend:** React, Vite, Monaco Editor  
**Backend:** Python, Flask  
**AI Model:** Groq (Llama 3.3-70B Versatile)  

---

## 🚧 Project Status

Currently in polishing phase for internship submission.

### 🟢 Core Functionality Completed
- Code execution
- Input handling
- Explain feature (LLM)
- Debug feature (LLM)
- Basic UI flow

### 🟡 Polishing & Documentation
- UI refinements
- Example programs
- Demo video
- README improvements

### 🔜 Potential Future Enhancements
- Multi-language support (C++, Java, JS)
- Execution sandboxing
- Persistent workspace/history

![status](https://img.shields.io/badge/build-passing-brightgreen)

AI-assisted code runner that can execute Python, explain logic, and debug errors using LLM reasoning.

---

## ✨ Features

✔ Run Python code  
✔ Explain code using LLM reasoning  
✔ Debug runtime errors (with suggested fixes)  
✔ Supports Python `input()`  
✔ Clean UI (React + Monaco Editor)  
✔ AI backend powered by Groq  

---

## 🧰 Tech Stack

**Frontend:** React, Vite, Monaco Editor  
**Backend:** Python, Flask  
**AI Model:** Groq (Llama 3.3-70B Versatile)  

---

## 🚧 Project Status

Currently in polishing phase for internship submission.

### 🟢 Core Functionality Completed
- Code execution
- Input handling
- Explain feature (LLM)
- Debug feature (LLM)
- Basic UI flow

### 🟡 Polishing & Documentation
- UI refinements
- Example programs
- Demo video
- README improvements

### 🔜 Potential Future Enhancements
- Multi-language support (C++, Java, JS)
- Execution sandboxing
- Persistent workspace/history

![status](https://img.shields.io/badge/build-passing-brightgreen)






## 🧪 Usage / Demo Flow

1. Write Python code in the editor
2. (Optional) Provide input values for programs that use `input()`
3. Click **Run** to execute the code
4. Click **Explain** to get an LLM-based code explanation
5. Click **Debug** to analyze errors and receive suggested fixes


##Example 1 — Basic I/O

n = int(input())
print(n * 2)

Input:
5

Output:
10


##Example 2 — Student Marks (Multi-line Input)

n = int(input("How many students? "))

students = []
total = 0

for i in range(n):
    raw = input("Enter name & marks (e.g., Aisha 90): ")
    name, marks = raw.split()
    marks = int(marks)
    students.append((name, marks))
    total += marks

avg = total / n

print("\n--- RESULTS ---")
for name, marks in students:
    print(f"{name} scored {marks}")

print(f"\nClass Average = {avg:.2f}")

Input:
3
Aisha 90
Rahul 85
John 70

Output:
--- RESULTS ---
Aisha scored 90
Rahul scored 85
John scored 70

Class Average = 81.67


##Example 3 — Error + Debug

n = int(input())
print(n + "10")

Input:
5

Error:
TypeError: unsupported operand type(s) for +: 'int' and 'str'

Debug Output (LLM):
The error occurs because you’re adding an integer to a string.
Convert input to int or convert 10 to string.
Correct version:
print(n + 10)





