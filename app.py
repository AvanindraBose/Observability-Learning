import streamlit as st
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
from custom_metrics import predict


def main() -> None:
    st.set_page_config(page_title="Iris Predictor")
    st.title("Iris Species Prediction")
    st.write("Enter the four iris measurements and click the button to get a prediction.")

    iris = datasets.load_iris()
    classifier = RandomForestClassifier(random_state=42)
    classifier.fit(iris.data, iris.target)

    sepal_length = st.number_input("Sepal length (cm)", min_value=0.0, max_value=10.0, value=5.1, step=0.1)
    sepal_width = st.number_input("Sepal width (cm)", min_value=0.0, max_value=10.0, value=3.5, step=0.1)
    petal_length = st.number_input("Petal length (cm)", min_value=0.0, max_value=10.0, value=1.4, step=0.1)
    petal_width = st.number_input("Petal width (cm)", min_value=0.0, max_value=10.0, value=0.2, step=0.1)

    if st.button("Get prediction"):
        prediction = predict([[sepal_length, sepal_width, petal_length, petal_width]],classifier)
        species = iris.target_names[prediction[0]]
        st.success(f"Predicted species: {species.title()}")


if __name__ == "__main__":
    main()

