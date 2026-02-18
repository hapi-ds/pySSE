#!/usr/bin/env python3
"""
Test Data Generator for Sample Size Estimator

This script generates various types of statistical distributions for testing
the Sample Size Estimator application.

Usage:
    uv run python examples/generate_test_data.py

The script will create CSV files with different distribution types in the
examples/ directory.
"""

import numpy as np
from pathlib import Path


def generate_normal_data(
    mean: float = 10.0,
    std_dev: float = 0.5,
    size: int = 30,
    filename: str = "custom_normal.csv"
) -> None:
    """
    Generate normally distributed data.
    
    Args:
        mean: Population mean
        std_dev: Population standard deviation
        size: Number of samples
        filename: Output filename
    """
    data = np.random.normal(loc=mean, scale=std_dev, size=size)
    
    output_path = Path(__file__).parent / filename
    
    with open(output_path, 'w') as f:
        f.write(f"# Normal Distribution Data\n")
        f.write(f"# Mean: {mean}, Std Dev: {std_dev}, n: {size}\n")
        f.write(f"# Generated with numpy.random.normal\n")
        f.write(",".join([f"{x:.4f}" for x in data]))
    
    print(f"✓ Generated normal data: {filename}")
    print(f"  Mean: {np.mean(data):.4f}, Std Dev: {np.std(data, ddof=1):.4f}")


def generate_lognormal_data(
    mean: float = 1.0,
    sigma: float = 0.5,
    size: int = 40,
    filename: str = "custom_lognormal.csv"
) -> None:
    """
    Generate log-normally distributed data (right-skewed).
    
    Args:
        mean: Mean of underlying normal distribution
        sigma: Standard deviation of underlying normal distribution
        size: Number of samples
        filename: Output filename
    """
    data = np.random.lognormal(mean=mean, sigma=sigma, size=size)
    
    output_path = Path(__file__).parent / filename
    
    with open(output_path, 'w') as f:
        f.write(f"# Log-Normal Distribution Data (Right-Skewed)\n")
        f.write(f"# Underlying Normal: mean={mean}, sigma={sigma}, n={size}\n")
        f.write(f"# Use logarithmic transformation\n")
        f.write(",".join([f"{x:.4f}" for x in data]))
    
    print(f"✓ Generated log-normal data: {filename}")
    print(f"  Mean: {np.mean(data):.4f}, Median: {np.median(data):.4f}")


def generate_data_with_outliers(
    mean: float = 10.0,
    std_dev: float = 0.5,
    size: int = 38,
    num_outliers: int = 2,
    outlier_magnitude: float = 5.0,
    filename: str = "custom_outliers.csv"
) -> None:
    """
    Generate normal data with added outliers.
    
    Args:
        mean: Population mean for normal data
        std_dev: Population standard deviation
        size: Number of normal samples
        num_outliers: Number of outliers to add
        outlier_magnitude: How many std devs away from mean
        filename: Output filename
    """
    normal_data = np.random.normal(loc=mean, scale=std_dev, size=size)
    
    # Create outliers
    outliers = []
    for i in range(num_outliers):
        if i % 2 == 0:
            # High outlier
            outliers.append(mean + outlier_magnitude * std_dev)
        else:
            # Low outlier
            outliers.append(mean - outlier_magnitude * std_dev)
    
    data = np.concatenate([normal_data, outliers])
    np.random.shuffle(data)  # Mix outliers with normal data
    
    output_path = Path(__file__).parent / filename
    
    with open(output_path, 'w') as f:
        f.write(f"# Normal Data with Outliers\n")
        f.write(f"# Normal: mean={mean}, std_dev={std_dev}, n={size}\n")
        f.write(f"# Outliers: {num_outliers} at ±{outlier_magnitude} std devs\n")
        f.write(",".join([f"{x:.4f}" for x in data]))
    
    print(f"✓ Generated data with outliers: {filename}")
    print(f"  Expected outliers at: {mean - outlier_magnitude * std_dev:.2f} and {mean + outlier_magnitude * std_dev:.2f}")


def generate_uniform_data(
    low: float = 1.0,
    high: float = 11.0,
    size: int = 40,
    filename: str = "custom_uniform.csv"
) -> None:
    """
    Generate uniformly distributed data.
    
    Args:
        low: Lower bound
        high: Upper bound
        size: Number of samples
        filename: Output filename
    """
    data = np.random.uniform(low=low, high=high, size=size)
    
    output_path = Path(__file__).parent / filename
    
    with open(output_path, 'w') as f:
        f.write(f"# Uniform Distribution Data\n")
        f.write(f"# Range: [{low}, {high}], n={size}\n")
        f.write(f"# Try Box-Cox transformation\n")
        f.write(",".join([f"{x:.4f}" for x in data]))
    
    print(f"✓ Generated uniform data: {filename}")
    print(f"  Min: {np.min(data):.4f}, Max: {np.max(data):.4f}")


def generate_bimodal_data(
    mean1: float = 5.0,
    mean2: float = 15.0,
    std_dev: float = 0.5,
    size_per_mode: int = 20,
    filename: str = "custom_bimodal.csv"
) -> None:
    """
    Generate bimodal data (two distinct peaks).
    
    Args:
        mean1: Mean of first mode
        mean2: Mean of second mode
        std_dev: Standard deviation for both modes
        size_per_mode: Number of samples per mode
        filename: Output filename
    """
    mode1 = np.random.normal(loc=mean1, scale=std_dev, size=size_per_mode)
    mode2 = np.random.normal(loc=mean2, scale=std_dev, size=size_per_mode)
    
    data = np.concatenate([mode1, mode2])
    np.random.shuffle(data)
    
    output_path = Path(__file__).parent / filename
    
    with open(output_path, 'w') as f:
        f.write(f"# Bimodal Distribution Data\n")
        f.write(f"# Mode 1: mean={mean1}, Mode 2: mean={mean2}\n")
        f.write(f"# Std Dev: {std_dev}, n={size_per_mode * 2}\n")
        f.write(f"# Transformations likely to fail - use Wilks' method\n")
        f.write(",".join([f"{x:.4f}" for x in data]))
    
    print(f"✓ Generated bimodal data: {filename}")
    print(f"  Overall mean: {np.mean(data):.4f}, Std Dev: {np.std(data, ddof=1):.4f}")


def generate_exponential_data(
    scale: float = 2.0,
    size: int = 40,
    filename: str = "custom_exponential.csv"
) -> None:
    """
    Generate exponentially distributed data (right-skewed).
    
    Args:
        scale: Scale parameter (1/lambda)
        size: Number of samples
        filename: Output filename
    """
    data = np.random.exponential(scale=scale, size=size)
    
    output_path = Path(__file__).parent / filename
    
    with open(output_path, 'w') as f:
        f.write(f"# Exponential Distribution Data (Right-Skewed)\n")
        f.write(f"# Scale: {scale}, n={size}\n")
        f.write(f"# Use logarithmic or Box-Cox transformation\n")
        f.write(",".join([f"{x:.4f}" for x in data]))
    
    print(f"✓ Generated exponential data: {filename}")
    print(f"  Mean: {np.mean(data):.4f}, Median: {np.median(data):.4f}")


def main():
    """Generate all test data files."""
    print("=" * 60)
    print("Test Data Generator for Sample Size Estimator")
    print("=" * 60)
    print()
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    print("Generating test data files...\n")
    
    # Generate various distributions
    generate_normal_data(
        mean=10.0,
        std_dev=0.5,
        size=30,
        filename="generated_normal.csv"
    )
    
    generate_lognormal_data(
        mean=1.0,
        sigma=0.5,
        size=40,
        filename="generated_lognormal.csv"
    )
    
    generate_data_with_outliers(
        mean=10.0,
        std_dev=0.5,
        size=38,
        num_outliers=2,
        outlier_magnitude=5.0,
        filename="generated_outliers.csv"
    )
    
    generate_uniform_data(
        low=1.0,
        high=11.0,
        size=40,
        filename="generated_uniform.csv"
    )
    
    generate_bimodal_data(
        mean1=5.0,
        mean2=15.0,
        std_dev=0.5,
        size_per_mode=20,
        filename="generated_bimodal.csv"
    )
    
    generate_exponential_data(
        scale=2.0,
        size=40,
        filename="generated_exponential.csv"
    )
    
    print()
    print("=" * 60)
    print("✓ All test data files generated successfully!")
    print("=" * 60)
    print()
    print("Files created in examples/ directory:")
    print("  - generated_normal.csv")
    print("  - generated_lognormal.csv")
    print("  - generated_outliers.csv")
    print("  - generated_uniform.csv")
    print("  - generated_bimodal.csv")
    print("  - generated_exponential.csv")
    print()
    print("You can now use these files to test the application.")
    print("See examples/README.md for usage instructions.")


if __name__ == "__main__":
    main()
