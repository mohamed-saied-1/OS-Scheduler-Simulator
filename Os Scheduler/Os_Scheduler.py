import sys
import random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                            QVBoxLayout, QLabel, QTabWidget, QFileDialog,
                            QTableWidget, QTableWidgetItem, QHBoxLayout,
                            QComboBox, QSpinBox, QTextEdit, QHeaderView)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
import numpy as np

class ProcessGenerator:
    def __init__(self, num, mean_arrival, std_arrival, mean_burst, std_burst, lambda_priority):
        self.num = num
        self.mean_arrival = mean_arrival
        self.std_arrival = std_arrival
        self.mean_burst = mean_burst
        self.std_burst = std_burst
        self.lambda_priority = lambda_priority

    def generate(self):
        processes = []
        for i in range(1, self.num + 1):
            arrival = max(0, int(np.random.normal(self.mean_arrival, self.std_arrival)))
            burst = max(1, int(np.random.normal(self.mean_burst, self.std_burst)))
            priority = max(1, np.random.poisson(self.lambda_priority))
            processes.append((f"P{i}", arrival, burst, priority))
        return processes

class Scheduler:
    @staticmethod
    def fcfs(processes):
        processes.sort(key=lambda x: x[1])
        current_time = 0
        results = []
        for pid, arrival, burst, priority in processes:
            start_time = max(current_time, arrival)
            finish_time = start_time + burst
            turnaround = finish_time - arrival
            waiting = turnaround - burst
            results.append((pid, arrival, burst, priority, waiting, turnaround))
            current_time = finish_time
        return results
    @staticmethod
    def nph_priority(processes):
        # ????? ???????? ??? ???????? (?????? ?????) ?? ??? ??? ??????
        processes.sort(key=lambda x: (x[3], x[1]))
        current_time = 0
        results = []
        for pid, arrival, burst, priority in processes:
            start_time = max(current_time, arrival)
            finish_time = start_time + burst
            turnaround = finish_time - arrival
            waiting = turnaround - burst
            results.append((pid, arrival, burst, priority, waiting, turnaround))
            current_time = finish_time
        return results

    @staticmethod
    def round_robin(processes, quantum):
        # ????? ???????? ??? ??? ??????
        processes.sort(key=lambda x: x[1])
        queue = processes[:]
        current_time = 0
        results = []
        while queue:
            pid, arrival, burst, priority = queue.pop(0)
            if burst > quantum:
                queue.append((pid, arrival, burst - quantum, priority))  # ????? ??????? ??? ??????? ??? ????? ??? ????
                finish_time = current_time + quantum
                current_time = finish_time
            else:
                finish_time = current_time + burst
                current_time = finish_time
            turnaround = finish_time - arrival
            waiting = turnaround - burst
            results.append((pid, arrival, burst, priority, waiting, turnaround))
        return results

    @staticmethod
    def srtf(processes):
        import heapq
        processes.sort(key=lambda x: x[1])  # sort by arrival
        n = len(processes)
        time = 0
        remaining = [(arrival, burst, pid, priority) for pid, arrival, burst, priority in processes]
        heap = []
        results = []
        finished = set()
        start_times = {}
        remaining_burst = {pid: burst for pid, arrival, burst, priority in processes}

        while len(finished) < n:
            while remaining and remaining[0][0] <= time:
                arrival, burst, pid, priority = remaining.pop(0)
                heapq.heappush(heap, (remaining_burst[pid], arrival, pid, priority))

            if heap:
                burst_left, arrival, pid, priority = heapq.heappop(heap)

                if pid not in start_times:
                    start_times[pid] = time

                time += 1
                remaining_burst[pid] -= 1

                if remaining_burst[pid] > 0:
                    heapq.heappush(heap, (remaining_burst[pid], arrival, pid, priority))
                else:
                    finish_time = time
                    turnaround = finish_time - arrival
                    waiting = turnaround - processes[[p[0] for p in processes].index(pid)][2]  # original burst
                    results.append((pid, arrival, processes[[p[0] for p in processes].index(pid)][2], priority, waiting, turnaround))
                    finished.add(pid)
            else:
                time += 1

        return results


class SchedulerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OS Scheduler Simulator")
        self.setGeometry(150, 80, 1000, 700)

        self.setStyleSheet("""
            QWidget {
            background-color: #1E1E2F;
            color: #D1D5DB;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            }
    
            QPushButton {
            background-color: #4CAF50;
            border: none;
            
            padding: 12px 20px;
            font-size: 14px;
            border-radius: 5px;
            transition: background-color 0.3s ease, transform 0.3s ease;
            }

            QPushButton:hover {
            background-color: #45a049;
            transform: scale(1.05);
            }

            QTableWidget {
            background-color: #2F3741;
            gridline-color: #444444;
            color: #E4E4E4;
            font-size: 12px;
            }

            QHeaderView::section {
            background-color: #3C4A5B;
            color: #D1D5DB;
            padding: 8px;
            border: 1px solid #444;
            font-weight: bold;
            }

            QTableWidget::item {
            background-color: #2F3741;
            color: #E4E4E4;
            padding: 8px;
            }


            QTableWidget::item:selected {
            background-color: #3A4A62;
            color: white;
            }

            QTextEdit, QLineEdit, QComboBox, QSpinBox {
            background-color: #2C353D;
            border: 1px solid #3E4A59;
            border-radius: 3px;
            padding: 8px;
            color: #D1D5DB;
            }

            QComboBox, QSpinBox {
            padding: 6px;
            }

        QLabel {
        color: #E4E4E4;
        font-size: 14px;
        }

        QTabWidget {
        background-color: #2F3741;
        font-size: 14px;
        color: #E4E4E4;
        }

        QTabWidget::pane {
        border-top: 2px solid #3C4A5B;
        }

        QTabBar::tab {
        background-color: #3C4A5B;
        padding: 10px;
        margin-right: 2px;
        border-radius: 5px;
        } 

        QTabBar::tab:selected {
        background-color: #4CAF50;
        }

        QSpinBox::up-button, QSpinBox::down-button {
        border: none;
        background-color: #3C4A5B;
        color: #E4E4E4;
        padding: 6px;
        }

        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: #4CAF50;
        }
    
        
        """)


        font = QFont("Segoe UI", 10)
        self.setFont(font)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.init_process_tab()
        self.init_scheduler_tab()
        self.init_gantt_tab()
        self.init_comparison_tab()
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_layout.addWidget(self.tabs)
        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.show_about) 
        about_btn.setFixedWidth(100)  # ??????? ?????
        main_layout.addWidget(about_btn, alignment=Qt.AlignLeft)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        about_btn = QPushButton("Reset")
        about_btn.clicked.connect(self.reset_all) 
        about_btn.setFixedWidth(100)  # ??????? ?????
        main_layout.addWidget(about_btn, alignment=Qt.AlignRight)


    def init_gantt_tab(self):
        self.gantt_tab = QWidget()
        layout = QVBoxLayout()
        self.gantt_canvas = FigureCanvas(Figure(figsize=(10, 4)))
        layout.addWidget(self.gantt_canvas)
        self.gantt_tab.setLayout(layout)
        self.tabs.addTab(self.gantt_tab, " Gantt Chart")
    
    def draw_gantt_chart(self, results):
        self.gantt_canvas.figure.clear()
        ax = self.gantt_canvas.figure.add_subplot(111)

        y = 0
        for process in results:
            pid, arrival, burst, priority, waiting, turnaround = process
            start = arrival + waiting
            end = start + burst
            ax.barh(y, burst, left=start, height=0.5, label=pid)
            ax.text(start + burst / 2, y, pid, va='center', ha='center', color='white', fontsize=9)
            y += 1

        ax.set_xlabel("Time")
        ax.set_yticks([])
        ax.set_title("Gantt Chart")
        ax.grid(True)
        self.gantt_canvas.draw()

    def init_process_tab(self):
        self.process_tab = QWidget()
        layout = QVBoxLayout()

        self.load_label = QLabel(" Choose Input File: (or enter manually)")
        layout.addWidget(self.load_label)

        load_btn = QPushButton("Load Input File")
        load_btn.clicked.connect(self.load_input_file)
        layout.addWidget(load_btn)

        load_btn = QPushButton("Save Output File")
        load_btn.clicked.connect(self.save_output_file)
        layout.addWidget(load_btn)

        generate_btn = QPushButton(" Generate Processes")
        generate_btn.clicked.connect(self.generate_processes)
        layout.addWidget(generate_btn)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.process_tab.setLayout(layout)
        self.tabs.addTab(self.process_tab, " Process Generator")
    
    

    def init_scheduler_tab(self):
        self.scheduler_tab = QWidget()
        layout = QVBoxLayout()

        algo_layout = QHBoxLayout()
        self.algo_box = QComboBox()
        self.algo_box.addItems([
            "First Come First Serve (FCFS)",
            "Non-Preemptive Priority",
            "Round Robin",
            "Shortest Remaining Time First (SRTF)"
        ])
        algo_layout.addWidget(QLabel(" Choose Algorithm:"))
        algo_layout.addWidget(self.algo_box)

        self.quantum_input = QSpinBox()
        self.quantum_input.setMinimum(1)
        self.quantum_input.setValue(2)
        algo_layout.addWidget(QLabel(" Quantum (if RR):"))
        algo_layout.addWidget(self.quantum_input)

        layout.addLayout(algo_layout)

        run_btn = QPushButton(" Run Scheduling")
        run_btn.clicked.connect(self.run_scheduling)
        layout.addWidget(run_btn)
        reset_btn = QPushButton(" Reset All")
        reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(reset_btn)


        self.result_table = QTableWidget()
        self.result_table.setAlternatingRowColors(True)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.result_table)

        self.analysis_box = QTextEdit()
        self.analysis_box.setReadOnly(True)
        export_btn = QPushButton(" Export Results")
        export_btn.clicked.connect(self.export_results)
        layout.addWidget(export_btn)

        layout.addWidget(QLabel(" Analysis:"))
        layout.addWidget(self.analysis_box)

        self.scheduler_tab.setLayout(layout)
        self.tabs.addTab(self.scheduler_tab, " Scheduler")

    def load_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Input File")
        if file_name:
            with open(file_name, 'r') as file:
                lines = file.readlines()
                self.num_processes = int(lines[0])
                self.mean_arrival, self.std_arrival = map(float, lines[1].split())
                self.mean_burst, self.std_burst = map(float, lines[2].split())
                self.lambda_priority = float(lines[3])



    def save_output_file(self):
        # Open file dialog to save the file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Process List", "", "Text Files (*.txt);;All Files (*)")
        if not file_path:
            return  # User canceled

        # Get number of rows and columns from the table where processes are listed
        num_rows = self.table.rowCount()  # or self.processTable if that's your widget
        num_cols = self.table.columnCount()
        
        if num_rows == 0:
            QMessageBox.warning(self, "Warning", "No processes to copy.")
            return

        try:
            # Open the file for writing
            with open(file_path, 'w') as file:
                # Write the number of processes
                file.write(f"{num_rows}\n")
                
                # Write each process's data (ID, arrival time, burst time, priority)
                for row in range(num_rows):
                    line = []
                    for col in range(num_cols):
                        item = self.table.item(row, col)  # or self.processTable
                        # Ensure that we handle None (empty cells) by using an empty string
                        line.append(item.text() if item else "0")
                    # Write the row data to the file, separated by spaces
                    file.write(" ".join(line) + "\n")

            # Inform the user that the file has been saved
            QMessageBox.information(self, "Success", f"Process list saved to:\n{file_path}")
        
        except Exception as e:
            # Handle any errors during file writing
            QMessageBox.critical(self, "Error", f"Failed to write file:\n{str(e)}")



    def export_results(self):
        if self.result_table.rowCount() == 0:
            self.analysis_box.setText(" No results to export!")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "CSV Files (*.csv);;PDF Files (*.pdf)", options=options)
    
        if file_name:
            if file_name.endswith(".csv"):
                with open(file_name, 'w') as file:
                    headers = [self.result_table.horizontalHeaderItem(i).text() for i in range(self.result_table.columnCount())]
                    file.write(','.join(headers) + '\n')
                    for row in range(self.result_table.rowCount()):
                        row_data = []
                        for col in range(self.result_table.columnCount()):
                            item = self.result_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        file.write(','.join(row_data) + '\n')
                self.analysis_box.setText(f"? Results exported to {file_name}")
        
            elif file_name.endswith(".pdf"):
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.pdfgen import canvas

                    c = canvas.Canvas(file_name, pagesize=letter)
                    width, height = letter
                    c.setFont("Helvetica", 10)
                    y = height - 40

                    headers = [self.result_table.horizontalHeaderItem(i).text() for i in range(self.result_table.columnCount())]
                    c.drawString(40, y, "   ".join(headers))
                    y -= 20

                    for row in range(self.result_table.rowCount()):
                        row_data = []
                        for col in range(self.result_table.columnCount()):
                            item = self.result_table.item(row, col)
                            row_data.append(item.text() if item else "")
                        c.drawString(40, y, "   ".join(row_data))
                        y -= 20
                        if y < 40:
                            c.showPage()
                            y = height - 40

                    c.save()
                    self.analysis_box.setText(f"Results exported to {file_name}")

                except ImportError:
                    self.analysis_box.setText(" Install reportlab to export as PDF (pip install reportlab)")


    def generate_processes(self):
        try:
            _ = self.num_processes
            _ = self.mean_arrival
            _ = self.std_arrival
            _ = self.mean_burst
            _ = self.std_burst
            _ = self.lambda_priority
        except AttributeError:
            QMessageBox.critical(self, "Missing Data", "Please load a process configuration file first before generating processes.")
            return

        
        gen = ProcessGenerator(self.num_processes, self.mean_arrival, self.std_arrival,
                                self.mean_burst, self.std_burst, self.lambda_priority)
        self.processes = gen.generate()

        self.table.setRowCount(len(self.processes))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Process ID", "Arrival Time", "Burst Time", "Priority"])

        for row, (pid, arrival, burst, priority) in enumerate(self.processes):
            self.table.setItem(row, 0, QTableWidgetItem(pid))
            self.table.setItem(row, 1, QTableWidgetItem(str(arrival)))
            self.table.setItem(row, 2, QTableWidgetItem(str(burst)))
            self.table.setItem(row, 3, QTableWidgetItem(str(priority)))

    def init_comparison_tab(self):
        self.compare_tab = QWidget()
        layout = QVBoxLayout()

        run_all_btn = QPushButton(" Run All Algorithms")
        run_all_btn.clicked.connect(self.compare_all_algorithms)
        layout.addWidget(run_all_btn)

        self.comparison_chart = FigureCanvas(Figure(figsize=(5, 4)))
        self.ax = self.comparison_chart.figure.add_subplot(111)
        layout.addWidget(self.comparison_chart)

    # ? ????? ???? ???????
        self.analysis_table = QTableWidget()    
        self.analysis_table.setColumnCount(3)
        self.analysis_table.setHorizontalHeaderLabels(["Algorithm", "Avg Waiting Time", "Avg Turnaround Time"])
        self.analysis_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.analysis_table)

        self.compare_tab.setLayout(layout)
        self.tabs.addTab(self.compare_tab, "Compare and Analyze")


    def compare_all_algorithms(self):
        QTimer.singleShot(100, self._perform_comparison)

    def _perform_comparison(self):
        if not hasattr(self, 'processes') or not self.processes:
            QMessageBox.warning(self, "?? Missing Processes", "Please generate or load processes before comparing algorithms.")
            return

        self.analysis_table.setRowCount(0)
        self.ax.clear()

        algos = {
            "FCFS": Scheduler.fcfs,
            "Non-Preemptive Priority": Scheduler.nph_priority,
            "Round Robin": lambda p: Scheduler.round_robin(p, self.quantum_input.value()),
            "SRTF": Scheduler.srtf
            }

        waiting_times = []
        turnaround_times = []
        algo_names = []

        for name, func in algos.items():
            try:
                results = func(self.processes[:])
                wt = sum([r[4] for r in results]) / len(results)
                tat = sum([r[5] for r in results]) / len(results)

                waiting_times.append(wt)
                turnaround_times.append(tat)
                algo_names.append(name)

                row = self.analysis_table.rowCount()
                self.analysis_table.insertRow(row)
                self.analysis_table.setItem(row, 0, QTableWidgetItem(name))
                self.analysis_table.setItem(row, 1, QTableWidgetItem(f"{wt:.2f}"))
                self.analysis_table.setItem(row, 2, QTableWidgetItem(f"{tat:.2f}"))
            except Exception as e:
                print(f"?? Error with algorithm {name}: {e}")

        x = np.arange(len(algo_names))
        width = 0.35
        self.ax.bar(x - width/2, waiting_times, width, label='Avg Waiting Time')
        self.ax.bar(x + width/2, turnaround_times, width, label='Avg Turnaround Time')

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(algo_names)
        self.ax.set_ylabel('Time')
        self.ax.set_title('Comparison of Scheduling Algorithms')
        self.ax.legend()

        self.comparison_chart.draw()


    def run_scheduling(self):
        if not hasattr(self, 'processes') or not self.processes:
            self.analysis_box.setText("Please generate processes first!")
            return

        algo = self.algo_box.currentText()
        if algo == "First Come First Serve (FCFS)":
            results = Scheduler.fcfs(self.processes[:])
        elif algo == "Non-Preemptive Priority":
            results = Scheduler.nph_priority(self.processes[:])
        elif algo == "Round Robin":
            quantum = self.quantum_input.value()
            results = Scheduler.round_robin(self.processes[:], quantum)
        elif algo == "Shortest Remaining Time First (SRTF)":
            results = Scheduler.srtf(self.processes[:])

        self.result_table.setRowCount(len(results))
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(["PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround"])

        total_waiting, total_turnaround = 0, 0
        for row, (pid, arrival, burst, priority, waiting, turnaround) in enumerate(results):
            self.result_table.setItem(row, 0, QTableWidgetItem(pid))
            self.result_table.setItem(row, 1, QTableWidgetItem(str(arrival)))
            self.result_table.setItem(row, 2, QTableWidgetItem(str(burst)))
            self.result_table.setItem(row, 3, QTableWidgetItem(str(priority)))
            self.result_table.setItem(row, 4, QTableWidgetItem(str(waiting)))
            self.result_table.setItem(row, 5, QTableWidgetItem(str(turnaround)))
            total_waiting += waiting
            total_turnaround += turnaround

        avg_waiting = total_waiting / len(results)
        avg_turnaround = total_turnaround / len(results)
        self.analysis_box.setText(f"Average Waiting Time: {avg_waiting:.2f}\nAverage Turnaround Time: {avg_turnaround:.2f}")
        self.draw_gantt_chart(results)

    
    def show_about(self):
        QMessageBox.information(self, "About Project", 
            "OS Scheduler Simulator\n\n"
            "This application simulates different CPU scheduling algorithms:\n"
            "- FCFS (First Come First Serve)\n"
            "- Non-Preemptive Priority\n"
            "- Round Robin\n"
            "- SRTF (Shortest Remaining Time First)\n\n"
            "Features:\n"
            "- Process generation using statistical distributions\n"
            "- Visualization via Gantt Charts\n"
            "- Comparison of algorithms using bar graphs\n"
            "- Export results to CSV and PDF\n\n"
            "Developed using Python and PyQt5.")   

    def reset_all(self):
        self.processes = []

    # Clear tables
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        self.result_table.clear()
        self.result_table.setRowCount(0)
        self.result_table.setColumnCount(0)

        self.analysis_table.setRowCount(0)

    # Reset input fields
        self.quantum_input.setValue(2)
        self.algo_box.setCurrentIndex(0)

    # Clear analysis text
        self.analysis_box.clear()

    # Clear plots
        self.gantt_canvas.figure.clear()
        self.gantt_canvas.draw()

        self.ax.clear()
        self.comparison_chart.draw()

    # Clear any saved config
        if hasattr(self, "num_processes"): del self.num_processes
        if hasattr(self, "mean_arrival"): del self.mean_arrival
        if hasattr(self, "std_arrival"): del self.std_arrival
        if hasattr(self, "mean_burst"): del self.mean_burst
        if hasattr(self, "std_burst"): del self.std_burst
        if hasattr(self, "lambda_priority"): del self.lambda_priority

        QMessageBox.information(self, "Reset Done", "Application has been reset successfully.")
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = SchedulerGUI()
    gui.show()
    sys.exit(app.exec_())
    