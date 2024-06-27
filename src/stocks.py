import numpy as np
import matplotlib.pyplot as plt


# Parameters
T = 1.0  # total time (e.g., 1 year)
stock_names = ['BIGCORP A', 'B INC.', 'C', 'TECHCORP', 'TECHSTART', 'SHORTS EMPORIUM', '$$$']
mu = np.array(
    [0.103, 0.1, 0.105, 0.11, 0.07, -0.03, 0.05]
)  # expected returns for each stock
sigma = np.array(
    [0.1, 0.125, 0.15,  0.15,  0.3,  0.1, 1e-9]
)  # volatilities for each stock
beta = np.array([
    [1.0,  0.9,  1.2,  0.8,  0.2, -1.8, 1e-9],
    [0.0, -0.1,  0.1,  0.5,  1.0, -1.2, 1e-9],
    [0.1,  0.0,  0.2,  0.4, -1.0, -0.4, 0.0]
])  # market factor sensitivities
num_factors, num_stocks = beta.shape
S0 = np.array([100, 100, 100, 100, 100, 100, 100])  # initial stock prices
sigma_M = np.array([0.1,
                    0.2,
                    0.3
                    ])  # volatilities of the market factors

N = 500  # number of time steps
num_samples = 10  # number of samples

if __name__ == '__main__':
    # Time step
    dt = T / N

    # Time array
    t = np.linspace(0, T, N+1)

    # Function to generate multiple stock paths influenced by common market factor
    def generate_stock_paths():
        # Generate common market factors
        M = np.array([np.cumsum(np.sqrt(dt) * sigma_M[i] *  np.random.randn(N)) for i in range(num_factors)])
        M = np.insert(M, 0, 0, axis=1)  # M(0) = 0
        
        stock_paths = []
        
        for i in range(num_stocks):
            W = np.cumsum(np.sqrt(dt) * np.random.randn(N))  # Idiosyncratic Wiener process
            W = np.insert(W, 0, 0)  # Insert W(0) = 0
            S = S0[i] * np.exp((mu[i] - 0.5 * sigma[i]**2) * t + sigma[i] * W + np.sum(beta[:, i].reshape(-1, 1) * M, axis=0))
            stock_paths.append(S)
        
        return np.array(stock_paths)

    samples = np.array([generate_stock_paths() for _ in range(num_samples)])

    strategies = {
        'riskfree': [0., 0., 0., 0., 0., 0., 1.], # min variance
        'safe    ': [0.015, 0.01, 0.006, 0.008, 0.002, 0.005, 0.953], # low variance (1e-5)
        'balanced': [0.377, 0.279, 0.091, 0.194, 0.022, 0.036, 0.], # med variance (0.01)
        'C_tech  ': [0., 0., 0.05, 0.95, 0., 0., 0.],  # high variance (0.05)
        'max_E   ': [0., 0., 0., 1., 0., 0., 0.] # max expectation
    }


    for strat_name, strat_weights in strategies.items():
        end_vals = [np.dot(strat_weights, stock_paths)[-1] for stock_paths in samples]
        print(f'{strat_name} payoffs: \t' + '\t'.join(f'${end_val:.2f}' for end_val in end_vals))

    for j in range(num_samples):

        # Plotting
        plt.figure(figsize=(14, 8))
        ax = plt.gca()
        ax.set_facecolor('black')  # Set plot background to black
        fig = plt.gcf()
        fig.patch.set_facecolor('black')  # Set figure background to black

        for i in range(num_stocks):
            plt.plot(t, samples[j][i], label=stock_names[i], alpha=0.8, linewidth=1.5)

        plt.title('GBM simulation with common market factors', color='white')
        plt.xlabel('Time (t)', color='white')
        plt.ylabel('Stock Price', color='white')
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
        plt.grid(True, color='gray')
        ax.tick_params(colors='white')  # Change tick color to white
        
        plt.show()

    # weights = np.ones(num_stocks) / num_stocks  # equal weights for simplicity

    # # Expected values
    # expected_values = S0 * np.exp(mu * T)

    # # Effective expected value
    # effective_expected_value = np.sum(weights * expected_values)

    # # Covariance matrix
    # cov_matrix = np.zeros((num_stocks, num_stocks))
  
    # for i in range(num_stocks):
    #     for j in range(num_stocks):
    #         if i == j:
    #             cov_matrix[i, j] = sigma[i]**2 * S0[i]**2 * np.exp(2 * mu[i] * T)
    #         else:
    #             cov_matrix[i, j] = S0[i] * S0[j] * np.exp((mu[i] + mu[j]) * T) * np.sum(beta[:, i] * beta[:, j] * sigma_M**2 * T)

    # # Effective volatility
    # portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
    # effective_volatility = np.sqrt(portfolio_variance)

    # print(f"Effective Expected Value: {effective_expected_value}")
    # print(f"Effective Volatility: {effective_volatility}")


