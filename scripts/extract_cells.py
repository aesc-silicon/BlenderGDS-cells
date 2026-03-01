#!/usr/bin/env python3
"""
KLayout script to extract all top cells from a GDS file
and save each as an individual GDS file.

Usage:
  klayout -b -r extract_cells.py -rd input_gds=path/to/stdcells.gds
  klayout -b -r extract_cells.py -rd input_gds=path/to/stdcells.gds -rd output_dir=path/to/output
"""

import os
import sys
import pya

# --- Configuration ---
# input_gds: set via -rd input_gds=... on the command line
# output_dir: optional, defaults to same directory as input GDS

if not hasattr(pya.Application.instance().main_window(), "__class__") and "input_gds" not in dir():
    print("Error: Please provide input_gds via -rd input_gds=<path>")
    sys.exit(1)

input_path = input_gds  # noqa: F821 — injected by klayout -rd
output_path = output_dir if "output_dir" in dir() else os.path.dirname(os.path.abspath(input_path))  # noqa: F821

os.makedirs(output_path, exist_ok=True)

# --- Load the layout ---
layout = pya.Layout()
layout.read(input_path)

# --- Identify top cells ---
top_cells = [cell for cell in layout.top_cells()]

if not top_cells:
    print("No top cells found in the GDS file.")
    sys.exit(1)

print(f"Found {len(top_cells)} top cell(s) in: {input_path}")
print(f"Output directory: {output_path}\n")

# --- Export each top cell as its own GDS ---
for cell in top_cells:
    cell_name = cell.name

    # Create a new layout with only this cell and its hierarchy
    export_layout = pya.Layout()
    export_layout.dbu = layout.dbu

    # Copy the cell and all its dependencies into the new layout
    export_layout.cell(export_layout.add_cell(cell_name))
    src_cell_index = cell.cell_index()
    dst_cell_index = export_layout.cell_by_name(cell_name)

    # Use CellMapping to copy the full hierarchy
    cm = pya.CellMapping()
    cm.for_single_cell_full(export_layout, dst_cell_index, layout, src_cell_index)
    export_layout.copy_tree_shapes(layout, cm)

    # Also copy layer properties
    for li in layout.layer_indices():
        info = layout.get_info(li)
        if export_layout.find_layer(info) is None:
            export_layout.layer(info)

    # Save
    out_file = os.path.join(output_path, f"{cell_name}.gds")
    export_layout.write(out_file)
    print(f"  Saved: {out_file}")

print(f"\nDone. Exported {len(top_cells)} cell(s).")
