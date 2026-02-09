"""Charts panel with Matplotlib."""
import matplotlib
matplotlib.use('qtagg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget


class ChartCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 4), dpi=100)
        super().__init__(self.fig)

    def plot_bar(self, labels, values):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.bar(labels, values, color='#2563eb', alpha=0.8)
        ax.set_xlabel('Equipment Type')
        ax.set_ylabel('Count')
        ax.set_title('Equipment Type Distribution')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        self.draw()

    def plot_line(self, labels, values):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(range(len(values)), values, 'o-', color='#22c55e', linewidth=2)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_xlabel('Equipment')
        ax.set_ylabel('Flowrate')
        ax.set_title('Flowrate Trends')
        self.draw()

    def plot_pie(self, labels, values):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        colors = ['#2563eb', '#22c55e', '#eab308', '#ef4444', '#a855f7', '#ec4899']
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)], startangle=90)
        ax.set_title('Type Percentages')
        self.draw()


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.bar_canvas = ChartCanvas()
        self.line_canvas = ChartCanvas()
        self.pie_canvas = ChartCanvas()
        self.tabs.addTab(self.bar_canvas, 'Type Distribution')
        self.tabs.addTab(self.line_canvas, 'Flowrate Trends')
        self.tabs.addTab(self.pie_canvas, 'Type %')
        layout.addWidget(self.tabs)

    def set_data(self, dataset):
        equipment = dataset.get('equipment_list', []) or []
        type_summaries = dataset.get('type_summaries', []) or []

        if type_summaries:
            labels = [t['equipment_type'] for t in type_summaries]
            values = [t['count'] for t in type_summaries]
            self.bar_canvas.plot_bar(labels, values)
            self.pie_canvas.plot_pie(labels, values)

        if equipment:
            names = [e.get('equipment_name', f'#{i+1}') for i, e in enumerate(equipment)]
            flowrates = [float(e.get('flowrate', 0)) for e in equipment]
            self.line_canvas.plot_line(names, flowrates)
