import io
import sys
import base64
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from .dataset_manager import DatasetManager
import logging

logger = logging.getLogger(__name__)

class CodeExecutor:
    def __init__(self, data_path: str = "datasets"):
        self.output = ""
        self.error = None
        self.figures = []
        self.dataset_manager = DatasetManager(data_path)
        self.execution_context = {}
        
    def _capture_output(self):
        self.output_buffer = io.StringIO()
        sys.stdout = self.output_buffer
        
    def _restore_output(self):
        sys.stdout = sys.__stdout__
        self.output = self.output_buffer.getvalue()
        self.output_buffer.close()
    
    def _save_current_figure(self):
        fig_nums = plt.get_fignums()
        if fig_nums:
            for fig_num in fig_nums:
                fig = plt.figure(fig_num)
                if fig is not None:
                    img_buffer = io.BytesIO()
                    fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, 
                               facecolor='white', edgecolor='none')
                    img_buffer.seek(0)
                    img_str = base64.b64encode(img_buffer.getvalue()).decode()
                      # Check if image has meaningful content (remove arbitrary 1000 char limit)
                    if len(img_str) > 100:  # Very minimal check for actual image data
                        self.figures.append({
                            'type': 'matplotlib',
                            'data': img_str
                        })
                        logger.info(f"Matplotlib figure captured (size: {len(img_str)} chars)")
                    else:
                        logger.warning(f"Figure too small to be meaningful (size: {len(img_str)} chars)")
                    img_buffer.close()
                    plt.close(fig)
                    
    def _handle_plotly_figure(self, fig):
        plotly_json = json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
        self.figures.append({
            'type': 'plotly',
            'data': plotly_json
        })
        logger.info("Plotly figure captured and added to results")
        
    def execute_code_block(self, code: str, uploaded_filename: str = None, block_index: int = 0) -> dict:
        """Execute a single code block and return results immediately"""
        logger.info(f"Executing code block {block_index + 1}")
        
        self.output = ""
        self.error = None
        self.figures = []
        
        matplotlib.use('Agg')
        
        # Setup data context
        df = self._setup_data_context(uploaded_filename)
        namespace = self._create_namespace(df)
        
        try:
            self._capture_output()
            plt.ioff()
              # Execute the code block
            exec(code, namespace)
            
            # Capture any matplotlib figures (both show_plot() and auto-capture)
            self._save_current_figure()
            
            # Auto-capture any remaining figures not captured by show_plot()
            remaining_figs = plt.get_fignums()
            if remaining_figs and not self.figures:
                logger.info("Auto-capturing remaining figures not captured by show_plot()")
                self._save_current_figure()
              # Log results with debugging info
            if self.figures:
                logger.info(f"Generated {len(self.figures)} figure(s) in block {block_index + 1}")
                for i, fig in enumerate(self.figures):
                    logger.info(f"  Figure {i+1}: type={fig['type']}, data_size={len(fig['data'])} chars")
            else:
                logger.warning(f"No figures captured in block {block_index + 1}! Check:")
                logger.warning("  - Does code call show_plot()?")
                logger.warning("  - Is data available for plotting?")
                logger.warning("  - Are there any errors in the plotting code?")
            
            if self.output.strip():
                logger.info(f"Code block {block_index + 1} produced output: {self.output[:100]}...")
                
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error in code block {block_index + 1}: {self.error}")
        finally:
            self._restore_output()
            plt.ion()
        
        return {
            'block_index': block_index,
            'output': self.output,
            'error': self.error,
            'figures': self.figures,
            'has_plots': len(self.figures) > 0
        }
    
    def _setup_data_context(self, uploaded_filename: str = None):
        """Setup the data context for code execution"""
        df = None
        if uploaded_filename:
            df = self.dataset_manager.load_dataset(uploaded_filename)
            if df is None:
                try:
                    example_manager = DatasetManager("example_data")
                    df = example_manager.load_dataset(uploaded_filename)
                except:
                    pass
        
        if df is None:
            df = self.dataset_manager.auto_detect_dataset()
            
        if df is None:
            try:
                example_manager = DatasetManager("example_data")
                df = example_manager.auto_detect_dataset()
            except:
                pass
                
        return df
    
    def _create_namespace(self, df):
        """Create the execution namespace with all necessary imports and data"""
        namespace = {
            'pd': pd, 'np': np, 'plt': plt, 'sns': sns, 'px': px, 'go': go,
            'show_plot': self._save_current_figure,
            'show_plotly': self._handle_plotly_figure,
            'df': df, 'data': df, 'dataset': df,
        }
        
        # Add all available datasets to namespace
        available_datasets = self.dataset_manager.get_available_datasets()
        for dataset_file in available_datasets:
            dataset_name = dataset_file.split('.')[0]
            dataset_df = self.dataset_manager.load_dataset(dataset_file)
            if dataset_df is not None:
                namespace[dataset_name] = dataset_df
        
        # Add example datasets
        try:
            example_manager = DatasetManager("example_data")
            example_datasets = example_manager.get_available_datasets()
            for dataset_file in example_datasets:
                dataset_name = f"example_{dataset_file.split('.')[0]}"
                dataset_df = example_manager.load_dataset(dataset_file)
                if dataset_df is not None:
                    namespace[dataset_name] = dataset_df
        except:
            pass
            
        return namespace
        
    def execute(self, code: str, uploaded_filename: str = None) -> dict:
        """Legacy execute method for backward compatibility"""
        self.output = ""
        self.error = None
        self.figures = []
        
        matplotlib.use('Agg')
        
        df = self._setup_data_context(uploaded_filename)
        namespace = self._create_namespace(df)
        
        try:
            self._capture_output()
            plt.ioff()
            exec(code, namespace)
            self._save_current_figure()
        except Exception as e:
            self.error = str(e)
        finally:
            self._restore_output()
            plt.ion()
        
        return {
            'output': self.output,
            'error': self.error,
            'figures': self.figures
        }