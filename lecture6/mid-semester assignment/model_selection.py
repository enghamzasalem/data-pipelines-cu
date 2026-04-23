import os
import joblib

MODEL_PATH = "models/gold_model.pkl"

def select_best_model(results):

    best_model = None
    best_score = 0

    for name, (model, score) in results.items():

        print(name, "accuracy:", score)

        if score > best_score:
            best_score = score
            best_model = model

    # ✅ Ensure directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # ✅ Save model
    joblib.dump(best_model, MODEL_PATH)

    print("Best model saved:", MODEL_PATH)