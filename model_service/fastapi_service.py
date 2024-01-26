import io
import pandas as pd
import uvicorn

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse, PlainTextResponse

from sklearn.linear_model._base import LinearModel
from sklearn.linear_model import *
from sklearn.model_selection import train_test_split
import sklearn.metrics


class ModelInfo:
    def __init__(self, csv_filename: str):
        df = pd.read_csv(csv_filename)
        self.X, self.y = df.drop('TARGET', axis=1), df['TARGET']
        self.linear_model = None

    def reset(self, new_model: LinearModel, func_score: str):
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, shuffle=True, stratify=self.y)
        self.linear_model = new_model.fit(X_train, y_train)
        score_function = getattr(sklearn.metrics, func_score)
        y_pred = self.linear_model.predict(X_test).round()
        score = score_function(y_test, y_pred)
        return score

    def predict(self, X: pd.DataFrame):
        return self.linear_model.predict_proba(X)[:, 1]

    def get_params(self):
        res = dict()
        res['model_type'] = type(self.linear_model).__name__
        res |= self.linear_model.get_params()
        return res


app = FastAPI()
model = ModelInfo('data.csv')


@app.get('/')
def root():
    return JSONResponse("Inner linear model service")


@app.get('/column_names')
def column_names():
    return JSONResponse(model.X.columns.to_list())


@app.patch('/predict/')
async def predict_csv(request: Request):
    with io.BytesIO(await request.body()) as csv_buffer:
        df = pd.read_csv(csv_buffer)

    df['TARGET'] = model.predict(df)

    return PlainTextResponse(df.to_csv(index=False))


@app.get('/model_info')
def model_info():
    return JSONResponse(model.get_params())


@app.patch('/train_model/')
def train(model_name: str, func_score: str):
    return JSONResponse(model.reset(globals()[model_name](), func_score))


if __name__ == '__main__':
    uvicorn.run(app)
