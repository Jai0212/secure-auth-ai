import joblib
from geopy.distance import great_circle
import datetime
import joblib
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Any, Tuple
import pandas as pd
from collections import Counter
import os

# This file contains the functions that are used to predict whether a login attempt is safe or not using the AI model and statistical anomaly detection


def distance_change(
    coords: List[Tuple[float, float]], curr_coords: Tuple[float, float]
) -> int:
    """Calculates variation in average change in distance of login location"""

    distances = [
        great_circle(coords[i], coords[i + 1]).kilometers
        for i in range(len(coords) - 1)
    ]

    if len(distances) == 0:
        return 0

    distance = great_circle(coords[len(coords) - 1], curr_coords).kilometers

    return abs(int((sum(distances) / len(distances)) - distance))


def device_change(devices: List[str], curr_device: str) -> int:
    """Calculates variation in average number of times the device used to login was changed"""

    device_changes = Counter(devices)

    if len(device_changes) == 0:
        return 0
    else:
        average_device_change = int(
            sum(list(device_changes.values())) / len(device_changes)
        )

        if curr_device in device_changes:
            return average_device_change
        else:
            return average_device_change + 1


def time_change(times: List[datetime.datetime], curr_time: datetime.datetime) -> float:
    """Calculates variation in average time at which user logged in"""

    time_differences = [
        (abs((times[i] - times[i + 1]).total_seconds() / 3600))
        for i in range(len(times) - 1)
    ]

    if len(time_differences) == 0:
        return 0

    time_difference = abs((times[len(times) - 1] - curr_time).total_seconds() / 3600)

    return abs((sum(time_differences) / len(time_differences)) - time_difference)


def attempts_change(attempts: List[int], curr_attempts: int) -> int:
    """Calculates variation in average number of attempts taken to login"""

    attempts_changes = [
        abs(attempts[i] - attempts[i + 1]) for i in range(len(attempts) - 1)
    ]

    if len(attempts_changes) == 0:
        return 0

    attempts_change = abs(attempts[len(attempts) - 1] - curr_attempts)

    return abs(int((sum(attempts_changes) / len(attempts_changes)) - attempts_change))


def model_prediction(
    distance_change: int, device_change: int, attempts_change: int, time_change: float
) -> bool:
    """Predicts whether login attempt is safe or not using the AI model based on the change in distance, device, attempts and time"""

    curr_dir = os.path.dirname(__file__)
    loaded_model = joblib.load(os.path.join(curr_dir, "secure_auth_ai_model.pkl"))

    new_data = {
        "distance_change": [distance_change],
        "device_change": [device_change],
        "attempts_change": [attempts_change],
        "time_change": [time_change],
    }

    new_data_df = pd.DataFrame(new_data)

    # print("New data for prediction:")
    # print(new_data_df)

    predictions = loaded_model.predict(new_data_df)

    # print("Predicted class labels:", predictions)

    return bool(predictions[0])


def number_anamoly(data: List[Any], tester: Any) -> bool:
    """Finds anomalies in the number of attempts"""

    data.append(tester)

    threshold = 2

    data_array = np.array(data)

    z_scores = np.abs(stats.zscore(data_array))

    anomalies = np.where(z_scores > threshold)

    values = data_array[anomalies].tolist()

    return tester in values


def tuple_anomaly(data: List[Tuple[float, float]], tester: Tuple[float, float]) -> bool:
    """Finds anomalies in the locations of login"""

    data_array = np.array(data)

    threshold = 2

    tester_array = np.array(tester)
    tester_z_scores = np.abs(stats.zscore(data_array, axis=0))
    tester_anomaly = np.any(
        tester_z_scores[np.all(data_array == tester_array, axis=1)] > threshold
    )

    return tester_anomaly


def time_anamoly(data: List[datetime.datetime], tester: datetime.datetime) -> bool:
    """Finds anomalies in the times of login"""

    data.append(tester)

    time_differences = [
        ((data[i] - data[i + 1]).total_seconds() / 3600) for i in range(len(data) - 1)
    ]

    return number_anamoly(time_differences, time_differences[len(time_differences) - 1])


def string_anamoly(data: List[str], tester: Any) -> bool:
    """Finds anomalies in the device used to login"""

    data.append(tester)

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data)

    similarity_matrix = cosine_similarity(X)

    average_similarities = np.mean(similarity_matrix, axis=1)

    threshold = 0.2

    anomalies = np.where(average_similarities < threshold)

    values = np.array(data)[anomalies].tolist()

    return tester in values


def is_safe(
    coords: List[List[str]],
    devices: List[str],
    times: List[datetime.datetime],
    attempts: List[int],
    curr_attempts: int,
) -> bool:
    """Based on the AI model and the statistical anomaly detection, decides whether the login attempt is safe or not"""

    # print(coords, devices, times, attempts, curr_attempts)

    coords_float: List[Tuple[float, float]] = [(float(x), float(y)) for x, y in coords]

    curr_coords = coords_float.pop()
    curr_device = devices.pop()
    curr_time = times.pop()

    distance_change_var = distance_change(coords_float, curr_coords)
    device_change_var = device_change(devices, curr_device)
    time_change_var = time_change(times, curr_time)
    attempts_change_var = attempts_change(attempts, curr_attempts)

    distance_change_anamoly = tuple_anomaly(coords_float, curr_coords)
    device_change_anamoly = string_anamoly(devices, curr_device)
    time_change_anamoly = time_anamoly(times, curr_time)
    attempts_change_anamoly = number_anamoly(attempts, curr_attempts)

    prediction = model_prediction(
        distance_change_var, device_change_var, attempts_change_var, time_change_var
    )

    # print(prediction)
    # print(
    #     distance_change_anamoly,
    #     device_change_anamoly,
    #     time_change_anamoly,
    #     attempts_change_anamoly,
    # )

    number_of_trues = sum(
        [
            prediction,
            distance_change_anamoly,
            device_change_anamoly,
            time_change_anamoly,
            attempts_change_anamoly,
        ]
    )

    print("No. of trues: " + str(number_of_trues))
    return not number_of_trues >= 3
