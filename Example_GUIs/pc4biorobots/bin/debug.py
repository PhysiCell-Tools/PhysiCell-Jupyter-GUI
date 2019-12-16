import ipywidgets as widgets

# Provides a simple output widget to contain debug output.
# Works in callbacks and threads.
# Does not mess up other outputs.
debug_view = widgets.Output(layout={'border': '1px solid black'})
