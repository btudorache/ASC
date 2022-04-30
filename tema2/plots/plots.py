import matplotlib.pyplot as plt

dimensions = [200, 400, 600, 800, 1000, 1200, 1400]
blas_times = [0.053, 0.039, 0.110, 0.221, 0.401, 0.672, 1.034]
neopt_times = [0.081, 0.692, 2.485, 8.829, 15.843, 41.835, 65.353]
opt_m_times = [0.045, 0.323, 1.079, 2.618, 5.279, 9.237, 14.089]

fig, ax = plt.subplots()
ax.plot(dimensions, blas_times)
ax.set(xlabel='dimension N (matrix side)', ylabel='time (s)',
       title='Blas running time')
ax.grid()
fig.savefig("blas.png")
plt.show()

fig, ax = plt.subplots()
ax.plot(dimensions, neopt_times)
ax.set(xlabel='dimension N (matrix side)', ylabel='time (s)',
       title='Neopt running time')
ax.grid()
fig.savefig("neopt.png")
plt.show()

fig, ax = plt.subplots()
ax.plot(dimensions, opt_m_times)
ax.set(xlabel='dimension N (matrix side)', ylabel='time (s)',
       title='Opt_m running time')
ax.grid()
fig.savefig("opt_m.png")
plt.show()

fig, ax = plt.subplots()
ax.plot(dimensions, blas_times, label='blas')
ax.plot(dimensions, neopt_times, label='neopt')
ax.plot(dimensions, opt_m_times, label='opt_m')
ax.set(xlabel='dimension N (matrix side)', ylabel='time (s)',
       title='All running times')
plt.legend(loc='upper center')
ax.grid()
fig.savefig("all.png")
plt.show()
