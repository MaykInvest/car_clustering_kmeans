### 📌 Executive Summary & Conclusion

#### 🎯 Project Overview
This project segments ~11,000 U.S. car models (1990–2018) into natural 
market groups using K-Means clustering — an unsupervised approach with 
no predefined categories and no target variable to predict.

#### 📊 Results — 3 Market Segments

| Cluster | Avg. HP | Cylinders | Highway MPG | City MPG | Avg. MSRP | Count |
|---|---|---|---|---|---|---|
| Efficient / Mainstream | 184 | 4.1 | 32.2 | 24.4 | $27,603 | 4,038 |
| High-Performance / Luxury | 330 | 6.9 | 22.6 | 15.9 | $61,242 | 5,438 |
| Historical (Pre-1997 Models) | 169 | 5.5 | 23.2 | 17.2 | $5,518 | 1,625 |

- **Efficient / Mainstream**: practical, fuel-conscious cars — best MPG, 
  moderate price
- **High-Performance / Luxury**: highest HP and price, lowest MPG — 
  sports and luxury vehicles
- **Historical (Pre-1997 Models)**: low price driven by model year, not 
  by design — confirmed by inspecting the actual years within this 
  cluster before naming it

#### 🔑 Key Modeling Decisions
1. **Outlier correction**: identified and removed a data entry error 
   (Audi listed at 354 highway MPG — physically implausible).
2. **Log-transformed MSRP**: reduced the distorting influence of a small 
   number of multi-million-dollar hypercars on distance calculations.
3. **Feature exclusions**: `make` and `popularity` were deliberately 
   left out, to avoid clustering on brand identity or brand-buzz rather 
   than actual car specifications.
4. **Choosing K**: tested K=3 through K=7 via Silhouette Score. K=3 
   scored highest (0.235), meaningfully ahead of K=6/K=7, and only 
   marginally ahead of K=5 — K=3 was selected as the clearer, 
   top-scoring choice.

#### ⚠️ Key Limitation
Cluster labels are a human interpretation applied after clustering — 
K-Means itself only outputs group numbers. Each label here was derived 
by comparing real feature averages across clusters (not the compressed 
PCA visualization), and, where a cluster's story wasn't immediately 
obvious (the low-price cluster), verified by inspecting the underlying 
data before finalizing a name.

#### 🚧 Future Work
- Re-run clustering with `make` included to test whether brand-driven 
  segments add meaningful insight
- Try DBSCAN as a density-based alternative that doesn't require 
  pre-specifying K
- Test whether a 4- or 5-cluster solution becomes more competitive 
  under different feature/preprocessing choices