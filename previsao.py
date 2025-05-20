import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from datetime import datetime
import matplotlib.pyplot as plt
import logging
import sys
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

TICKERS_VALIDOS = {
    "Ouro": "Ouro", "Prata": "Prata", "Cobre": "Cobre", "Alumínio": "Alumínio", "Zinco": "Zinco",
    "Gado_Vivo": "Gado_Vivo", "Carne_Porco": "Carne_Porco", "Milho": "Milho", "Soja": "Soja", "Trigo": "Trigo",
    "Petróleo_WTI": "Petróleo_WTI", "Petróleo_Brent": "Petróleo_Brent", "Gás_Natural": "Gás_Natural",
    "Gasolina_RBOB": "Gasolina_RBOB", "Óleo_Aquecimento": "Óleo_Aquecimento", "Suco_Laranja": "Suco_Laranja",
    "Algodão": "Algodão", "Café_Arábica": "Café_Arábica", "Açúcar": "Açúcar", "Cacau": "Cacau",
    "Madeira": "Madeira", "Platina": "Platina", "Paládio": "Paládio"
}

CACHE_DIR = "data_cache"


def compute_rsi(data, periods=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_macd(data, short=12, long=26, signal=9):
    exp1 = data.ewm(span=short, adjust=False).mean()
    exp2 = data.ewm(span=long, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd - signal_line


class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=128, num_layers=2, output_size=1, dropout=0.2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size,
                            num_layers, batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :])


def preprocessar_dados(data, seq_length=60):
    if 'Date' in data.columns:
        data = data.drop(columns=['Date'])

    data = data.select_dtypes(include=[np.number])
    data = data.dropna()

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)

    X, y = [], []
    for i in range(seq_length, len(scaled_data)):
        X.append(scaled_data[i-seq_length:i])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    return X, y, scaler


def carregar_dados_csv(csv_path="data_cache/commodities.csv"):
    try:
        df = pd.read_csv(csv_path)
        logging.info(f"Dados carregados com sucesso do arquivo: {csv_path}")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Erro: Arquivo CSV não encontrado em: {csv_path}")
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError(
            f"Erro: O arquivo CSV está vazio: {csv_path}")
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo CSV: {e}")


def obter_dados(nome_commodity, df_commodities):
    if nome_commodity in df_commodities.columns:
        data = df_commodities[['Date', nome_commodity]].copy()
        data = data.dropna()
        if data.empty:
            raise ValueError(
                f"Dados insuficientes para a commodity: {nome_commodity}")
        return data
    else:
        raise ValueError(
            f"Commodity '{nome_commodity}' não encontrada no DataFrame.")


def plot_predictions(y_test, predicted_prices, scaler, data, ticker, predicted_next):

    y_test = y_test.reshape(-1, 1) if y_test.ndim == 1 else y_test
    predicted_prices = predicted_prices.reshape(-1, 1) if predicted_prices.ndim == 1 else predicted_prices

    y_test_actual = scaler.inverse_transform(
        np.concatenate([y_test, np.zeros((y_test.shape[0], data.shape[1]-1))], axis=1)
    )[:, 0]
    
    predicted_actual = scaler.inverse_transform(
        np.concatenate([predicted_prices, np.zeros((predicted_prices.shape[0], data.shape[1]-1))], axis=1)
    )[:, 0]

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['Date'].iloc[-len(y_test):],
        y=y_test_actual,
        name='Valores Reais',
        line=dict(color='blue', width=2),
        mode='lines+markers'
    ))
    
    fig.add_trace(go.Scatter(
        x=data['Date'].iloc[-len(predicted_prices):],
        y=predicted_actual,
        name='Previsões',
        line=dict(color='red', width=2, dash='dot'),
        mode='lines+markers'
    ))

    last_date = pd.to_datetime(data['Date'].iloc[-1])
    next_date = last_date + pd.Timedelta(days=1)
    
    fig.add_trace(go.Scatter(
        x=[next_date],
        y=[predicted_next],
        name='Previsão Amanhã',
        mode='markers',
        marker=dict(color='green', size=10, symbol='star'),
        hoverinfo='text',
        text=f'Previsão: {predicted_next:.2f}'
    ))

    fig.update_layout(
        title=f'Previsão de Preços - {ticker}',
        xaxis_title='Data',
        yaxis_title='Preço (USD)',
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    fig.add_vline(
        x=last_date,
        line_width=1,
        line_dash="dash",
        line_color="grey"
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def direction_accuracy(y_true, y_pred):
    y_true_diff = np.diff(y_true.flatten())
    y_pred_diff = np.diff(y_pred.flatten())
    correct = np.sum((y_true_diff > 0) == (y_pred_diff > 0))
    return correct / (len(y_true_diff) - 1) if len(y_true_diff) > 1 else 0.0


def executar_previsao(nome_commodity, df_commodities, exibir_log=True):
    torch.cuda.empty_cache()
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        data = obter_dados(nome_commodity, df_commodities)
        X, y, scaler = preprocessar_dados(data)

        train_size = int(len(X) * 0.7)
        val_size = int(len(X) * 0.15)
        X_train, X_val, X_test = X[:train_size], X[train_size:train_size +
                                                   val_size], X[train_size+val_size:]
        y_train, y_val, y_test = y[:train_size], y[train_size:train_size +
                                                   val_size], y[train_size+val_size:]

        X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
        y_train_tensor = torch.tensor(
            y_train, dtype=torch.float32).unsqueeze(-1)
        X_val_tensor = torch.tensor(X_val, dtype=torch.float32)
        y_val_tensor = torch.tensor(y_val, dtype=torch.float32).unsqueeze(-1)
        X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
        y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(-1)

        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

        model = LSTMModel(input_size=X.shape[2], hidden_size=128,
                          num_layers=2, output_size=1, dropout=0.2).to(device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.0003)
        scheduler = optim.lr_scheduler.StepLR(
            optimizer, step_size=10, gamma=0.8)

        epochs = 25
        best_val_loss = float('inf')
        patience, trigger = 7, 0
        best_model = None

        for epoch in range(epochs):
            model.train()
            epoch_loss = 0
            for xb, yb in train_loader:
                xb, yb = xb.to(device), yb.to(device)
                optimizer.zero_grad()
                out = model(xb)
                loss = criterion(out, yb)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            scheduler.step()
            model.eval()
            with torch.no_grad():
                val_out = model(X_val_tensor.to(device)).cpu().numpy()
                val_loss = mean_squared_error(y_val, val_out)
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                trigger = 0
                best_model = model.state_dict()
            else:
                trigger += 1
                if trigger >= patience:
                    break
            if exibir_log and epoch % 5 == 0:
                print(
                    f"Epoch {epoch}, Train Loss: {epoch_loss/len(train_loader):.4f}, Val Loss: {val_loss:.4f}")

        model.load_state_dict(best_model)
        model.eval()
        with torch.no_grad():
            predicted_prices = model(X_test_tensor.to(device)).cpu().numpy()
            mse = mean_squared_error(y_test, predicted_prices)
            rmse = np.sqrt(mse)
            dir_acc = direction_accuracy(y_test, predicted_prices)

            last_sequence = torch.tensor(
                X[-1].reshape(1, X.shape[1], X.shape[2]), dtype=torch.float32).to(device)
            predicted_next_scaled = model(last_sequence).cpu().numpy()

            zeros_shape = (1, X.shape[2] - 1) if X.shape[2] > 1 else (1, 0)
            if zeros_shape[1] > 0:
                predicted_next = scaler.inverse_transform(
                    np.concatenate(
                        [predicted_next_scaled, np.zeros(zeros_shape)], axis=1)
                )[0][0]
            else:
                predicted_next = scaler.inverse_transform(
                    predicted_next_scaled)[0][0]

        preco_atual = float(data.iloc[-1, 1])
        print(
            f"[DEBUG] {nome_commodity} - Preço atual: {preco_atual:.2f}, Previsão: {predicted_next:.2f}")

        grafico_html = plot_predictions(
            y_test, 
            predicted_prices,
            scaler, 
            data, 
            nome_commodity, 
            predicted_next
        )

        return {
            "preco_atual": preco_atual,
            "previsao_amanha": predicted_next,
            "rmse": rmse,
            "acuracia": dir_acc,
            "grafico_html": grafico_html,  
            "y_test": y_test,
            "predicted_prices": predicted_prices,
            "scaler": scaler,
            "data": data
        }


    except Exception as e:
        raise RuntimeError(f"Erro: {e}")


if __name__ == '__main__':
    try:
        df_commodities = carregar_dados_csv()
    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        sys.exit(1)

    nome_commodity = 'Milho'
    try:
        resultado = executar_previsao(nome_commodity, df_commodities)
        print(f"Previsão para {nome_commodity}:")
        print(f"Preço Atual: {resultado['preco_atual']:.2f}")
        print(f"Previsão para Amanhã: {resultado['previsao_amanha']:.2f}")
        print(f"RMSE: {resultado['rmse']:.4f}")
        print(f"Acurácia da Direção: {resultado['acuracia']:.2%}")
    except RuntimeError as e:
        print(f"Erro ao executar a previsão: {e}")
