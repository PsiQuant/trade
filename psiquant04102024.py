#let's begin with the importation of docu needed to do the work

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
import yfinance as yf


#apple's stock data

stock = yf.Ticker("AAPL")
data = stock.history(period="1y")
print(data.head())

# Calculation of momentum

data['momentum'] = data['Close'].pct_change()
#ou bien on peut encore améliorer
# Calcul du momentum avec une fenêtre glissante
window_size = 20
#Une fenêtre glissante permet de capturer mieux les mouvements de tendance.
data['momentum'] = data['Close'].pct_change(window_size)

# Creating subplots to show momentum and buying/selling markers
#Par défaut, elle calcule la différence relative entre chaque élément et celui qui le précède.
#Pour les DataFrames, vous pouvez ajouter facilement une nouvelle colonne contenant les changements en pourcentage :
# using df['FR_pct_change'] = df['FR'].pct_change()
#tu obtiens une mesure plus robuste qui prend en compte les mouvements à moyen terme, plutôt qu'une simple comparaison entre deux jours consécutifs.
#La fenêtre de 20 jours est souvent choisie parce qu'elle représente environ un mois de trading

figure = make_subplots(rows=2, cols=1)
#Cette ligne crée un objet Figure contenant deux sous-plots alignés horizontalement.

figure.add_trace(go.Scatter(x=data.index,
                         y=data['Close'],
                         name='Close Price'))
#Cette ligne ajoute une trace de type Scatter au sous-plot
figure.add_trace(go.Scatter(x=data.index,
                         y=data['momentum'],
                         name='Momentum',
                         yaxis='y2'))
# Adding the buy and sell signals
figure.add_trace(go.Scatter(x=data.loc[data['momentum'] > 0].index,
                         y=data.loc[data['momentum'] > 0]['Close'],
                         mode='markers', name='Buy',
                         marker=dict(color='green', symbol='triangle-up')))

figure.add_trace(go.Scatter(x=data.loc[data['momentum'] < 0].index,
                         y=data.loc[data['momentum'] < 0]['Close'],
                         mode='markers', name='Sell',
                         marker=dict(color='red', symbol='triangle-down')))

figure.update_layout(title='Algorithmic Trading using Momentum Strategy',
                  xaxis_title='Date',
                  yaxis_title='Price')
figure.update_yaxes(title="Momentum", secondary_y=True)
#figure.show()

figure.write_html("mon_graphique1.html")

#Calcul de la moyenne mobile simple sur 20 jours
window_size = 20
data['SMA'] = data['Close'].rolling(window=window_size).mean()
# Ajout des signaux d'achat et de vente basés sur la SMA :
# Signaux d'achat et de vente basés sur la SMA
data['buy_signal'] = data['Close'] > data['SMA']  # Achat lorsque le prix dépasse la SMA
data['sell_signal'] = data['Close'] < data['SMA']  # Vente lorsque le prix descend sous la SMA

# Ajout des signaux sur le graphique
figure.add_trace(go.Scatter(x=data.loc[data['buy_signal']].index,
                            y=data.loc[data['buy_signal']]['Close'],
                            mode='markers', name='Buy (SMA)',
                            marker=dict(color='green', symbol='triangle-up')))

figure.add_trace(go.Scatter(x=data.loc[data['sell_signal']].index,
                            y=data.loc[data['sell_signal']]['Close'],
                            mode='markers', name='Sell (SMA)',
                            marker=dict(color='red', symbol='triangle-down')))
# Ajout de la courbe de la moyenne mobile simple (SMA)
figure.add_trace(go.Scatter(x=data.index, y=data['SMA'],
                            name='SMA', line=dict(color='blue', width=2)))
figure.update_layout(title='Algorithmic Trading using SMA Strategy',
                     xaxis_title='Date',
                     yaxis_title='Price')
#lorsque le prix de clôture dépasse la SMA est basée sur l'interprétation que cela peut signaler un changement de tendance haussière

figure.write_html("mon_graphique_SMA.html")

################################################
###############################################
initial_balance = 10000  # Starting with $10,000
balance = initial_balance
position = 0  # No position initially

# List to store the portfolio value over time
portfolio_values = []

for i in range(1, len(data)):
    if data['buy_signal'].iloc[i] and position == 0:  # Buy signal and no current position
        position = balance / data['Close'].iloc[i]  # Buy stock with entire balance
        balance = 0  # Use all cash to buy

    elif data['sell_signal'].iloc[i] and position > 0:  # Sell signal and position held
        balance = position * data['Close'].iloc[i]  # Sell stock
        position = 0  # Close position

    # Calculate portfolio value
    portfolio_value = balance + position * data['Close'].iloc[i]
    portfolio_values.append(portfolio_value)

data['Portfolio Value'] = portfolio_values


