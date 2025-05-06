import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier

# Sample training data
# Each input is a sequence of events; each label is the corresponding journey stage
X = [
    "page_view product_view add_to_cart purchase",
    "page_view product_view add_to_cart",
    "page_view product_view",
    "page_view",
    "page_view product_view wishlist",
    "page_view wishlist"
]
y = [
    "purchase",    # user purchased
    "checkout",    # user added to cart but not purchased
    "engaged",     # user viewed products
    "aware",       # only visited the page
    "wishlist",    # added to wishlist
    "wishlist"     # just added to wishlist without viewing
]

vectorizer = CountVectorizer()
X_vectorized = vectorizer.fit_transform(X)

# Train model
model = DecisionTreeClassifier()
model.fit(X_vectorized, y)

# Save both model and vectorizer
joblib.dump(model, "ml-model/journey_model.pkl")
joblib.dump(vectorizer, "ml-model/vectorizer.pkl")

print("Model and vectorizer saved.")
