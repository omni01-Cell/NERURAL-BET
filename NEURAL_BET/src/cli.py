# -*- coding: utf-8 -*-
"""
NEURAL BET CLI Entry Point.
Allows launching the TUI from anywhere with: neuralbet
"""
import sys
import os

# Ensure the project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """CLI entry point - launches the TUI."""
    from src.tui import NeuralBetApp
    
    app = NeuralBetApp()
    app.run()


def run_pipeline():
    """Alternative entry point - runs the headless pipeline."""
    import asyncio
    from src.main import main as pipeline_main
    
    asyncio.run(pipeline_main())


if __name__ == "__main__":
    main()
