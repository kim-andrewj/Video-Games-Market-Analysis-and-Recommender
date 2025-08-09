import re
import difflib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="Game Recommender", layout="wide")
DATA_PATH = "cleaned_data.csv"  

@st.cache_data(show_spinner=True)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # in case of null, fill with placeholder values
    fill_map = {
        "Genres": "Unknown",
        "Developers": "Unknown",
        "Publishers": "Unknown",
        "Platforms": "Unknown",
        "Release Years": "Unknown",
        "Game Modes": "Unspecified",
        "Themes": "Unspecified",
    }
    for c, v in fill_map.items():
        if c in df.columns:
            df[c] = df[c].fillna(v).astype(str)

    # Ensuring numeric
    if "Rating" in df.columns:
        df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0)
    if "Rating Count" in df.columns:
        df["Rating Count"] = pd.to_numeric(df["Rating Count"], errors="coerce").fillna(0).astype(int)

    scaler = MinMaxScaler()
    df["Rating_norm"] = scaler.fit_transform(df[["Rating"]])
    df["RatingCount_norm"] = scaler.fit_transform(df[["Rating Count"]])
    return df


df = load_data(DATA_PATH)

def to_list(cell: str):
    if pd.isna(cell):
        return []
    return [p.strip() for p in str(cell).split(",") if p.strip()]


def make_mode_tag(modes_list):
    tags = []
    txt = " ".join([m.lower() for m in modes_list])
    if "single" in txt:
        tags.append("single")
    if "multiplayer" in txt:
        tags.append("multiplayer")
    if "co-operative" in txt or "cooperative" in txt:
        tags.append("cooperative")
    if "split" in txt:
        tags.append("split")
    return tags or ["unspecified_mode"]


def build_feature_text(row):
    genres = [re.sub(r"\s+", "_", g.lower()) for g in to_list(row["Genres"])]
    themes = [re.sub(r"\s+", "_", t.lower()) for t in to_list(row["Themes"])]
    platforms = [re.sub(r"\s+", "_", p.lower()) for p in to_list(row["Platforms"])]
    modes = make_mode_tag(to_list(row["Game Modes"]))
    tokens = genres + themes + platforms + modes
    return " ".join(tokens)


@st.cache_data(show_spinner=False)
def build_matrix(df_subset: pd.DataFrame):
    corpus = df_subset.apply(build_feature_text, axis=1).tolist()
    vectorizer = TfidfVectorizer(min_df=2)
    X = vectorizer.fit_transform(corpus)
    return X, vectorizer


def cosine_sim_matrix(X):
    X = X.tocsr()
    norms = np.sqrt(X.multiply(X).sum(1)).A1  # 1-D
    norms[norms == 0] = 1e-9
    sims = (X @ X.T).toarray()               # ndarray
    sims = sims / (norms[:, None] * norms[None, :])
    return sims


def rank_content_based(df_subset, X, sims, idx, top_k=15, w_rating=0.5, w_count=0.5):
    base = np.asarray(sims[idx]).ravel()  # (N,)
    quality = np.asarray(df_subset["Rating_norm"].values).ravel()
    engage = np.asarray(df_subset["RatingCount_norm"].values).ravel()
    score = base * (w_rating * quality + w_count * engage)
    order = np.argsort(-score)

    recs = df_subset.iloc[order].copy().reset_index(drop=True)
    recs["score"] = score[order]
    # drop the query itself
    return recs.iloc[1:top_k+1]


def filter_df(df,
              sel_genres=None,
              sel_platforms=None,
              sel_themes=None,
              mode_pref="Any",
              min_rating=0.0,
              min_count=0):
    temp = df.copy()
    if sel_genres:
        temp = temp[temp["Genres"].str.contains("|".join([re.escape(g) for g in sel_genres]))]
    if sel_platforms:
        temp = temp[temp["Platforms"].str.contains("|".join([re.escape(p) for p in sel_platforms]))]
    if sel_themes:
        temp = temp[temp["Themes"].str.contains("|".join([re.escape(t) for t in sel_themes]))]

    if mode_pref != "Any":
        if mode_pref == "Single Only":
            s = temp["Game Modes"].str.contains("Single player", case=False, na=False)
            m = temp["Game Modes"].str.contains("Multiplayer|Co-operative", case=False, na=False)
            temp = temp[s & ~m]
        elif mode_pref == "Multi Only":
            temp = temp[temp["Game Modes"].str.contains("Multiplayer|Co-operative", case=False, na=False)]
        elif mode_pref == "Both":
            s = temp["Game Modes"].str.contains("Single player", case=False, na=False)
            m = temp["Game Modes"].str.contains("Multiplayer|Co-operative", case=False, na=False)
            temp = temp[s & m]

    temp = temp[(temp["Rating"] >= min_rating) & (temp["Rating Count"] >= min_count)]
    return temp.drop_duplicates(subset=["Name"]).reset_index(drop=True)


# Sidebar
st.sidebar.header("Filters")
all_genres = sorted({g for row in df["Genres"] for g in to_list(row)})
all_platforms = sorted({p for row in df["Platforms"] for p in to_list(row)})
all_themes = sorted({t for row in df["Themes"] for t in to_list(row)})

sel_genres = st.sidebar.multiselect("Preferred Genres", all_genres)
sel_platforms = st.sidebar.multiselect("Preferred Platforms", all_platforms)
sel_themes = st.sidebar.multiselect("Preferred Themes", all_themes)
mode_pref = st.sidebar.selectbox("Game Mode", ["Any", "Single Only", "Multi Only", "Both"])
min_rating = st.sidebar.slider("Min Rating", 0.0, 100.0, 50.0, 1.0)
min_count = st.sidebar.slider("Min Rating Count", 0, int(df["Rating Count"].max()), 5, 1)

# Main
st.title("Video Game Recommender (Genres × Platforms × Themes)")
st.caption("Welcome to my video game recommendation system! This was built off of an extracted, cleaned" \
            " dataset of video games from IGDB using the IGDB API. Using engagement-aware weighting" \
            " as well as specific filters and toggles, you can feel free to find your new favorite game here!")

tab_rec, tab_viz = st.tabs(["Recommendations", "Platform Share"])

# Recommendations
with tab_rec:
    st.subheader("Content-Based Recommender")
    anchor_mode = st.toggle("Want to query a specific game? Toggle this button to search for similar games!", value=False)

    filtered_pool = filter_df(
        df,
        sel_genres=sel_genres,
        sel_platforms=sel_platforms,
        sel_themes=sel_themes,
        mode_pref=mode_pref,
        min_rating=min_rating,
        min_count=min_count,
    )

    if filtered_pool.empty:
        st.warning("No games match your filters. Loosen filters and try again.")
    else:
        filtered_pool = filtered_pool.reset_index(drop=True)
        anchor_game = None

        if anchor_mode:
            st.markdown("**Search or scroll to choose a game**")
            options = filtered_pool["Name"].sort_values().tolist()
            q = st.text_input("Type to search:", value="", placeholder="e.g., The Witcher 3")
            if q.strip():
                # substring filter first
                filtered_options = [n for n in options if q.lower() in n.lower()]
                # if nothing, fall back to close matches
                if not filtered_options:
                    filtered_options = difflib.get_close_matches(q, options, n=25, cutoff=0.4)
            else:
                filtered_options = options[:2000]  # cap for faster UI

            anchor_game = st.selectbox("OR Select a game", options=filtered_options, index=0 if filtered_options else None)

        w_rating = st.slider("Weight: Rating (quality)", 0.0, 1.0, 0.5, 0.05)
        w_count = 1.0 - w_rating
        top_k = st.slider("How many recommendations?", 1, 30, 10, 1)

        # Build features & similarities
        X, _ = build_matrix(filtered_pool)
        sims = cosine_sim_matrix(X)

        if anchor_mode and anchor_game:
            # Use the chosen game
            anchor_idx = int(filtered_pool.index[filtered_pool["Name"] == anchor_game][0])
            recs = rank_content_based(filtered_pool, X, sims, anchor_idx,
                                      top_k=top_k, w_rating=w_rating, w_count=w_count)
            st.write(f"**Query game:** `{filtered_pool.loc[anchor_idx, 'Name']}`")
        else:
            # Fallback: silently use a centroid-like representative (no display)
            anchor_idx = int((filtered_pool["Rating_norm"] + filtered_pool["RatingCount_norm"]).values.argmax())
            recs = rank_content_based(filtered_pool, X, sims, anchor_idx,
                                      top_k=top_k, w_rating=w_rating, w_count=w_count)
            st.write("Using your **filters + weights** (no specific query selected).")

        st.dataframe(
            recs[["Name", "Genres", "Themes", "Platforms", "Rating", "Rating Count", "score"]]
            .reset_index(drop=True)
        )

    st.subheader("Hidden Gems (High Rating, Lower Exposure)")
    alpha = st.slider("Quality vs. Obscurity (α)", 0.1, 0.90, 0.5, 0.05)
    min_gem_count = st.slider("Minimum rating count", 0, 100, 5, 1)
    k2 = st.slider("How many gems?", 1, 30, 10, 1)

    gem_pool = filter_df(
        df,
        sel_genres=sel_genres,
        sel_platforms=sel_platforms,
        sel_themes=sel_themes,
        mode_pref=mode_pref,
        min_rating=min_rating,  
        min_count=min_gem_count,
    )

    if gem_pool.empty:
        st.warning("No games found for the Hidden Gems criteria. Loosen filters or reduce the minimum rating count.")
    else:
        q = gem_pool["Rating_norm"].values
        e = gem_pool["RatingCount_norm"].values
        score = alpha * q + (1 - alpha) * (1 - e)
        order = np.argsort(-score)
        gems = gem_pool.iloc[order].head(k2).copy()
        gems["score"] = score[order][:k2]

        st.dataframe(
            gems[["Name", "Genres", "Themes", "Platforms", "Rating", "Rating Count", "score"]]
            .reset_index(drop=True)
        )
        st.caption("Higher α favors quality; lower α favors under-the-radar picks. Titles must meet your minimum rating-count threshold.")
    

# Platform Share
with tab_viz:
    st.subheader("Platform Share Within Current Filters")
    viz_pool = filter_df(
        df,
        sel_genres=sel_genres,
        sel_platforms=sel_platforms,
        sel_themes=sel_themes,
        mode_pref=mode_pref,
        min_rating=min_rating,
        min_count=min_count,
    )
    if viz_pool.empty:
        st.info("No data to visualize with current filters.")
    else:
        tmp = viz_pool.copy()
        tmp["Platforms"] = tmp["Platforms"].apply(to_list)
        tmp = tmp.explode("Platforms")
        
        # Count how many games per platform
        plat_counts = tmp.groupby("Platforms")["Name"].nunique().sort_values(ascending=False)
        
        # Slider to choose how many platforms to show
        topN = st.slider("Show top N platforms", 3, min(15, len(plat_counts)), min(8, len(plat_counts)), 1)
        
        count_data = plat_counts.head(topN).rename("Number of Games")
        
        st.bar_chart(count_data)

