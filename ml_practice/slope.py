from statistics import mean
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import random

style.use('ggplot')

def create_dataset(hm, variance, step=2, correlation=False):
    val = 0
    noise = 0
    ys = []
    for i in range(hm):
        if variance:
            noise = random.randrange(-variance, variance)
        y = val + noise
        ys.append(y)
        if correlation and correlation == 'pos':
            val += step
        elif correlation and correlation == 'neg':
            val -= step
    xs = [i for i in range(len(ys))]
    return np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)

def best_fit_slope_and_intercept(xs, ys):
    m = ( ((mean(xs)*mean(ys)) - mean(xs*ys)) /
          ((mean(xs)**2) - mean(xs**2)) )
    b = mean(ys) - m*mean(xs)
    return m, b

def squared_error(ys_orig, ys_line):
    return sum((ys_line-ys_orig)**2)

def coefficient_of_determination(ys_orig, ys_line):
    ys_mean_line = [mean(ys_orig) for y in ys_orig]
    squared_error_regr = squared_error(ys_orig, ys_line)
    squared_error_y_mean = squared_error(ys_orig, ys_mean_line)
    return 1 - (squared_error_regr / squared_error_y_mean)

model_slope = 0.5
sims = {}
for n_points in [3,4,5]:
    slopes, r_squareds = [], []
    for i in range(5000):
        xs, ys = create_dataset(n_points, 4, model_slope, correlation='pos')
        m, b = best_fit_slope_and_intercept(xs, ys)
        regression_line = [(m*x)+b for x in xs]
        r_squared = coefficient_of_determination(ys, regression_line)
        slopes.append(m)
        r_squareds.append(r_squared)

    sims[n_points] = [slopes, r_squareds]

for idx, plot in enumerate(sims):
    plt.subplot(1,len(sims),idx+1)
    plt.hist(np.array(sims[plot][0])-model_slope, bins=np.arange(-5, 5, 0.5))
plt.show()
