"""
State management for analyzer connection.
"""

class AnalyzerState:
    def __init__(self):
        self.connected = False
        self.last_report = None
