import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

def compare_images():
    img_a_path = 'standard_A.png'
    img_b_path = 'standard_B.png'
    
    if not os.path.exists(img_a_path) or not os.path.exists(img_b_path):
        print("Error: One or both images not found.")
        return

    img_a = mpimg.imread(img_a_path)
    img_b = mpimg.imread(img_b_path)

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    
    axes[0].imshow(img_a)
    axes[0].axis('off')
    axes[0].set_title('Standard A', fontsize=20)
    
    axes[1].imshow(img_b)
    axes[1].axis('off')
    axes[1].set_title('Standard B', fontsize=20)
    
    plt.tight_layout()
    plt.savefig('standard_A_vs_B_comparison.png', dpi=300)
    print("Comparison image saved as 'standard_A_vs_B_comparison.png'")

if __name__ == "__main__":
    compare_images()
