import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Excel automatically loads your highlighted table into a variable called 'df'.
# Replace the placeholder below if you highlighted a different range.
df = xl("A2:E6", headers=True)

# 1. Clean the Data 
# Set the first column (Markets) as the index
df = df.set_index(df.columns[0])
# Strip '%' signs and convert everything to numbers
df = df.replace('%', '', regex=True).astype(float)

# 2. Logic & Math
# Market sizes (Widths) are the first column
segment_pcts = df.iloc[:, 0].values
if segment_pcts.sum() <= 1.5: 
    segment_pcts = segment_pcts * 100
    
# Competitor shares (Heights) are the rest of the columns
plot_df = df.iloc[:, 1:].T 
if plot_df.max().max() <= 1.5: 
    plot_df = plot_df * 100

cum_widths = np.cumsum(segment_pcts)
x_edges = np.insert(cum_widths, 0, 0)

# 3. Plotting
fig, ax = plt.subplots(figsize=(10, 6))
bottoms = np.zeros(len(plot_df.columns))

# Use standard professional colors
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

for i, (competitor, row) in enumerate(plot_df.iterrows()):
    heights = row.values
    
    # Draw the blocks
    bars = ax.bar(x_edges[:-1], heights, width=segment_pcts, bottom=bottoms, 
                  align='edge', edgecolor='white', linewidth=2, label=competitor, 
                  color=colors[i % len(colors)])
    
    # Add the text inside the blocks
    for j, bar in enumerate(bars):
        if heights[j] >= 4: 
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + bar.get_height()/2, 
                    f"{heights[j]:.0f}%", 
                    ha='center', va='center', color='white', fontweight='bold')
    
    bottoms += heights

# 4. Formatting the Chart
ax.set_xlim(0, 100)
ax.set_ylim(0, 115) 
ax.set_xticks(x_edges[:-1] + segment_pcts/2)

# Create the top headers floating over the columns
top_labels = [f"{col}\n({pct:.0f}%)" for col, pct in zip(plot_df.columns, segment_pcts)]
ax.set_xticklabels(top_labels, fontweight='bold')

# Clean up the borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_yticks([]) 

plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(plot_df), frameon=False)
plt.tight_layout()

# Return the image to Excel
fig