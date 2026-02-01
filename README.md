# 🖥️ OS Scheduler Simulator (Visual CPU Scheduling)

## 📝 Project Overview
**OS Scheduler Simulator** is a high-performance desktop application designed to simulate and visualize how Operating Systems manage process execution. Built with **Python** and **PyQt5**, the tool provides an interactive environment to compare various CPU scheduling algorithms, helping users understand performance trade-offs through real-time **Gantt Charts** and statistical analysis.

---

## 🌟 Key Features

### 1. Supported Algorithms
The simulator implements four of the most critical scheduling strategies used in modern and classical OS:
* **FCFS (First Come First Serve):** Simple non-preemptive scheduling based on arrival time.
* **Non-Preemptive Priority:** Executes processes based on priority level without interruption.
* **Round Robin (RR):** Time-sharing scheduling with a customizable **Time Quantum**.
* **SRTF (Shortest Remaining Time First):** A preemptive version of SJF that always picks the process closest to completion.

### 2. Intelligent Process Generation
* **Statistical Modeling:** Instead of manual entry only, the system can generate processes using **Statistical Distributions** (Normal distribution for arrival/burst times, Poisson for priority).
* **Randomized Testing:** Allows for stress-testing algorithms with a large number of processes.

### 3. Visual Analytics & Reporting
* **Dynamic Gantt Charts:** Real-time visualization of the CPU timeline using **Matplotlib**.
* **Performance Comparison:** Automated bar graphs comparing **Average Waiting Time** and **Average Turnaround Time** across all algorithms.
* **Data Export:** Export simulation results directly to **CSV** or **PDF** for further documentation.

---

## 📊 Comparison & Observations
Based on simulations, the project provides insights into algorithm efficiency:
* **SRTF** typically yields the minimum average waiting time.
* **Round Robin** performance is highly sensitive to the chosen Time Quantum.
* **FCFS** is prone to the "Convoy Effect," where short processes wait for a long one.



---

## 🛠 Tech Stack
* **Language:** Python 3.x
* **GUI Framework:** PyQt5
* **Data Visualization:** Matplotlib, NumPy
* **I/O Operations:** File handling for `input.txt` and `output.txt`, CSV/PDF export.

---

## 🚀 Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/mohamed-saied-1/OS-Scheduler-Simulator.git]
    ```
2.  **Install Dependencies:**
    ```bash
    pip install PyQt5 matplotlib numpy
    ```
3.  **Run the Simulator:**
    ```bash
    python Os_Scheduler.py
    ```

---

## 📁 Project Structure
* `Os_Scheduler.py`: The main application logic and GUI.
* `input.txt` / `output.txt`: Sample data for batch process loading.
* `OS_Scheduler.pptx`: Technical presentation and findings.

---
**Core Systems Engineering © 2025.**
*Visualizing the heart of Operating Systems.*
