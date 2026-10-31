# 🚗 Car Market Segmentation — K-Means Clustering

Unsupervised segmentation of the Kaggle
[Car Features and MSRP](https://www.kaggle.com/datasets/CooperUnion/cardataset)
dataset into natural market groups with K-Means.

## 📁 Repository Contents

| File | Description |
|---|---|
| `project.ipynb` | Full analysis: data loading, cleaning, EDA, choosing K, clustering, profiling, naming |
| `car_clustering_model.pkl` | Fitted preprocessing pipeline + K-Means (K=3) + cluster name mapping |
| `app.py` | FastAPI app that assigns a car to a segment — see [Running the API](#-running-the-api) |
| `requirements.txt` | Pinned Python dependencies |

## ▶️ How to Run

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
jupyter lab project.ipynb
```

The dataset is downloaded automatically by `kagglehub` on first run.

To use the saved model on new cars:

```python
import joblib, numpy as np

bundle = joblib.load('car_clustering_model.pkl')
# new_cars: DataFrame with the notebook's sanitized column names; add log_msrp first
new_cars['log_msrp'] = np.log1p(new_cars['msrp'])
X = bundle['preprocessor'].transform(new_cars)
names = [bundle['cluster_names'][c] for c in bundle['kmeans_model'].predict(X)]
```

## 🚀 Running the API

`app.py` serves the saved model with FastAPI and tells you which of the 3
market segments a car belongs to.

### 1. Start the server

From the project folder, with the dependencies installed (see
**How to Run** above):

```powershell
.venv\Scripts\activate
uvicorn app:app --reload
```

When it is ready you will see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000/docs (Press CTRL+C to quit)
```

`--reload` restarts the server automatically whenever you edit `app.py`.
Leave this terminal open — closing it stops the API.

### 2. Open the app in your browser

| URL | What it is |
|---|---|
| http://127.0.0.1:8000/docs | **Interactive docs (start here)** — try the API with buttons |
| http://127.0.0.1:8000/ | Health check — confirms the model loaded |
| http://127.0.0.1:8000/redoc | Read-only documentation |

To try it in `/docs`:
1. Click **POST /segment**
2. Click **Try it out**
3. Edit the example car in the request body (or keep it as is)
4. Click **Execute** — the answer appears under **Response body**

### 📨 Example request

```json
{
  "year": 2015,
  "engine_hp": 180,
  "engine_cylinders": 4,
  "number_of_doors": 4,
  "highway_mpg": 34,
  "city_mpg": 25,
  "msrp": 24000,
  "engine_fuel_type": "regular unleaded",
  "transmission_type": "AUTOMATIC",
  "driven_wheels": "front wheel drive",
  "vehicle_size": "Midsize",
  "vehicle_style": "Sedan"
}
```

### 📬 Example response

```json
{
  "cluster": 2,
  "segment": "Efficient / Mainstream",
  "distance_to_each_segment": {
    "Older Models (Mostly Pre-2001)": 4.5,
    "High-Performance / Luxury": 3.776,
    "Efficient / Mainstream": 1.42
  }
}
```

- **`segment`** — the market segment the car belongs to
- **`distance_to_each_segment`** — how far the car is from the center of each segment.
  The smallest distance is the chosen segment; if two distances are close, the car sits
  on the border between them

### Calling it from PowerShell instead of the browser

```powershell
$car = @{
  year = 2015; engine_hp = 180; engine_cylinders = 4; number_of_doors = 4
  highway_mpg = 34; city_mpg = 25; msrp = 24000
  engine_fuel_type = "regular unleaded"; transmission_type = "AUTOMATIC"
  driven_wheels = "front wheel drive"; vehicle_size = "Midsize"; vehicle_style = "Sedan"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8000/segment -Method Post -Body $car -ContentType "application/json"
```

### 📋 Accepted values

| Field | Required | Allowed values |
|---|---|---|
| `year` | ✅ | 1990–2017 |
| `engine_hp` | — | number > 0 (filled with the training median if left out) |
| `engine_cylinders` | — | number > 0 |
| `number_of_doors` | — | number |
| `highway_mpg`, `city_mpg` | ✅ | between 0 and 100 |
| `msrp` | ✅ | between 0 and 500,000 |
| `engine_fuel_type` | — | `regular unleaded`, `premium unleaded (recommended)`, `premium unleaded (required)`, `diesel`, `natural gas`, `flex-fuel (unleaded/E85)`, `flex-fuel (premium unleaded recommended/E85)`, `flex-fuel (premium unleaded required/E85)`, `flex-fuel (unleaded/natural gas)` |
| `transmission_type` | ✅ | `AUTOMATIC`, `MANUAL`, `AUTOMATED_MANUAL`, `DIRECT_DRIVE`, `UNKNOWN` |
| `driven_wheels` | ✅ | `front wheel drive`, `rear wheel drive`, `all wheel drive`, `four wheel drive` |
| `vehicle_size` | ✅ | `Compact`, `Midsize`, `Large` |
| `vehicle_style` | ✅ | `Sedan`, `Coupe`, `Convertible`, `Wagon`, `2dr Hatchback`, `4dr Hatchback`, `2dr SUV`, `4dr SUV`, `Convertible SUV`, `Passenger Minivan`, `Cargo Minivan`, `Passenger Van`, `Cargo Van`, `Regular Cab Pickup`, `Extended Cab Pickup`, `Crew Cab Pickup` |

Values are case-sensitive. Anything outside these lists is rejected with a
**422** error that names the wrong field.

> ⚠️ Electric cars and cars priced at $500,000+ were removed before training, so the
> API does not accept them. Prices for older (pre-2001) cars in the training data
> were often a `$2,000` placeholder, so treat price-driven results for old cars with care.

### 🛑 Stopping the server

Press **CTRL + C** in the terminal where it is running.

### 🧯 Troubleshooting

| Problem | Fix |
|---|---|
| `uvicorn` is not recognized | The virtual environment is not active — run `.venv\Scripts\activate` |
| `ModuleNotFoundError: fastapi` | Run `pip install -r requirements.txt` |
| `FileNotFoundError: car_clustering_model.pkl` | Start `uvicorn` from the project folder, or re-run `project.ipynb` to export the model |
| Port 8000 already in use | Use another port: `uvicorn app:app --reload --port 8001` |
| Error loading the `.pkl` | Keep `scikit-learn==1.9.0` — the model only loads reliably with the version that saved it |

---

### 📌 Executive Summary & Conclusion

#### 🎯 Project Overview
This project segments ~11,100 U.S. car listings (1990–2017 model years, 
after cleaning) into natural market groups using **K-Means clustering** 
— an unsupervised approach with no predefined categories and no target 
variable to predict. Rather than imposing labels like "economy" or 
"luxury" in advance, the goal was to let the data reveal its own 
structure, then interpret what that structure means.

---

#### 📊 Results — 3 Market Segments

| Cluster | Avg. HP | Cylinders | Highway MPG | City MPG | Median MSRP | Mean MSRP | Median Year | Count |
|---|---|---|---|---|---|---|---|---|
| Efficient / Mainstream | 184 | 4.1 | 32.2 | 24.4 | $25,460 | $27,603 | 2015 | 4,038 |
| High-Performance / Luxury | 329 | 6.9 | 22.6 | 15.9 | $40,400 | $61,144 | 2015 | 5,455 |
| Older Models (Mostly Pre-2001) | 170 | 5.5 | 23.2 | 17.2 | $2,114 | $5,523 | 1996 | 1,628 |

- **Efficient / Mainstream** — practical, fuel-conscious cars: best fuel 
  economy of the three segments, moderate price
- **High-Performance / Luxury** — the most powerful and expensive 
  segment by a wide margin, trading off fuel economy for performance
- **Older Models (Mostly Pre-2001)** — its low price reflects data 
  quality, not a deliberate "budget" design: ~46% of its prices are a 
  `$2,000` placeholder used only for 1990–2000 models. A sensitivity 
  check (re-clustering without those rows) showed an older-models 
  segment still forms, so the cluster is named after its age rather 
  than its price

---
#### 📝**Note**:  
**Choosing K via Silhouette Score** — tested K=2 through K=7; 
  K=3 scored highest (0.235), clearly ahead of K=2, K=6 and K=7, and only marginally ahead of K=5 (0.232). K=3 was selected as the clearer, top-scoring, and simplest-to-interpret choice.

   A Silhouette Score of 0.235 indicates weak-to-moderate cluster 
   separation — the segments are statistically the best available 
   option among those tested, but the underlying structure isn't 
   strongly distinct. This is a realistic outcome given how continuous 
   and overlapping real-world car specs tend to be, rather than a flaw 
   in the methodology.

---

#### 🔑 Key Modeling Decisions

1. **Outlier filtering** — removed a data entry error (an Audi listed 
   at 354 highway MPG, physically implausible for a gas-powered 
   vehicle), electric vehicles, and hypercars priced at $500,000 or 
   more (e.g., the $2M+ Bugatti Veyron). Rows with a missing cylinder 
   count (mostly Mazda rotary engines) were kept and imputed.
2. **Log-transformed MSRP** — even after removing hypercars, prices 
   still run from $2,000 to ~$500,000; the log transform keeps the most 
   expensive cars from dominating K-Means' distance calculations.
3. **Deliberate feature exclusions** — `make` and `popularity` were left 
   out of clustering, to avoid grouping cars by brand identity or 
   brand-buzz rather than by their actual specifications.
4. **Choosing K via Silhouette Score** — tested K=2 through K=7; K=3 
   scored highest (0.235) and was selected as the clearer, top-scoring, 
   and simplest-to-interpret choice.
5. **Data-driven cluster naming** — K-Means numbers its clusters 
   arbitrarily, so each name is attached to the cluster whose profile 
   matches it (oldest median year, then highest horsepower), not to a 
   fixed cluster number.

---

#### ⚠️ Key Limitation

Cluster labels are a human interpretation applied *after* clustering — 
K-Means itself only outputs group numbers (0, 1, 2), with no inherent 
meaning attached. Each label in this project was derived by comparing 
real feature values across clusters (the PCA plot is only a supporting 
visual, since it compresses the data to 56% of its variance). Where a 
cluster's story wasn't immediately obvious — the low-price cluster — 
the underlying data was inspected directly and a sensitivity check was 
run before finalizing a name, rather than guessing from price alone.

The `$2,000` placeholder prices remain in the data and still sharpen 
the older-models segment; its MSRP values should not be used for any 
price-based business interpretation.

More broadly, K-Means assumes clusters are roughly round/similarly 
sized, which may not perfectly reflect how real car segments are 
shaped in the underlying feature space — a limitation worth exploring 
with alternative methods.

---

#### 🚧 Future Work

- Treat the `$2,000` placeholder prices as missing values and impute 
  them, rather than clustering on them
- Re-run clustering with `make` included, to test whether brand-driven 
  segments reveal additional insight beyond specs alone
- Explore **DBSCAN** as a density-based alternative that doesn't 
  require pre-specifying K, and can explicitly flag outlier vehicles 
  as noise rather than forcing them into a cluster
- Test whether a 4- or 5-cluster solution becomes more competitive 
  under different feature or preprocessing choices, since K=3 and K=5 
  were nearly tied on Silhouette Score
