import pandas as pd
import streamlit as st
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier


def load_data() -> pd.DataFrame:
    iris = datasets.load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = iris.target
    df["species"] = df["target"].map({i: name for i, name in enumerate(iris.target_names)})
    return df, iris


def main() -> None:
    st.set_page_config(page_title="Iris Explorer", layout="wide")
    st.title("Iris Dataset Explorer")
    st.write("Explore the classic Iris dataset and predict flower species using a simple classifier.")

    df, iris = load_data()

    with st.sidebar:
        st.header("Settings")
        show_data = st.checkbox("Show raw data", value=True)
        species_filter = st.multiselect("Filter species", options=iris.target_names, default=list(iris.target_names))
        st.markdown("---")
        st.subheader("Prediction input")
        sepal_length = st.slider("Sepal length", float(df["sepal length (cm)"].min()), float(df["sepal length (cm)"].max()), float(df["sepal length (cm)"].mean()))
        sepal_width = st.slider("Sepal width", float(df["sepal width (cm)"].min()), float(df["sepal width (cm)"].max()), float(df["sepal width (cm)"].mean()))
        petal_length = st.slider("Petal length", float(df["petal length (cm)"].min()), float(df["petal length (cm)"].max()), float(df["petal length (cm)"].mean()))
        petal_width = st.slider("Petal width", float(df["petal width (cm)"].min()), float(df["petal width (cm)"].max()), float(df["petal width (cm)"].mean()))

    if show_data:
        st.subheader("Iris data")
        st.dataframe(df[df["species"].isin(species_filter)].reset_index(drop=True))

    st.subheader("Feature summary")
    st.write(df[df["species"].isin(species_filter)][iris.feature_names].describe())

    classifier = RandomForestClassifier(random_state=42)
    classifier.fit(df[iris.feature_names], df["target"])
    prediction = classifier.predict([[sepal_length, sepal_width, petal_length, petal_width]])
    predicted_species = iris.target_names[prediction[0]]

    st.subheader("Prediction")
    st.write(f"Predicted species: **{predicted_species.title()}**")
    st.write("Input features:")
    st.json({
        "sepal_length": sepal_length,
        "sepal_width": sepal_width,
        "petal_length": petal_length,
        "petal_width": petal_width,
    })

    st.subheader("Species distribution")
    hist_data = df["species"].value_counts().rename_axis("species").reset_index(name="count")
    st.bar_chart(hist_data.rename(columns={"species": "index", "count": "value"}).set_index("index"))


if __name__ == "__main__":
    main()

