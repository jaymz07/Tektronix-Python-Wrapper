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
