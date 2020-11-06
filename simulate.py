# Movie Theatre Simulation
# Goal -- Average customer wait time: 10 mins or less

import simpy
import random
import statistics

wait_times = []

class Theatre:
    def __init__(self, env, num_cashiers, num_servers, num_ushers):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)
        self.server = simpy.Resource(env, num_servers)
        self.usher = simpy.Resource(env, num_ushers)

    def purchase_ticket(self, moviegoer):
        yield self.env.timeout(random.randint(1,3))

    def check_ticket(self, moviegoer):
        yield self.env.timeout(3/60)

    def sell_food(self, moviegoer):
        yield self.env.timeout(random.randint(1,6))

def go_to_movies(env, moviegoer, theatre):
    # arrives at theatre
    arrival_time = env.now
    # buy ticket
    with theatre.cashier.request() as request:
        yield request
        yield env.process(theatre.purchase_ticket(moviegoer))

    # check ticket
    with theatre.usher.request() as request:
        yield request
        yield env.process(theatre.check_ticket(moviegoer))

    # buy food
    if random.choice([True, False]):
        with theatre.server.request() as request:
            yield request
            yield env.process(theatre.sell_food(moviegoer))

    # go to their seat
    wait_times.append(env.now - arrival_time)

def run_theatre(env, num_cashiers, num_servers, num_ushers):
    theatre = Theatre(env, num_cashiers, num_servers, num_ushers)

    for moviegoer in range(3):
        env.process(go_to_movies(env, moviegoer, theatre))

    while True:
        yield env.timeout(0.2)

        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theatre))

def calculate_wait_times(wait_times):
    average_wait = statistics.mean(wait_times)
    # print results
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)

def get_user_input():
    num_cashiers = input('Input # of cashiers working: ')
    num_servers = input('Input # of servers working: ')
    num_ushers = input('Input # of ushers working: ')

    params = [num_cashiers, num_servers, num_ushers]

    if all(str(i).isdigit() for i in params):
        params = [int(x) for x in params]
    else:
        print('Could not parse input. The simulation will use default values: \
        \n1 cashier, 1 server, 1 usher')
        params = [1,1,1]
    return params

def main(num_cashiers,num_servers,num_ushers):
    # Setup
    random.seed(42)
    # num_cashiers, num_servers, num_ushers = get_user_input()
    # Run the simulation
    env = simpy.Environment()
    env.process(run_theatre(env, num_cashiers,num_servers,num_ushers))
    env.run(until=90)

    # View results
    mins, secs = calculate_wait_times(wait_times)

    # print(f'Running simulation...\
    # \nThe average wait time is {mins} minutes and {secs} seconds.')

    return mins, secs

def find_optimized_solution(n_cashiers,n_servers,n_ushers):
    import pandas as pd
    df = pd.DataFrame(columns=['cashiers','servers','ushers','time'])
    print('Beginning simulations...')
    for c in range(1,n_cashiers):
        for s in range(1,n_servers):
            for u in range(1,n_ushers):
                mins, secs = main(c,s,u)
                time = mins + secs/60
                df = df.append({'cashiers':c,'servers':s,'ushers':u,'time':time},ignore_index=True)
    print('Simulations complete.')
    return df

if __name__ == '__main__':
    num_cashiers, num_servers, num_ushers = get_user_input()
    df = find_optimized_solution(num_cashiers,num_servers,num_ushers)
    print(df)