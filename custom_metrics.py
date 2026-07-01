from prometheus_client import Counter,Summary,start_http_server

REQUESTS_COUNTER = Counter(name="prediction_requests_total",
                           documentation="This metric will be used for counting the total number of incoming requests")

RESPONSE_TIME_SUMMARY = Summary(name="prediction_requests_duration_seconds",
                                documentation="This metric will be used for counting the request and the duration taken by model to server the prediction")

start_http_server(8000)
@RESPONSE_TIME_SUMMARY.time()
def predict(input,classifier):
    REQUESTS_COUNTER.inc()
    prediction = classifier.predict(input)
    return prediction
