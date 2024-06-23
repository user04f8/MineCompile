import numpy as np
from scipy.optimize import minimize

from stocks import T, N, mu, sigma, beta, num_factors, num_stocks, S0, sigma_M


factor_cov_matrix = np.diag(sigma_M ** 2)
stock_cov_matrix = np.zeros((num_stocks, num_stocks))

for i in range(num_stocks):
    for j in range(num_stocks):
        market_cov = beta[:, i] @ factor_cov_matrix @ beta[:, j]
        if i == j:
            stock_cov_matrix[i, j] = sigma[i] ** 2 + market_cov
        else:
            stock_cov_matrix[i, j] = market_cov


# Check if the covariance matrix is positive semi-definite
def is_positive_semi_definite(matrix):
    try:
        np.linalg.cholesky(matrix)
        return True
    except np.linalg.LinAlgError:
        return False

if not is_positive_semi_definite(stock_cov_matrix):
    raise ValueError("Covariance matrix is not positive semi-definite. Check the input parameters.")

def portfolio_variance(weights):
    return np.dot(weights.T, np.dot(stock_cov_matrix, weights))


expected_values = S0 * np.exp(mu * T)
def portfolio_negative_expectation(weights):
    return -np.sum(weights * expected_values)

def max_e_for_var():

    max_vars = [1e-6, 1e-5, 1e-4, 1e-3, 0.01, 0.02, 0.03, 0.04, 0.05, 1.0]

    for max_var in max_vars:

        # Constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1}, {'type': 'ineq', 'fun': lambda x: max_var - portfolio_variance(x)})  # Weights sum to 1
        bounds = tuple((0, 1) for _ in range(num_stocks))  # Weights between 0 and 1

        portfolio = np.ones(num_stocks) / num_stocks

        portfolio = minimize(portfolio_negative_expectation, portfolio, method='SLSQP', bounds=bounds, constraints=constraints)
        weights = portfolio.x

        print(f"max-E weights for var {max_var}: {' '.join(f'{100*weight:.1f}%' for weight in weights)}")
        print(f"Var[portfolio] = {portfolio_variance(weights):.4f}")
        print(f"E[portfolio] = {-portfolio_negative_expectation(weights)-100:.1f}%")

def max_p_greater_than():
    target_value = riskless_return = 105.14 # actually rounds to $105.13

    def generate_simulations(weights, num_simulations=100):
        portfolio_returns = np.zeros(num_simulations)
        for _ in range(num_simulations):
            M = np.random.multivariate_normal(np.zeros(num_factors), factor_cov_matrix, T * num_stocks)
            W = np.random.multivariate_normal(np.zeros(num_stocks), stock_cov_matrix, T * num_stocks)
            total_returns = np.sum(weights * (mu * T + np.dot(beta.T, M.T).T + W), axis=1)
            portfolio_returns += total_returns
        portfolio_end_values = S0 @ weights * np.exp(portfolio_returns)
        return portfolio_end_values

    def objective(weights):
        simulations = generate_simulations(weights)
        prob = np.mean(simulations > target_value)
        return -prob
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # Weights sum to 1
    bounds = tuple((0, 1) for _ in range(num_stocks))  # Weights between 0 and 1
    initial_guess = np.ones(num_stocks) / num_stocks
    result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    weights = result.x

    optimal_simulations = generate_simulations(weights)
    optimal_probability = np.mean(optimal_simulations > target_value)

    print(f"max-E weights: {' '.join(f'{100*weight:.1f}%' for weight in weights)}")
    print(f"Var[portfolio] = {portfolio_variance(weights):.4f}")
    print(f"E[portfolio] = {-portfolio_negative_expectation(weights)-100:.1f}%")
    print(f"P[V_t > {target_value}] = {optimal_probability}")

if __name__ == '__main__':
    max_p_greater_than()

# portfolio = minimize(portfolio_variance, portfolio, method='SLSQP', bounds=bounds, constraints=constraints)
# min_variance_weights = portfolio.x
# effective_volatility = np.sqrt(portfolio_variance(min_variance_weights))

# print(f"Minimum Variance Portfolio Weights: {min_variance_weights}")
# print(f"Effective Volatility of Minimum Variance Portfolio: {effective_volatility}")

# expected_values = S0 * np.exp(mu * T)
# effective_expected_value = np.sum(min_variance_weights * expected_values)
# print(f"E[portfolio] = {effective_expected_value}")
