### MDP Value Iteration and Policy Iteration
import argparse
import numpy as np
import gym
import time
from lake_envs import *

np.set_printoptions(precision=3)

parser = argparse.ArgumentParser(description='A program to run assignment 1 implementations.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("--env",
                    help="The name of the environment to run your algorithm on.", 
                    choices=["Deterministic-4x4-FrozenLake-v0","Stochastic-4x4-FrozenLake-v0"],
                    default="Deterministic-4x4-FrozenLake-v0")

"""
For policy_evaluation, policy_improvement, policy_iteration and value_iteration,
the parameters P, nS, nA, gamma are defined as follows:

    P: nested dictionary
        From gym.core.Environment
        For each pair of states in [1, nS] and actions in [1, nA], P[state][action] is a
        tuple of the form (probability, nextstate, reward, terminal) where
            - probability: float
                the probability of transitioning from "state" to "nextstate" with "action"
            - nextstate: int
                denotes the state we transition to (in range [0, nS - 1])
            - reward: int
                either 0 or 1, the reward for transitioning from "state" to
                "nextstate" with "action"
            - terminal: bool
              True when "nextstate" is a terminal state (hole or goal), False otherwise
    nS: int
        number of states in the environment
    nA: int
        number of actions in the environment
    gamma: float
        Discount factor. Number in range [0, 1)
"""


def policy_evaluation(P, nS, nA, policy, gamma=0.9, tol=1e-3):
    """Evaluate the value function from a given policy.

    Parameters
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    policy: np.array[nS]
        The policy to evaluate. Maps states to actions.
    tol: float
        Terminate policy evaluation when
            max |value_function(s) - prev_value_function(s)| < tol
    Returns
    -------
    value_function: np.ndarray[nS]
        The value function of the given policy, where value_function[s] is
        the value of state s
    """

    value_function = np.zeros(nS)

    ############################
    # YOUR IMPLEMENTATION HERE #

    def B_pi(value_function):
        V_new = np.zeros(shape=value_function.shape)
        for state in range(nS):
            V_new[state] = 0
            action = policy[state]
            for probability, nextstate, reward, terminal in P[state][action]:
                V_new[state] += probability*(reward + gamma*value_function[nextstate])
        return V_new

    V_current = value_function
    V_next = None
    gap = tol + 1
    i = 0
    while gap >= tol:
        i += 1
        V_next = B_pi(V_current)
        gap = np.max(np.abs(V_next - V_current))
        V_current = V_next

    value_function = V_next
    ############################
    return value_function


def policy_improvement(P, nS, nA, value_from_policy, policy, gamma=0.9):
    """Given the value function from policy improve the policy.

    Parameters
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    value_from_policy: np.ndarray
        The value calculated from the policy
    policy: np.array
        The previous policy.

    Returns
    -------
    new_policy: np.ndarray[nS]
        An array of integers. Each integer is the optimal action to take
        in that state according to the environment dynamics and the
        given value function.
    """

    new_policy = np.zeros(nS, dtype='int')

    ############################
    # YOUR IMPLEMENTATION HERE #
    for state in range(nS):
        action_values = np.zeros(nA)
        for action in range(nA):
            for probability, nextstate, reward, terminal in P[state][action]:
                action_values[action] += probability*(reward + gamma*value_from_policy[nextstate])
        new_policy[state] = np.argmax(action_values)

    ############################
    return new_policy


def policy_iteration(P, nS, nA, gamma=0.9, tol=10e-3):
    """Runs policy iteration.

    You should call the policy_evaluation() and policy_improvement() methods to
    implement this method.

    Parameters
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    tol: float
        tol parameter used in policy_evaluation()
    Returns:
    ----------
    value_function: np.ndarray[nS]
    policy: np.ndarray[nS]
    """

    value_function = np.zeros(nS)
    policy = np.zeros(nS, dtype=int)

    ############################
    # YOUR IMPLEMENTATION HERE #

    value_from_policy_prev = policy_evaluation(P, nS, nA, policy, gamma, tol)
    gap = tol + 1
    while gap >= tol:
        policy = policy_improvement(P, nS, nA, value_from_policy_prev, policy, gamma)
        value_from_policy = policy_evaluation(P, nS, nA, policy, gamma, tol)
        gap = np.max(np.abs(value_from_policy - value_from_policy_prev))
        # print('New policy: ', policy)

        value_from_policy_prev = value_from_policy

    value_function = value_from_policy

    print('Resulting policy:', policy)
    print('\tValue function = ', value_function)

    ############################
    return value_function, policy


def value_iteration(P, nS, nA, gamma=0.9, tol=1e-3):
    """
    Learn value function and policy by using value iteration method for a given
    gamma and environment.

    Parameters:
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    tol: float
        Terminate value iteration when
            max |value_function(s) - prev_value_function(s)| < tol
    Returns:
    ----------
    value_function: np.ndarray[nS]
    policy: np.ndarray[nS]
    """

    value_function = np.zeros(nS)
    policy = np.zeros(nS, dtype=int)
    ############################
    # YOUR IMPLEMENTATION HERE #

    def backup(value_function):
        value_function_new = np.zeros(len(value_function))
        for state in range(nS):
            action_values = np.zeros(nA)
            for action in range(nA):
                for probability, nextstate, reward, terminal in P[state][action]:
                    action_values[action] += probability*(reward + gamma*value_function[nextstate])
            value_function_new[state] = np.max(action_values)
            policy[state] = np.argmax(action_values)
        return value_function_new, policy

    gap = tol + 1
    prev_value_function = value_function
    while gap >= tol:
        value_function, policy = backup(prev_value_function)
        gap = np.max(np.abs(value_function - prev_value_function))
        prev_value_function = value_function

    print('Resulting value function = ', value_function)
    print('\tCorrespondent greedy policy:', policy)

    ############################s
    return value_function, policy

def render_single(env, policy, max_steps=100):
  """
    This function does not need to be modified
    Renders policy once on environment. Watch your agent play!

    Parameters
    ----------
    env: gym.core.Environment
      Environment to play on. Must have nS, nA, and P as
      attributes.
    Policy: np.array of shape [env.nS]
      The action to take at a given state
  """

  episode_reward = 0
  ob = env.reset()
  for t in range(max_steps):
    env.render()
    time.sleep(0.25)
    a = policy[ob]
    ob, rew, done, _ = env.step(a)    
    episode_reward += rew
    if done:
      break
  env.render();
  if not done:
    print("The agent didn't reach a terminal state in {} steps.".format(max_steps))
  else:
      print("Episode reward: %f" % episode_reward)


# Edit below to run policy and value iteration on different environments and
# visualize the resulting policies in action!
# You may change the parameters in the functions below
if __name__ == "__main__":
    # read in script argument
    args = parser.parse_args()

    # Make gym environment
    env = gym.make(args.env)
    import json
    with open('P_dynamics.txt', 'a') as f:
        json.dump(env.P, f, indent=4)

    print("\n" + "-"*25 + "\nBeginning Policy Iteration\n" + "-"*25)

    V_pi, p_pi = policy_iteration(env.P, env.nS, env.nA, gamma=0.9, tol=1e-3)
    render_single(env, p_pi, 100)

    print("\n" + "-"*25 + "\nBeginning Value Iteration\n" + "-"*25)

    V_vi, p_vi = value_iteration(env.P, env.nS, env.nA, gamma=0.9, tol=1e-3)
    render_single(env, p_vi, 100)


# #### Deterministic variant:

# In the first run, with deterministic dynamics, we managed to reach the optimal policy [1 2 1 0 1 0 1 0 2 1 1 0 0 2 2 0]
# with both policy iteration and value iteration procedures. Resulting Value functions also were equal:
# [0.59  0.656 0.729 0.656 0.656 0.    0.81  0.    0.729 0.81  0.9   0.     0.    0.9   1.    0.   ]

# #### Stochastic variant:

# *Policy iteration
# Resulting policy: [0 3 0 3 0 0 0 0 3 1 0 0 0 2 1 0]
#           Value function =  [0.062 0.056 0.07  0.051 0.086 0.    0.11  0.    0.141 0.244 0.297 0.     0.    0.377 0.638 0.   ]
# *Value iteration:
# Resulting value function =  [0.063 0.056 0.071 0.052 0.086 0.    0.11  0.    0.141 0.244 0.297 0.     0.    0.378 0.638 0.   ]
# 		Correspondent greedy policy: [0 3 0 3 0 0 0 0 3 1 0 0 0 2 1 0]
# We see that values of the states now are much less, then in deterministic situation. It's because with stochastic dynamics,
# there are chances, that we didn't get the reward at all, or reward will be received with a great discount, because the way to reward was long. 