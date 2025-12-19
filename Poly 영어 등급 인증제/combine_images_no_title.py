import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
import os

def main():
    base_dir = r"c:\Users\user\projects\LT_data_analysis\LT_등급제"
    output_file = r"c:\Users\user\projects\LT_data_analysis\LT_Grade_Analysis_Combined_NoTitle.png"
    
    # Image paths
    img_paths = {
        'abs_crit': os.path.join(base_dir, "LT_ELE_절대평가.png"),
        'abs_dist': os.path.join(base_dir, "LT_ELE_절대평가_분포.png"),
        'rel_crit': os.path.join(base_dir, "LT_ELE_상대평가.png"),
        'rel_dist': os.path.join(base_dir, "LT_ELE_상대평가_분포.png")
    }
    
    # Check if files exist
    for key, path in img_paths.items():
        if not os.path.exists(path):
            print(f"Error: File not found - {path}")
            return

    # Load images
    images = {k: mpimg.imread(v) for k, v in img_paths.items()}
    
    # Create figure
    # We want a tight layout with no titles.
    fig = plt.figure(figsize=(16, 12))
    
    # 2x2 Grid with minimal spacing
    gs = GridSpec(2, 2, figure=fig, wspace=0.05, hspace=0.05)
    
    # --- Top Row: Absolute Evaluation ---
    # Top Left: Absolute Criteria
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(images['abs_crit'])
    ax1.axis('off')
    
    # Top Right: Absolute Distribution
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.imshow(images['abs_dist'])
    ax2.axis('off')
    
    # --- Bottom Row: Relative Evaluation ---
    # Bottom Left: Relative Criteria
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.imshow(images['rel_crit'])
    ax3.axis('off')
    
    # Bottom Right: Relative Distribution
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.imshow(images['rel_dist'])
    ax4.axis('off')
    
    # Save output with tight bounding box to remove extra white space
    plt.savefig(output_file, dpi=150, bbox_inches='tight', pad_inches=0.1)
    print(f"Combined image saved to: {output_file}")

if __name__ == "__main__":
    main()
