# Tektronix-Python-Wrapper
Wrapper class for easy control of a Tektronix oscilloscope on a Linux Machine using usbtmc driver. This uses the newer version of the usbtmc driver included with the Linux kernel. There may be slight differences for older versions.

Retrieve a scope trace as easily as:

```
import scopeWrapper
sw = scopeWrapper.ScopeWrapper()
y = sw.getTrace('CH1')
x = sw.getTimeAxis()
```

After importing your choice of plotting library, you can then just
```
plot(x,y)
```
Currently only tested with Tektronix MDO4104B-3 on Linux Kernel 5.3.18. This should at least work with all MDO4100 series scopes.

Some scope communication programs have trouble obtaining more than 10,000 or 100,000 points from these scopes. This issue has been fixed in this program, and the solution appears to be in the initialization of the communication.
