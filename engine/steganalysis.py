import cv2
import numpy as np
import os

def check_stego(image_path):
    """
    Performs a Chi-Square statistical test on the Least Significant Bits (LSB)
    of an image to detect potential steganography.
    Manual implementation to avoid scipy dependency on Android.
    """
    try:
        if not os.path.exists(image_path):
            return False
            
        img = cv2.imread(image_path)
        if img is None:
            return False
            
        # Convert to grayscale for initial statistical check
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pixels = gray.flatten()
        
        # Count pixel intensities
        counts = np.bincount(pixels, minlength=256)
        
        chi_stat = 0.0
        degrees_of_freedom = 0
        
        for i in range(0, 256, 2):
            c_2i = float(counts[i])
            c_2i_plus_1 = float(counts[i+1])
            
            pair_sum = c_2i + c_2i_plus_1
            
            if pair_sum > 10: # Significance threshold
                # Chi-square term: (O-E)^2 / E
                # For a pair (c1, c2), expected is (c1+c2)/2 each.
                # Simplified: (c1 - c2)^2 / (c1 + c2)
                term = ((c_2i - c_2i_plus_1) ** 2) / pair_sum
                chi_stat += term
                degrees_of_freedom += 1
        
        if degrees_of_freedom < 5:
            return False
            
        # Instead of calculating full p-value (which requires gamma function),
        # we use the fact that p > 0.95 means chi_stat is very small 
        # relative to degrees of freedom.
        # Rule of thumb for PoVs: If chi_stat is significantly SMALLER than DoF,
        # it indicates steganography (the even/odd counts are too close).
        
        # For DoF around 100, if chi_stat < DoF * 0.7, it's suspicious.
        # But specifically, p > 0.95 means chi_stat is smaller than the 5th percentile 
        # of the chi-square distribution.
        
        # Approximating critical values for high p-values (suspiciously uniform):
        # A very low chi_stat compared to degrees_of_freedom means high p-value.
        # Typical threshold for LSB detection:
        is_suspicious = chi_stat < (degrees_of_freedom * 0.6)
        
        return is_suspicious
        
    except Exception as e:
        print(f"Error analyzing image {image_path}: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = check_stego(sys.argv[1])
        print(f"Stego Detected: {res}")
