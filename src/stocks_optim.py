import numpy as np
from scipy.optimize import minimize, dual_annealing
from scipy.stats import norm

from stocks import T, mu, sigma, beta, num_factors, num_stocks, S0, sigma_M


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
    riskless_return = 105.14 # actually rounds to $105.13
    target_value = 150

    def generate_stock_paths(n):
        dt = T / n
        t = np.linspace(0, T, n+1)
        M = np.array([np.cumsum(np.sqrt(dt) * sigma_M[i] *  np.random.randn(n)) for i in range(num_factors)])
        M = np.insert(M, 0, 0, axis=1)  # M(0) = 0
        
        stock_paths = []
        
        for i in range(num_stocks):
            W = np.cumsum(np.sqrt(dt) * np.random.randn(n))  # Idiosyncratic Wiener process
            W = np.insert(W, 0, 0)  # Insert W(0) = 0
            S = S0[i] * np.exp((mu[i] - 0.5 * sigma[i]**2) * t + sigma[i] * W + np.sum(beta[:, i].reshape(-1, 1) * M, axis=0))
            stock_paths.append(S)
        
        return np.array(stock_paths)
    
    def empirical_prob(weights, n_tries=100, big_n=False):
        simulations = np.array([np.dot(weights, generate_stock_paths(n = (500 if big_n else 10)))[-1] for _ in range(n_tries)])
        prob = np.mean(simulations > target_value)
        return prob
    
    def portfolio_stats(weights):
        mu_p = np.sum(weights * mu)
        sigma_p2 = np.dot(weights.T, np.dot(stock_cov_matrix, weights))
        return mu_p, sigma_p2

    def objective(weights):
        # mu_p, sigma_p2 = portfolio_stats(weights)
        # print(mu_p, sigma_p2)
        # sigma_p = np.sqrt(sigma_p2)
        # V_0 = 1  # Initial portfolio value (assuming 1 for simplicity)
        # Z = (target_value - V_0 * np.exp(mu_p)) / (V_0 * sigma_p * np.exp(mu_p))
        # prob = 1 - norm.cdf(Z)
        penalty = 0
        if np.sum(weights) > 1:
            penalty = 1e6 * (np.sum(weights) - 1)**2  # Large penalty for violating the constraint

        return penalty - empirical_prob(weights, n_tries=5)
    
    # constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # Weights sum to 1
    bounds = tuple((0, 1) for _ in range(num_stocks))  # Weights are between 0 to 1
    weights = [0., 0., 0., 0., 1., 0., 0.]
    # result = dual_annealing(objective, bounds)
    # weights = result.x

    print(f'pre-norm sum: {np.sum(weights)}')
    weights /= np.sum(weights)

    print(f"max-E weights: {' '.join(f'{100*weight:.1f}%' for weight in weights)}")
    print(f"Var[portfolio] = {portfolio_variance(weights):.4f}")
    print(f"E[portfolio] = {-portfolio_negative_expectation(weights)-100:.1f}%")
    # print(f"P[V_t > {target_value}] (theoretical) = {-objective(weights)}")
    print(f"P[V_t > {target_value}] (empirical)   = {empirical_prob(weights, n_tries=1000, big_n=True)}")

if __name__ == '__main__':
    max_e_for_var()

# portfolio = minimize(portfolio_variance, portfolio, method='SLSQP', bounds=bounds, constraints=constraints)
# min_variance_weights = portfolio.x
# effective_volatility = np.sqrt(portfolio_variance(min_variance_weights))

# print(f"Minimum Variance Portfolio Weights: {min_variance_weights}")
# print(f"Effective Volatility of Minimum Variance Portfolio: {effective_volatility}")

# expected_values = S0 * np.exp(mu * T)
# effective_expected_value = np.sum(min_variance_weights * expected_values)
# print(f"E[portfolio] = {effective_expected_value}")
